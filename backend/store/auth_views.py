import logging

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from .authentication import SignedTokenAuthentication, make_token

User = get_user_model()
logger = logging.getLogger(__name__)

PASSWORD_RESET_RESPONSE = {
    'detail': 'If an active account uses that email address, password reset instructions have been sent.'
}


class PasswordResetRateThrottle(AnonRateThrottle):
    scope = 'password_reset'


def password_reset_user(uid):
    try:
        user_id = force_str(urlsafe_base64_decode(uid))
        return User.objects.get(pk=user_id, is_active=True)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return None


def user_data(user):
    return {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'full_name': user.get_full_name(),
    }


class ProtectedAuthView(APIView):
    authentication_classes = [SignedTokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = (request.data.get('username') or '').strip()
        email = (request.data.get('email') or '').strip().lower()
        password = request.data.get('password') or ''
        if not username or not email or not password:
            return Response({'detail': 'All fields are required.'}, status=400)
        if User.objects.filter(username__iexact=username).exists():
            return Response({'detail': 'That username is already registered.'}, status=400)
        if User.objects.filter(email__iexact=email).exists():
            return Response({'detail': 'That email is already registered.'}, status=400)
        try:
            validate_password(password)
        except ValidationError as error:
            return Response({'detail': ' '.join(error.messages)}, status=400)
        user = User.objects.create_user(username=username, email=email, password=password)
        return Response({'token': make_token(user), 'user': user_data(user)}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        login_value = (request.data.get('username') or request.data.get('email') or '').strip()
        password = request.data.get('password') or ''

        if not login_value or not password:
            return Response({'detail': 'Username/email and password are required.'}, status=400)

        username = login_value

        # If user entered email, find the related username first
        if '@' in login_value:
            matched_user = User.objects.filter(email__iexact=login_value, is_active=True).order_by('pk').first()
            if matched_user:
                username = matched_user.username

        user = authenticate(username=username, password=password)

        if user is None:
            return Response({'detail': 'Invalid username/email or password.'}, status=400)

        return Response({'token': make_token(user), 'user': user_data(user)})
class LogoutView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        return Response(status=204)


class CurrentUserView(ProtectedAuthView):
    def get(self, request):
        return Response(user_data(request.user))


class ProfileView(ProtectedAuthView):
    def get(self, request):
        return Response(user_data(request.user))

    def patch(self, request):
        user = request.user
        first_name = (request.data.get('first_name', user.first_name) or '').strip()
        last_name = (request.data.get('last_name', user.last_name) or '').strip()
        email = (request.data.get('email', user.email) or '').strip().lower()
        if not email:
            return Response({'email': ['Email is required.']}, status=400)
        if User.objects.exclude(pk=user.pk).filter(email__iexact=email).exists():
            return Response({'email': ['That email is already used by another account.']}, status=400)
        user.first_name, user.last_name, user.email = first_name, last_name, email
        user.save(update_fields=['first_name', 'last_name', 'email'])
        return Response(user_data(user))


class PasswordChangeView(ProtectedAuthView):
    def post(self, request):
        user = request.user
        current = request.data.get('current_password') or ''
        new = request.data.get('new_password') or ''
        confirm = request.data.get('confirm_password') or ''
        if not user.check_password(current):
            return Response({'current_password': ['The current password is incorrect.']}, status=400)
        if new != confirm:
            return Response({'confirm_password': ['The new passwords do not match.']}, status=400)
        try:
            validate_password(new, user=user)
        except ValidationError as error:
            return Response({'new_password': error.messages}, status=400)
        user.set_password(new)
        user.save(update_fields=['password'])
        return Response({'detail': 'Password changed successfully.', 'token': make_token(user)})


class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [PasswordResetRateThrottle]

    def post(self, request):
        email = (request.data.get('email') or '').strip().lower()
        user = User.objects.filter(email__iexact=email, is_active=True).order_by('pk').first() if email else None

        if user and user.has_usable_password():
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_url = f"{settings.FRONTEND_URL.rstrip('/')}/reset-password?uid={uid}&token={token}"
            context = {
                'user': user,
                'reset_url': reset_url,
                'timeout_minutes': max(1, settings.PASSWORD_RESET_TIMEOUT // 60),
            }
            subject = 'Reset your NazRiy password'
            message = EmailMultiAlternatives(
                subject=subject,
                body=render_to_string('email/password_reset.txt', context),
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email],
            )
            message.attach_alternative(render_to_string('email/password_reset.html', context), 'text/html')
            try:
                message.send(fail_silently=False)
            except Exception:
                # Do not reveal whether an account exists or whether delivery failed.
                logger.exception('Password reset email delivery failed.')

        return Response(PASSWORD_RESET_RESPONSE)


class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    @staticmethod
    def valid_user(uid, token):
        user = password_reset_user(uid)
        return user if user and token and default_token_generator.check_token(user, token) else None

    def get(self, request):
        user = self.valid_user(request.query_params.get('uid', ''), request.query_params.get('token', ''))
        if not user:
            return Response({'valid': False, 'detail': 'This reset link is invalid or has expired.'}, status=400)
        return Response({'valid': True})

    def post(self, request):
        user = self.valid_user(request.data.get('uid', ''), request.data.get('token', ''))
        if not user:
            return Response({'detail': 'This reset link is invalid or has expired.'}, status=400)

        new_password = request.data.get('new_password') or ''
        confirm_password = request.data.get('confirm_password') or ''
        if new_password != confirm_password:
            return Response({'confirm_password': ['The new passwords do not match.']}, status=400)
        try:
            validate_password(new_password, user=user)
        except ValidationError as error:
            return Response({'new_password': error.messages}, status=400)

        user.set_password(new_password)
        user.save(update_fields=['password'])
        return Response({'detail': 'Your password has been reset successfully. You can now log in.'})

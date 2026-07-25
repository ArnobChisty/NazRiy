from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .authentication import SignedTokenAuthentication, make_token

User = get_user_model()


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
        user = authenticate(username=request.data.get('username'), password=request.data.get('password'))
        if user is None:
            return Response({'detail': 'Invalid username or password.'}, status=400)
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

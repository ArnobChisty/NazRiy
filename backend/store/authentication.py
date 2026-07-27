from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import signing
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

TOKEN_SALT = 'nazriy-auth-token'


def make_token(user):
    payload = {'user_id': user.pk, 'auth_hash': user.get_session_auth_hash()}
    return signing.dumps(payload, salt=TOKEN_SALT, compress=True)


class SignedTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        header = request.headers.get('Authorization', '')
        if not header.startswith('Token '):
            return None
        try:
            payload = signing.loads(
                header[6:], salt=TOKEN_SALT,
                max_age=int(getattr(settings, 'AUTH_TOKEN_MAX_AGE', 60 * 60 * 24 * 30)),
            )
            user = get_user_model().objects.get(pk=payload['user_id'], is_active=True)
            if payload.get('auth_hash') != user.get_session_auth_hash():
                raise AuthenticationFailed('Invalid or expired token.')
        except AuthenticationFailed:
            raise
        except (signing.BadSignature, signing.SignatureExpired, get_user_model().DoesNotExist, KeyError):
            raise AuthenticationFailed('Invalid or expired token.')
        return user, None

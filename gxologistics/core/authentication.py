
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from django.conf import settings

class CookieJWTAuthentication(JWTAuthentication):
    """
    Reads the access token from a cookie named 'access_token'.
    """

    def get_header(self, request):
        """
        Overridden to NOT look for the Authorization header,
        but read from cookies instead.
        """
        raw_token = request.COOKIES.get('access_token')
        if raw_token is None:
            return None
        return ('Bearer', raw_token)

    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = header[1]
        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token

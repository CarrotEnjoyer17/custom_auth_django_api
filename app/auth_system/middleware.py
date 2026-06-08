import jwt

from auth_system.models import Session
from auth_system.services import decode_access_token


class JWTAuthentificationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.auth_session = None

        authorization_header = request.headers.get("Authorization")

        if not authorization_header:
            return self.get_response(request)
        
        if not authorization_header.startswith("Bearer "):
            return self.get_response(request)
        
        token = authorization_header.removeprefix("Bearer ").strip()

        try:
            payload = decode_access_token(token)
        except jwt.PyJWTError:
            return self.get_response(request)
        
        session_id = payload.get("session_id")
        token_jti = payload.get("jti")
        user_id = payload.get("user_id")

        if not session_id or not token_jti or not user_id:
            return self.get_response(request)
        
        session = (
            Session.objects
            .select_related("user")
            .filter(
                id=session_id,
                token_jti=token_jti,
                user_id=user_id,
                is_active=True,
                user__is_active=True,
            ).first()
        )

        if session is None:
            return self.get_response(request)
        
        request.user = session.user
        request.auth_session = session

        return self.get_response(request)
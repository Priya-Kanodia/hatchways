import jwt

from messenger_backend.settings import SESSION_SECRET
from messenger_backend.models import app_user


class SimpleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        token = request.headers.get("x-access-token")

        if token:
            decoded= jwt.decode(token, SESSION_SECRET, algorithms=["HS256"])
            print(decoded)
            user = app_user.objects.filter(id=decoded['id'])
            print("VERIFIED**")
            if len(user)>0:
                request.user= user.first()

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response
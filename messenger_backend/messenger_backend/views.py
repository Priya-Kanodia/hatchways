import json

import jwt
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from django.core import serializers

from messenger_backend.models import app_user
from messenger_backend.settings import SESSION_SECRET
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class Login(APIView):
    def post(self,request):
        body = request.data
        if not body.get("username","") or not body.get("password",""):
            return JsonResponse({
                'error': "Username, password, and email required",
            }, status=400)
        user = app_user.objects.filter(username=body["username"])
        if not user.exists():
            return JsonResponse({
                "error": f'No user found for username: {body["username"]}',
            }, status=401)
        user = user.first()
        if not user.verify_password(body["password"]):
            return JsonResponse({
                "error": "Wrong username and/or password",
            }, status=401)
        token = jwt.encode({"id": user.id}, SESSION_SECRET, algorithm="HS256")
        # user.token = token
        user_json = serializers.serialize('json', [user,])
        user_dict = json.loads(user_json)
        user_res = user_dict[0]["fields"]
        user_res["token"] = token
        user_res["id"] = user.id
        return JsonResponse(user_res, status=200)

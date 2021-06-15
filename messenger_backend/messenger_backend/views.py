import json
import jwt
from django.http import JsonResponse
from rest_framework.views import APIView
from django.core import serializers
from django.db.models import Q
from django.db.models import Prefetch

from messenger_backend.models import app_user, Conversations, Message
from messenger_backend.settings import SESSION_SECRET
from messenger_backend.online_users import online_users

class Login(APIView):
    def post(self,request):
        # expects username and password in request.data
        body = request.data
        if not body.get("username","") or not body.get("password",""):
            return JsonResponse({
                'error': "Username and password required",
            }, status=400)
        user = app_user.objects.filter(username=body["username"])
        if not user.exists():
            print( 'error: No user found for username:', body["username"] )
            return JsonResponse({
                "error": f'No user found for username: {body["username"]}',
            }, status=401)
        user = user.first()
        if not user.verify_password(body["password"]):
            print( 'error: Wrong username and/or password' )
            return JsonResponse({
                "error": "Wrong username and/or password",
            }, status=401)
        token = jwt.encode({"id": user.id}, SESSION_SECRET, algorithm="HS256")
        # user.token = token
        user_json = serializers.serialize('json', [user,])
        user_dict = json.loads(user_json)
        user_res = user_dict[0]["fields"]
        user_res["token"] = token
        return JsonResponse(user_res, status=200)

class Register(APIView):
    def post(self,request):
        # expects {username, email, password} in request.data
        body=request.data
        if (not body.get("username","")) or (not body.get("password","")) or (not body.get("email","")):
            return JsonResponse({
                'error': "Username, password, and email required",
            }, status=400)
        if (len(body.get("password","")) < 6):
            return JsonResponse({
                'error': "Password must be at least 6 characters",
            }, status=400)
        user=app_user(username= body["username"], email=body['email'], password= body['password'])
        user.save()
        token = jwt.encode({"id": user.id}, SESSION_SECRET, algorithm="HS256")
        user_json = serializers.serialize('json', [user,])
        user_dict = json.loads(user_json)
        user_res = user_dict[0]["fields"]
        user_res["token"] = token
        return JsonResponse(user_res, status=200)

class LogOut(APIView):
    def delete(self,request):
        return JsonResponse(status=204)

class User(APIView):
    def get(self, request):
        body= request.user
        if body:
            return JsonResponse(body)
        else:
            return JsonResponse({})

class Conversation(APIView):
    ''' get all conversations for a user, include latest message text for preview, and all messages
    include other user model so we have info on username/profile pic (don't include current user info)
    TODO: for scalability, implement lazy loading'''

    def get(self,request):
        user = request.user
        if not user:
            return JsonResponse(status=401)
        user_id= user.id
        conversations= Conversations.objects.filter(Q(user1_id=user_id) | Q(user2_id=user_id)).values('id').prefetch_related(
            Prefetch('message',queryset= Message.objects.order_by('-created_at')),
            Prefetch('user1', queryset= app_user.objects.exclude(id=user_id)),
            Prefetch('user2', queryset= app_user.objects.exclude(id=user_id))
        )
        # conversations= Conversations.objects.raw("SELECT Conversations.id, Message.text, Message.sender_id, user1.id, user1.username, user1.photoUrl, user2.id, user2.username, user2.photoUrl from Conversations, Message, app_user as user1, app_user as user2 JOIN Message ON Message.conversation_id=Conversations.id WHERE (Conversations.user1_id=user_id OR Conversations.user2_id=user_id) AND (NOT(user1.id=user_id)) AND (NOT(user2.id=user_id)) ORDER BY Message.created_at DESC ")

    # expects {recipientId, text, conversationId } in body (conversationId will be null if no conversation exists yet)
    def post(self, request):
        user = request.user
        if not user:
            return JsonResponse(status=401)

        sender_id=user.id
        body= request.data
        # if we already know conversation id, we can save time and just add it to message and return
        if body.get('conversation_id'):
            message= Message(sender_id=sender_id, text=body['text'], conversation_id=body['conversation_id'])
            message.save()
            return JsonResponse((message,body['sender']))
        # if we don't have conversation id, find a conversation to make sure it doesn't already exist
        conversation=Conversations.find_conversation(sender_id,body['recipientId'])
        if len(conversation)==0:
            # create conversation
            conversation= Conversations(user1_id=sender_id , user2_id=body['recipientId'])
            conversation.save()
            if body['sender'].id in online_users:
                body['sender'].online= True
        else:
            conversation= conversation.first()
        message= Message(sender_id=sender_id, text=body['text'], conversation_id=conversation.id)
        message.save()
        return JsonResponse((message,body['sender']))
                
class Username(APIView):
    # find users by username
    def get(self,request):
        user = request.user
        if not user:
            return JsonResponse(status=401)
        username= request.GET['username']
        users= app_user.objects.get(username__contains=username).exclude(id=request.user.id)

        for i in len(users):
            user_json= json.dumps(users[i])
            # add online status to each user that is online
            if user_json.id in online_users:
                user_json.online= True 
            users[i]= user_json

        return JsonResponse(users)


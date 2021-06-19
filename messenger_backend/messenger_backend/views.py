import json
import jwt
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from django.core import serializers
from django.db.models import Q
from django.forms.models import model_to_dict

from messenger_backend.models import app_user, Conversations, Messages
from messenger_backend.settings import SESSION_SECRET
from messenger_backend.online_users import online_users

from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')

class Login(APIView):
    def post(self,request):
        # expects username and password in request.data
        try:
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
            user_dict = model_to_dict(user, fields=[field.name for field in user._meta.fields])
            user_dict["token"] = token
            return JsonResponse(user_dict, status=200)
        except:
            print('Error Occured')

class Register(APIView):
    def post(self,request):
        # expects {username, email, password} in request.data
        try:
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
            user_dict = model_to_dict(user, fields=[field.name for field in user._meta.fields])
            user_dict["token"] = token
            return JsonResponse(user_dict, status=200)
        except:
            print('Error Occured')

class LogOut(APIView):
    def delete(self,request):
        return JsonResponse({},status=204)

class User(APIView):
    def get(self, request):
        try:
            token = request.headers.get("x-access-token")
            if token:
                decoded = jwt.decode(token, SESSION_SECRET, algorithms=["HS256"])
                user = app_user.objects.filter(id=decoded['id']).values().first()
            if user:
                return JsonResponse(user)
            else:
                return JsonResponse({})
        except:
            print('Error Occured')

class Conversation(APIView):
    ''' get all conversations for a user, include latest message text for preview, and all messages
    include other user model so we have info on username/profile pic (don't include current user info)
    TODO: for scalability, implement lazy loading'''

    def get(self,request):
        try:
            token = request.headers.get("x-access-token")
            if token:
                    decoded= jwt.decode(token, SESSION_SECRET, algorithms=["HS256"])
                    user = app_user.objects.filter(id=decoded['id']).values().first()

            if not user:
                return JsonResponse(status=401)

            user_id= user['id']
            convos= Conversations.objects.filter(Q(user1Id=user_id) | Q(user2Id=user_id))
            conversations=[]
            for conv in convos:
                temp={'id':conv.id}

                messages= Messages.objects.filter(conversationId=conv.id).values()
                message_list=[]
                for m in messages:
                    message_list.append(m)

                user1= app_user.objects.filter(id=conv.user1Id.id).exclude(id=user_id).values("id", "username", "photoUrl")
                user2= app_user.objects.filter(id=conv.user2Id.id).exclude(id=user_id).values("id", "username", "photoUrl")
                if len(user1)>0:
                    other_user=user1.first()
                    temp['user2']= None
                elif len(user2)>0:
                    other_user= user2.first()
                    temp['user1']= None

                if other_user['id'] in online_users:
                    other_user['online']=True
                else:
                    other_user['online']=True

                latest_message= messages.first()['text']
                temp['messages']=message_list
                temp['otherUser']=other_user
                temp['latestMessageText']=latest_message
                conversations.append(temp)
            return JsonResponse(conversations, safe=False)
        except:
            print('Error Occured')

class Message(APIView):
    # expects {recipientId, text, conversationId } in body (conversationId will be null if no conversation exists yet)
    def post(self, request):
        try:
            token = request.headers.get("x-access-token")
            if token:
                    decoded= jwt.decode(token, SESSION_SECRET, algorithms=["HS256"])
                    user = app_user.objects.filter(id=decoded['id']).first()

            if not user:
                return JsonResponse(status=401)

            sender_id=user.id
            body= request.data
            # if we already know conversation id, we can save time and just add it to message and return
            if body.get('conversationId'):
                conv= Conversations.objects.filter(id=body['conversationId']).first()
                message= Messages(senderId=sender_id, text=body['text'], conversationId=conv)
                message.save()
                message_json= model_to_dict(message, fields=[field.name for field in message._meta.fields])
                return JsonResponse({'message':message_json, 'sender':body['sender']})
            # if we don't have conversation id, find a conversation to make sure it doesn't already exist
            conversation=Conversations.find_conversation(sender_id,body['recipientId'])
            if len(conversation)==0:
                # create conversation
                sender=app_user.objects.filter(id=sender_id)
                recipient= app_user.objects.filter(id=body['recipientId'])
                conversation= Conversations(user1Id=sender, user2Id=recipient)
                conversation.save()
                if body['sender'] and body['sender'].id in online_users:
                    body['sender'].is_active= True
                    body['sender'].online= True
            else:
                conversation= conversation.first()
            message= Messages(senderId=sender_id, text=body['text'], conversationId=conversation)
            message.save()
            message_json=model_to_dict(message, fields=[field.name for field in message._meta.fields])
            return JsonResponse({'message':message_json, 'sender':body['sender']})
        except:
            print('Error Occured')
                
class Username(APIView):
    # find users by username
    def get(self,request):
        try:
            token = request.headers.get("x-access-token")
            if token:
                    decoded= jwt.decode(token, SESSION_SECRET, algorithms=["HS256"])
                    user = app_user.objects.filter(id=decoded['id']).first()

            if not user:
                return JsonResponse(status=401)
            username= request.GET['username']
            users= app_user.objects.get(username__contains=username).exclude(id=user.id).values()
            new_users=[]
            for i in len(users):
                user_json= users[i]
                # add online status to each user that is online
                if user_json['id'] in online_users:
                    user_json['online']= True 
                new_users.append(user_json)

            return JsonResponse(users,safe=False)
        except:
            print('Error Occured')


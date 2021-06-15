from django.db import models
import os
import base64
import hashlib
from django.db.models import Q

class app_user(models.Model):
    username = models.CharField(max_length=200,null=False,unique=True)
    email = models.CharField(max_length=200,null=False,unique=True)
    photoUrl = models.CharField(max_length=200)
    password = models.CharField(max_length=200,null=False)
    salt = models.CharField(max_length=80,)
    created_at= models.DateTimeField(auto_now_add=True)

    def create_salt(self):
        result = os.urandom(16)
        return base64.b64encode(result)

    def encrypt_password(self, plain_password, salt):
        hash_creator = hashlib.sha256()
        hash_creator.update(plain_password.encode('utf-8'))
        hash_creator.update(salt.encode('utf-8'))
        return hash_creator.hexdigest()

    def is_password_changed(self):
        old_user = app_user.objects.filter(username=self.username)
        if old_user.exists():
            old_user = old_user.first()
            if self.password != old_user.password:
                return True
        return False

    def set_salt_and_password(self):
        self.salt = self.create_salt().decode("utf-8")
        self.password = self.encrypt_password(self.password,self.salt)

    def save(self, *args, **kwargs):
        self.set_salt_and_password()
        super(app_user, self).save(*args, **kwargs)

    def verify_password(self,password):
        print(self.encrypt_password(password, self.salt))
        if self.encrypt_password(password, self.salt) == self.password:
            return True
        else:
            return False

class Conversations(models.Model):
    user1_id=models.ForeignKey(app_user,on_delete=models.CASCADE, related_name='user1_id')
    user2_id=models.ForeignKey(app_user,on_delete=models.CASCADE, related_name='user2_id')
    created_at= models.DateTimeField(auto_now_add=True)

    # find conversation given two user Ids
    def find_conversation(user1Id,user2Id):
        conversation= Conversations.objects.filter((Q(user1_id=user1Id) | Q(user1_id=user2Id))
                                     , (Q(user2_id=user1Id) | Q(user2_id=user2Id)))
        # return conversation or null if it doesn't exist
        return conversation

class Message(models.Model):
    text = models.CharField(max_length=1000,null=False)
    sender_id= models.IntegerField(null=False)
    conversation_id= models.ForeignKey(Conversations,on_delete=models.CASCADE, related_name='conversation_id')
    created_at= models.DateTimeField(auto_now_add=True)
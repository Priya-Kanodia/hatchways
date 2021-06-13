from django.db import models
import os
import base64
import hashlib

class app_user(models.Model):
    username = models.CharField(max_length=200,null=False,unique=True)
    email = models.CharField(max_length=200,null=False,unique=True)
    photoUrl = models.CharField(max_length=200)
    password = models.CharField(max_length=200,null=False)
    salt = models.CharField(max_length=80,)


    def create_salt(self):
        result = os.urandom(16)
        return base64.b64encode(result)

    def encrypt_password(self, plain_password, salt):
        hash_creator = hashlib.sha256()
        hash_creator.update(plain_password)
        hash_creator.update(salt)
        return hash_creator.hexdigest()


    def is_password_changed(self):
        old_user = app_user.objects.filter(username=self.username)
        if old_user.exists():
            old_user = old_user.first()
            if self.password != old_user.password:
                return True
        return False

    def set_salt_and_password(self):
        self.salt = self.create_salt()
        self.password = self.encrypt_password(self.password.encode('utf-8'),self.salt)


    def save(self, *args, **kwargs):
        self.set_salt_and_password()
        super(app_user, self).save(*args, **kwargs)
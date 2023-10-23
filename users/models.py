import jwt

from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from django.db import models

import uuid

import firebase_admin
import google.cloud
from firebase_admin import credentials, firestore

db = firestore.client()

class UserManager(BaseUserManager):
    def create_user(self, data):
        if data["name"] is None:
            raise TypeError('Users must have a name.')

        if data["email"] is None:
            raise TypeError('Users must have an email address.')
        
        if data["phone"] is None:
            raise TypeError('Users must have an phone.')
        
        if data["password"] is None:
            raise TypeError('Users must have a password.')

        user_id = str(uuid.uuid4())
        user_data = {
            'id': user_id,
            'created': firestore.SERVER_TIMESTAMP,
            'name': data["name"],
            'email': data["email"],
            'phone': data["phone"],
            'password': data["password"],
        }
        user_doc_ref = db.collection('users').document(user_id)
        user_doc_ref = user_doc_ref.set(user_data)
        user_doc = db.collection('users').document(user_id).get()
        return user_doc
    
    def check_if_user_exists(self, email):
        if email is None:
            raise TypeError('Users must have an email address.')
       
        user_doc_ref = db.collection("users")
        user_docs = user_doc_ref.where("email", '==', email).get()

        if not len(user_docs) > 0:
            return False
        else:
            return True

class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(db_index=True, max_length=255)
    email = models.EmailField(db_index=True, unique=True)
    phone = models.CharField(db_index=True, max_length=255)
    created = models.DateTimeField()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', "phone"]
    objects = UserManager()

    def __str__(self):
        return self.email
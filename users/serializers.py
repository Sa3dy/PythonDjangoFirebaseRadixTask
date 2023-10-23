import os
from rest_framework import serializers

from .models import User

from django.contrib.auth import authenticate

import uuid

import firebase_admin
import google.cloud
from firebase_admin import credentials, firestore

import jwt

from datetime import datetime, timedelta

from django.conf import settings

db = firestore.client()

class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        fields = ['name', 'email', 'phone', 'password', 'token']

    def add_new_user(self, data):
        is_user_exists = User.objects.check_if_user_exists(data["email"])

        if is_user_exists:
            raise serializers.ValidationError(
                'There is an already existing user with this email.'
            )
        else:
            user_doc_ref = User.objects.create_user(data)
            user_data = user_doc_ref.to_dict()

            user_data["created"] = str(user_data["created"])

            dt = datetime.now() + timedelta(days=60)
            token = jwt.encode({
                'id': user_data["id"],
                'exp': dt.utcfromtimestamp(dt.timestamp())
            }, settings.SECRET_KEY, algorithm='HS256')

            token.encode().decode('utf-8')

            user_data["token"] = token
            
            return user_data
    
class LoginSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, read_only=True)
    email = serializers.CharField(max_length=255)
    phone = serializers.CharField(max_length=255, read_only=True)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        email = data.get('email', None)
        password = data.get('password', None)

        if email is None:
            raise serializers.ValidationError(
                'An email address is required to log in.'
            )

        if password is None:
            raise serializers.ValidationError(
                'A password is required to log in.'
            )

        user_doc_ref = db.collection("users")
        user_docs = user_doc_ref.where("email", '==', email).get()

        if not len(user_docs) > 0:
            raise serializers.ValidationError(
                'A user with this email and password was not found.'
            )
        
        user_doc = user_docs[0].to_dict()

        if not user_doc["password"] == password:
            raise serializers.ValidationError(
                'Invalid credentials.'
            )

        dt = datetime.now() + timedelta(days=60)

        token = jwt.encode({
            'id': user_doc["id"],
            'exp': dt.utcfromtimestamp(dt.timestamp())
        }, settings.SECRET_KEY, algorithm='HS256')

        token.encode().decode('utf-8')

        return {
            'name': user_doc["name"],
            'email': user_doc["email"],
            'phone': user_doc["phone"],
            'token': token,
        }
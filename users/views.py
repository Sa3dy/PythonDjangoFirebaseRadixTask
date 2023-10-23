import os
from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (LoginSerializer, RegistrationSerializer,)
from .renderers import UserJSONRenderer

import firebase_admin
import google.cloud
from firebase_admin import credentials, firestore

db = firestore.client()

class RegistrationAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer
    renderer_classes = (UserJSONRenderer,)

    def post(self, request):
        user = request.data.get('user', {})

        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        data = serializer.add_new_user(user)

        return Response(data, status=status.HTTP_200_OK)
    
class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = LoginSerializer

    def post(self, request):
        user = request.data.get('user', {})

        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def retrieve(self, request, *args, **kwargs):
        users_collection_ref = db.collection('users')
        chat_collection_ref = db.collection('chat')
        try:
            chat_docs = chat_collection_ref.get()
            users_docs = users_collection_ref.get()
            mapped_chat_docs = map(lambda d: d.to_dict(), chat_docs)
            mapped_users_docs = map(lambda d: d.to_dict(), users_docs)
        except google.cloud.exceptions.NotFound:
            print("No Data.")

        return Response(mapped_users_docs, status=status.HTTP_200_OK)
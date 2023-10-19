import os
from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (LoginSerializer, RegistrationSerializer, UserSerializer,)
from .renderers import UserJSONRenderer

import firebase_admin
import google.cloud
from firebase_admin import credentials, firestore

ROOT_DIR = os.path.abspath(os.curdir)
cred = credentials.Certificate(ROOT_DIR + "\\credentials\\serviceAccount.json")
app = firebase_admin.initialize_app(cred)

store = firestore.client()

class RegistrationAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer
    renderer_classes = (UserJSONRenderer,)

    def post(self, request):
        user = request.data.get('user', {})

        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
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
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)

    def retrieve(self, request, *args, **kwargs):
        users_collection_ref = store.collection('users')
        chat_collection_ref = store.collection('chat')
        try:
            chat_docs = chat_collection_ref.get()
            users_docs = users_collection_ref.get()
            mapped_chat_docs = map(lambda d: d.to_dict(), chat_docs)
            mapped_users_docs = map(lambda d: d.to_dict(), users_docs)
        except google.cloud.exceptions.NotFound:
            print("No Data.")

        return Response(mapped_chat_docs, status=status.HTTP_200_OK)
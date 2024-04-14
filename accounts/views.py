from django.shortcuts import render
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import JsonResponse
from requests import request, get
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from djoser.views import UserViewSet

from .models import User, Contact
from serializers.serializers_accounts import ContactSerializer, UserSerializer

# Create your views here.
class ActivateUser(UserViewSet):
    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
 
        # this line is the only change from the base implementation.
        kwargs['data'] = {"uid": self.kwargs['uid'], "token": self.kwargs['token']}
 
        return serializer_class(*args, **kwargs)
 
    def activation(self, request, uid, token, *args, **kwargs):
        super().activation(request, *args, **kwargs)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
class ContactView(viewsets.ModelViewSet):
    """ Представление для работы с контактами """
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    #permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrAdminOrReadOnly,)
    
    # функция для получения контактов
    def get_queryset(self):
        if self.request.user.is_anonymous:
            return Contact.objects.none()
        if not self.request.user.is_authenticated:
            return Contact.objects.none()
        return Contact.objects.filter(user=self.request.user)
    
    # функция для получения контактов
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
                
    # функция обновления        
    def update(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"Status": False, "Error": "Log in required"}, status=status.HTTP_403_FORBIDDEN)
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return JsonResponse({"Status": True}, status=status.HTTP_200_OK)
    
    # функция удаления
    def destroy(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"Status": False, "Error": "Log in required"}, status=status.HTTP_403_FORBIDDEN)
        
        instance = self.get_object()
        self.perform_destroy(instance)
        return JsonResponse({"Status": True}, status=status.HTTP_204_NO_CONTENT)   
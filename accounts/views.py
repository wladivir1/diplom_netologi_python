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
from rest_framework.generics import CreateAPIView
from djoser.views import UserViewSet

from .models import User, Contact
from serializers.serializers_accounts import ContactSerializer, UserSerializer, TypeUserSerializer
from permission.permissions import IsOwnerOrAdminOrReadOnly

# Create your views here.
class ActivateUser(UserViewSet):
    def get_serializer(self, *args, **kwargs) -> UserSerializer:
        """
        Переопределение сериализатора для активации пользователя
        """
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
 
        # this line is the only change from the base implementation.
        kwargs['data'] = {"uid": self.kwargs['uid'], "token": self.kwargs['token']}
 
        return serializer_class(*args, **kwargs)
 
    def activation(self, request, uid, token, *args, **kwargs) -> Response:
        """
        Активация пользователя
        """
        super().activation(request, *args, **kwargs)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
class ContactView(viewsets.ModelViewSet):
    """ Представление для работы с контактами """
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = (IsOwnerOrAdminOrReadOnly,)
    
    def get_queryset(self) -> Contact:
        if self.request.user.is_anonymous:
            return Contact.objects.none()
        if not self.request.user.is_authenticated:
            return Contact.objects.none()
        return Contact.objects.filter(user=self.request.user)
    
    
    def list(self, request, *args, **kwargs) -> Response:
        """ Функция для получения списка контактов """
        return super().list(request, *args, **kwargs)
   
    def update(self, request, *args, **kwargs) -> Response:
        """ Функция для обновления контактов """
        contact_id = request.data.get('id')
        if contact_id is None:
            return JsonResponse({"Status": False, "Error": "Contact id is required"}, status=status.HTTP_400_BAD_REQUEST)

        data = {}
        for field in ['index', 'city', 'street', 'house', 'structure', 'building', 'apartment']:
            value = request.data.get(field)
            if value is not None:
                data[field] = value

        try:
            Contact.objects.filter(id=contact_id).update(**data)
        except Exception as e:
            return JsonResponse({"Status": False, "Error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return JsonResponse({"Status": True}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs) -> Response:
        """ Функция для удаления контактов """
        items = request.data.get('items')
        if items is None:
            return JsonResponse({"Status": False, "Error": "Не указаны данные"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            Contact.objects.filter(id__in=items).delete()
        except Exception as e:
            return JsonResponse({"Status": False, "Error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return JsonResponse({"Status": True}, status=status.HTTP_200_OK)
    
class TypeUserView(CreateAPIView):
    """ Представление для работы с типами контактов """
    queryset = User.objects.all()
    serializer_class = TypeUserSerializer
    #permission_classes = (IsOwnerOrAdminOrReadOnly,)
    
    def post(self, request, *args, **kwargs) -> Response:
        """ Функция для изменения типа пользователя """
        user = User.objects.filter(id=request.user.id).update(type=request.data['type'])
        if not user:
            return JsonResponse({"Status": False, "Error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        return JsonResponse({"Status": True}, status=status.HTTP_200_OK)     
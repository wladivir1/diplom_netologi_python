from distutils.util import strtobool
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.db.models import Q, Sum, F
from djoser.views import UserViewSet
from rest_framework import viewsets, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, ListCreateAPIView, CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import serializers
from django.http import JsonResponse
from django.core.validators import URLValidator
from requests import patch, put, HTTPError, request, get
from ujson import loads as load_json
from yaml import serialize_all, serializer, serialize, load as load_yml, Loader

from accounts.models import User, Contact
from permission.permissions import IsOwnerOrAdminOrReadOnly, IsOwnerOrReadOnly
from .models import (Shop, Category, Parameter,
                     Product, ProductInfo, 
                     ProductParameter, Order, OrderItem)
from serializers.searializers_shop import (ShopSerializer, CategorySerializer,
                          ProductInfoSerializer, OrderItemSerializer,  
                          ProductSerializer, OrderSerializer, 
                          ProductParameterSerializer, ParameterSerializer)


class PartnerUpdate(APIView):
    """
    Класс для обновления списка товаров поставщика
    """
    # функция для обновления прайса
    def post(self, request, *args, **kwargs) -> JsonResponse:
        
        if request.user.type != 'shop':
            return JsonResponse({"Status": False, "Error": "Только для магазинов"}, status=status.HTTP_403_FORBIDDEN)
        
        url = request.data.get('url')
        if url:
            validat_url = URLValidator()
            try:
                Shop.objects.filter(user_id=request.user.id).update(url=url)
            except ValidationError as error:
                return JsonResponse({"Status": False, "Errors": str(error)}, status=status.HTTP_400_BAD_REQUEST)
            else:
                stream = get(url).content
                data = load_yml(stream, Loader=Loader)
                shop, _ = Shop.objects.get_or_create(name=data['shop'], user_id=request.user.id)
                for category_data in data['categories']:
                    category_obj, _ = Category.objects.get_or_create(id=category_data['id'], name=category_data['name'])
                    category_obj.shop.add(shop.id)
                    category_obj.save()
                ProductInfo.objects.filter(shop_id=shop.id).delete()
                for item in data['goods']:
                    product, _ = Product.objects.get_or_create(name=item['name'], category_id=item['category'])
                    product_info = ProductInfo.objects.create(
                        product_id=product.id,
                        external_id=item['id'],
                        model=item['model'],
                        price=item['price'],
                        price_rrc=item['price_rrc'],
                        quantity=item['quantity'],
                        shop_id=shop.id
                    )
                    for name, value in item['parameters'].items():
                        parameter_object, _ = Parameter.objects.get_or_create(name=name)
                        ProductParameter.objects.create(
                            product_info_id=product_info.id,
                            parameter_id=parameter_object.id,
                            value=value
                        )

                return JsonResponse({'Status': True}, status=status.HTTP_200_OK)

        return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'}, status=status.HTTP_400_BAD_REQUEST)

        
        
class PartnerStatus(ListCreateAPIView):
    """
    Класс для изменения статуса поставщика
    """
    # функция для получения статуса
    def get(self, request, *args, **kwargs) -> JsonResponse:
        
        if request.user.type != 'shop':
            return JsonResponse({"Status": False, "Error": "Только для магазинов"}, status=status.HTTP_403_FORBIDDEN)
        
        shop = Shop.objects.get(user_id=request.user.id)
        return JsonResponse({"Status": True, "status": shop.status})
        
    
    # функция для изменения статуса
    def post(self, request, *args, **kwargs) -> JsonResponse:
        
        if request.user.type != 'shop':
            return JsonResponse({"Status": False, "Error": "Только для магазинов"}, status=status.HTTP_403_FORBIDDEN)
        shop = Shop.objects.get(user_id=request.user.id)
        if shop.status == 'closed':
            Shop.objects.filter(user_id=request.user.id).update(status='open')
            return JsonResponse({"Status": True}, status=status.HTTP_200_OK)
        else :
            Shop.objects.filter(user_id=request.user.id).update(status='closed')
            return JsonResponse({"Status": True}, status=status.HTTP_200_OK)


class CategoryView(ListCreateAPIView):
    """
    Класс для просмотра категорий
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    


class ShopListView(ListAPIView):
    """
    Класс для просмотра списка магазинов
    """
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    permission_classes = [AllowAny]
    filterset_fields = ['status']
 
class ProductInfoView(ListAPIView):
    """
    Класс для просмотра списка продуктов
    """
    queryset = ProductInfo.objects.all()
    serializer_class = ProductInfoSerializer
    permission_classes = [AllowAny]
    filterset_fields = ['shop', 'product__category', 'product__name', 'quantity', 'price']



class BasketView(viewsets.ModelViewSet):
    """
    Класс для работы с корзиной
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    lookup_field = 'id'
    
    # функция для получения корзины пользователя
    def get_queryset(self):
        return self.queryset.filter(user_id=self.request.user.id)


class СonfirmationOrderView(APIView):
    """
    Класс для подтверждения заказа
    """
    # Подтверждение заказа
    def post(self, request, *args, **kwargs) -> JsonResponse:    
        try:
            basket = Order.objects.filter(user_id=request.user.id, state='new')
            if not basket:
                return JsonResponse({"Status": False, "Error": "Новых заказов нет"}, status=status.HTTP_404_NOT_FOUND)
            order_id = request.data.get('order_id')
            contact_id = request.data.get('contact_id')
            if not order_id or not contact_id:
                return JsonResponse({"Status": False, "Error": "Не указаны данные"}, status=status.HTTP_400_BAD_REQUEST)
            if not Order.objects.filter(id=order_id).exists():
                return JsonResponse({"Status": False, "Error": "Заказ не найден"}, status=status.HTTP_404_NOT_FOUND)
            if not Contact.objects.filter(id=contact_id).exists():
                return JsonResponse({"Status": False, "Error": "Контакт не найден"}, status=status.HTTP_404_NOT_FOUND)
            Order.objects.filter(id=order_id).update(state='confirmed')
            OrderItem.objects.filter(order_id=order_id).update(contact=Contact.objects.get(id=contact_id))
            return JsonResponse({"Status": True}, status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({"Status": False, "Error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    
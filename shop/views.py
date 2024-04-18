import logging

from django.conf import settings
from django.http import Http404
from django.core.exceptions import ValidationError
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, ListCreateAPIView
from rest_framework.permissions import AllowAny
from django.http import JsonResponse
from django.core.validators import URLValidator
from requests import exceptions, get
from ujson import loads as load_json
from yaml import load as load_yml, Loader

from accounts.models import User, Contact
from .models import (Shop, Category, Parameter,
                    Product, ProductInfo, 
                    ProductParameter, Order, OrderItem)
from serializers.searializers_shop import (ShopSerializer, CategorySerializer,
                                            ProductInfoSerializer, OrderSerializer)



# Create a logger
logger = logging.getLogger(__name__)


class PartnerUpdate(APIView):
    """
    Класс для обновления списка товаров поставщика
    """
    # функция для обновления прайса
    def post(self, request, *args, **kwargs) -> JsonResponse:
        # Check if the user is a shop
        if request.user.type != 'shop':
            return JsonResponse({"Status": False, "Error": "Только для магазинов"},
                                status=status.HTTP_403_FORBIDDEN)

        # Get the url and validate it
        url = request.data.get('url')
        if not url:
            return JsonResponse({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'},
                                status=status.HTTP_400_BAD_REQUEST)
        validat_url = URLValidator()
        try:
            validat_url(url)
        except ValidationError as e:
            return JsonResponse({"Status": False, "Errors": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Update the shop's url
        try:
            Shop.objects.filter(user_id=request.user.id).update(url=url)
        except Exception as e:
            return JsonResponse({"Status": False, "Error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Get the yml file
        try:
            stream = get(url).content
        except exceptions.RequestException as e:
            return JsonResponse({"Status": False, "Error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Parse the yml file
        try:
            data = load_yml(stream, Loader=Loader)
        except ValueError as e:
            return JsonResponse({"Status": False, "Error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Create the shop if it does not exist
        shop, _ = Shop.objects.get_or_create(name=data['shop'], user_id=request.user.id)

        # Update the categories
        for category_data in data['categories']:
            category_obj, _ = Category.objects.get_or_create(id=category_data['id'], name=category_data['name'])
            category_obj.shop.add(shop.id)
            category_obj.save()

        # Delete all of the product info
        try:
            ProductInfo.objects.filter(shop_id=shop.id).delete()
        except Exception as e:
            return JsonResponse({"Status": False, "Error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Create the product info
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

            # Create the product parameters
            for name, value in item['parameters'].items():
                parameter_object, _ = Parameter.objects.get_or_create(name=name)
                ProductParameter.objects.create(
                    product_info_id=product_info.id,
                    parameter_id=parameter_object.id,
                    value=value
                )

        return JsonResponse({'Status': True}, status=status.HTTP_200_OK)

   
class PartnerStatus(ListCreateAPIView):
    """
    Класс для изменения статуса поставщика
    """
    # функция для получения статуса магазина
    def get(self, request, *args, **kwargs) -> JsonResponse:
        shop = Shop.objects.get(user_id=request.user.id)
        return JsonResponse({"Status": True, "status": shop.status})

    # функция для изменения статуса
    def post(self, request, *args, **kwargs) -> JsonResponse:
        
        if request.user.type != 'shop':
            return JsonResponse({"Status": False, "Error": "Только для магазинов"}, status=status.HTTP_403_FORBIDDEN)
        try:
            shop = Shop.objects.get(user_id=request.user.id)
            if shop.status == 'closed':
                Shop.objects.filter(user_id=request.user.id).update(status='open')
                return JsonResponse({"Status": True}, status=status.HTTP_200_OK)
            else:
                Shop.objects.filter(user_id=request.user.id).update(status='closed')
                return JsonResponse({"Status": True}, status=status.HTTP_200_OK)
        except Shop.DoesNotExist:
            return JsonResponse({"Status": False, "Error": "Shop not found"}, status=status.HTTP_404_NOT_FOUND)

class PartnerOrders(ListAPIView):
    
    queriset = Order.objects.all()
    serializer_class = OrderSerializer
    
    def get_queryset(self):
        return self.queriset.filter(ordered_items__product_info__shop__user_id=self.request.user.id, state='new')
    
    def list(self, request, *args, **kwargs) -> JsonResponse:
        """
        Функция для получения списка заказов
        """
        try:
            # получаем id заказа
            order_id = request.query_params.get('order_id')
            if order_id is not None:
                self.queryset = self.queryset.filter(order_id=order_id)
                self.queryset = self.queryset.exclude(state='basket')

            return super().list(request, *args, **kwargs)
        except Exception as e:
            # Log the error and return a generic response to prevent leaking information
            logger.exception(e)
            raise Http404("Произошла ошибка")
    
    
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
    #permission_classes = [IsOwnerOrAdminOrReadOnly]
    
    def get_queryset(self):
        return self.queryset.filter(user_id=self.request.user.id)
    
    def list(self, request, *args, **kwargs) -> JsonResponse:
        """
        Функция для получения списка корзин
        """
        if not request or not request.user:
            return JsonResponse({"Status": False, "Error": "Невозможно проверить тип пользователя, так как запрос или пользователь не определены"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Check for unhandled exceptions
        try:
            order_items = OrderItem.objects.filter(order__user_id=request.user.id, order__state='new')
            list_order_items = []
            for item in order_items:
                id_order = item.order.id
                created_at = item.order.created_at
                total_sum = item.product_info.price * item.quantity
                stae = item.order.state
                list_order_items.append({
                    "id": id_order,
                    "created_at": created_at,
                    "total_sum": total_sum,
                    "state": stae
                })
            
            return JsonResponse({
                "Status": True,
                "Basket": list_order_items
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception('unhandled exception when getting order')
            return JsonResponse({"Status": False, "Error": "Непредвиденная ошибка"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  
    
    def create(self, request, *args, **kwargs) -> JsonResponse:
        """
        Функция для создания корзины
        """

        if User.objects.get(id=request.user.id).type == 'shop':
            return JsonResponse({"Status": False, "Error": "Нельзя создавать корзину для магазина"}, status=status.HTTP_400_BAD_REQUEST)
        
        items = request.data.get('items')
        if items is None:
            return JsonResponse({"Status": False, "Error": "Не указаны данные"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            items_dict = load_json(items)
        except ValueError as e:
            return JsonResponse({"Status": False, "Error": f"Неверный формат запроса: {e}"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            contact = Contact.objects.filter(user_id=request.user.id).first()
            if contact is None:
                return JsonResponse({"Status": False, "Error": "Не указан контакт для данного пользователя"}, status=status.HTTP_400_BAD_REQUEST)
        except Contact.DoesNotExist:
            return JsonResponse({"Status": False, "Error": "Не найден контакт для данного пользователя"}, status=status.HTTP_404_NOT_FOUND)

        try:
            order = Order.objects.create(user_id=request.user.id, state='basket')
            order.save()
        except Exception as e:
            return JsonResponse({"Status": False, "Error": f"Ошибка при создании заказа: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            for item in items_dict:
                product_info = ProductInfo.objects.filter(id=item["product_info"]).first()
                order_item = OrderItem.objects.create(order=order, product_info=product_info, quantity=item["quantity"], contact=contact)
                order_item.save()
        except Exception as e:
            return JsonResponse({"Status": False, "Error": f"Ошибка при добавлении товаров в заказ: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return JsonResponse({"Status": True}, status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs) -> JsonResponse:
        """ Функция для изменения количества товара в корзине """
        item_stings = request.data.get('items')
        if item_stings is None:
            return JsonResponse({"Status": False, "Error": "Не указаны данные"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            items_dict = load_json(item_stings)
        except ValueError:
            return JsonResponse({"Status": False, "Error": "Неверный формат запроса"}, status=status.HTTP_400_BAD_REQUEST)
        else:   
            basket, _ = Order.objects.get_or_create(user_id=request.user.id, state='basket')
            for item in items_dict:
                 
                OrderItem.objects.update_or_create(order=basket.id, product_info=item['id'], defaults={'quantity': item['quantity']})
            return JsonResponse({"Status": True}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs) -> JsonResponse:
        """
        Функция для удаления товара из корзины
        """
        items_sting = request.data.get('items')
        if items_sting is None:
            return JsonResponse({"Status": False, "Error": "Не указаны данные"}, status=status.HTTP_400_BAD_REQUEST)
        items_list = items_sting.split(',')
        try:
            basket = Order.objects.filter(user_id=request.user.id, state='basket')
        except Order.DoesNotExist:
            return JsonResponse({"Status": False, "Error": "Корзина не найдена"}, status=status.HTTP_404_NOT_FOUND)
        for order_item_id in items_list:
            if order_item_id.isdigit():
                try:
                    basket.filter(id=order_item_id).delete()
                except ValueError as exc:
                    return JsonResponse({"Status": False, "Error": "Ошибка удаления"}, status=status.HTTP_400_BAD_REQUEST)
                except Exception as exc:
                    logger.exception('unhandled exception when deleting order item')
                    return JsonResponse({"Status": False, "Error": "Непредвиденная ошибка"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return JsonResponse({"Status": True}, status=status.HTTP_200_OK)            
                
        
class OrderView(APIView):
    """
    Класс для подтверждения заказа
    """
    
    def get(self, request, *args, **kwargs) -> JsonResponse:
        """
        Функция для получения истории о заказах
        """
        # Check for null pointer references
        if not request or not request.user:
            return JsonResponse({"Status": False, "Error": "Невозможно проверить тип пользователя, так как запрос или пользователь не определены"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Check for unhandled exceptions
        try:
            order_items = OrderItem.objects.filter(order__user_id=request.user.id)
        except OrderItem.DoesNotExist:
            return JsonResponse({"Status": False, "Error": "Непредвиденная ошибка"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        list_order_items = []
        for item in order_items:
            if not item or not item.order or not item.product_info or not item.product_info.shop or not item.product_info.product:
                return JsonResponse({"Status": False, "Error": "Непредвиденная ошибка"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            if item.order.state == 'basket':
                continue
            id_order = item.order.id
            shop = item.product_info.shop.name
            product_name = item.product_info.product.name
            quantity = item.quantity
            created_at = item.order.created_at
            total_sum = item.product_info.price * item.quantity
            stae = item.order.state
            list_order_items.append({
                "id": id_order,
                "shop": shop,
                "product_name": product_name,
                "quantity": quantity,
                "created_at": created_at,
                "total_sum": total_sum,
                "state": stae
            })

        return JsonResponse({
            "Status": True,
            "Basket": list_order_items
        }, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs) -> JsonResponse:
        """
        Функция для подтверждения заказа
        """  
        try:
            # Check for null pointer references
            if not request or not request.user:
                return JsonResponse({"Status": False, "Error": "Невозможно проверить тип пользователя, так как запрос или пользователь не определены"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
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
            
            is_updated = Order.objects.filter(id=order_id).update(state='new')
            OrderItem.objects.filter(order_id=order_id).update(contact=Contact.objects.get(id=contact_id))
            if is_updated:
                    request.user.email_user(f'Обновление статуса заказа',
                                            'Заказ подтвержден',
                                            from_email=settings.EMAIL_HOST_USER)
            return JsonResponse({"Status": True}, status=status.HTTP_200_OK)
        except Exception as e:
            # Log the error and return a generic response to prevent leaking information
            logger.exception(e)
            return JsonResponse({"Status": False, "Error": "Произошла ошибка сервера"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def put(self, request, *args, **kwargs) -> JsonResponse:
        """
        Функция для обновления статуса заказа
        """
        
        if request.user.type != 'shop':
            return JsonResponse({"Status": False, "Error": "Только для магазинов"}, status=status.HTTP_403_FORBIDDEN)
        
        order_id = request.data.get('items')
        if order_id is None:
            return JsonResponse({"Status": False, "Error": "Не указаны данные"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            items_dict = load_json(order_id)
        except ValueError:
            return JsonResponse({"Status": False, "Error": "Неверный формат запроса"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            for item in items_dict:
                if type(item['id']) == int and type(item['state']) == str:
                    Order.objects.update_or_create(id=item['id'], defaults={'state': item['state']})
            return JsonResponse({"Status": True}, status=status.HTTP_200_OK)
        
        # Check for null pointer references
        if not request.user:
            return JsonResponse({"Status": False, "Error": "Невозможно отправить email, так как пользователь не определен"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        #Check for unhandled exceptions
        try:
            if is_updated:
                request.user.email_user(f'Обновление статуса заказа',
                                        f'Статус заказа изменен на {state}',
                                        from_email=settings.EMAIL_HOST_USER)
        except Exception as e:
            return JsonResponse({"Status": False, "Error": f"Ошибка при отправке email: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return JsonResponse({"Status": True}, status=status.HTTP_200_OK)

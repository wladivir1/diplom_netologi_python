# shop/serializers.py
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from djoser.serializers import UserSerializer
from djoser.serializers import UserCreateSerializer


from shop.models import (Shop, Category, Product,
                     ProductInfo, Parameter, ProductParameter,
                     Order, OrderItem)
from . serializers_accounts import ContactSerializer
from accounts.models import Contact, User


class ShopSerializer(serializers.ModelSerializer):
    """ Сериализатор магазина """
    
    class Meta:
        model = Shop
        fields = ('id', 'name', 'status')
        ordering = ('-name',)
        read_only_fields = ('id',)
        validators = [
            UniqueTogetherValidator(
                queryset=Shop.objects.all(),
                fields=('name',)
            ),
        ]
 

class CategorySerializer(serializers.ModelSerializer):
    """ Сериализатор категории """
    class Meta:
        model = Category
        fields = ('id', 'name')
        ordering = ('-name',)
        read_only_fields = ('id',)
        
        
class ProductSerializer(serializers.ModelSerializer):
    """ Сериализатор продукта """
    category = serializers.StringRelatedField()
    
    class Meta:
        model = Product
        fields = ('id','category', 'name')
        
        
        
class ProductParameterSerializer(serializers.ModelSerializer):
    """ Сериализатор параметра """
    parametr = serializers.StringRelatedField()
    
    class Meta:
        model = ProductParameter
        fields = ('id', 'parametr', 'value')

        
class ProductInfoSerializer(serializers.ModelSerializer):
    """ Сериализатор информации о продукте """
    product = ProductSerializer(read_only=True)
    product_parameters = ProductParameterSerializer(read_only=True, many=True)
    
    class Meta:
        model = ProductInfo
        fields = ('id', 'shop', 'model', 'product', 'product_parameters', 'quantity', 'price')
        read_only_fields = ('id',)  
        
              
class ParameterSerializer(serializers.ModelSerializer):
    """ Сериализатор параметра """
    class Meta:
        model = Parameter
        fields = ('id', 'name')
        
        
class OrderItemSerializer(serializers.ModelSerializer):
    """ Сериализатор для отображения элемента заказа """
    total_sum = serializers.SerializerMethodField()
    
    # функция для получения общей суммы
    def get_total_sum(self, obj):
        if obj is None:
            raise ValueError("obj cannot be None")
        if obj.product_info is None or obj.product_info.price is None:
            raise ValueError("obj.product_info or obj.product_info.price cannot be None")
        if obj.quantity is None or obj.quantity <= 0:
            raise ValueError("obj.quantity cannot be None or <= 0")
        
        return obj.product_info.price * obj.quantity
    
    class Meta:
        model = OrderItem
        fields = ('id', 'product_info', 'quantity', 'total_sum') 
        read_only_fields = ('id',)
        
       
class OrderSerializer(serializers.ModelSerializer):
    """ Сериализатор заказа """
    items = OrderItemSerializer(many=True, source='ordered_items')

    class Meta:
        model = Order
        fields = ('id', 'items')
        read_only_fields = ('id',)
        lookup_field = 'id'
        extra_kwargs = {
            'items': {'write_only': True},
        }
        validators = [
            UniqueTogetherValidator(
                queryset=Order.objects.all(),
                fields=('items',),
                message='Такой заказ уже существует'
            ),
        ]
        
    # функция для создания заказа
    def create(self, validated_data) -> Order:
        request = self.context['request']
        if request.user is None:
            raise serializers.ValidationError('Покупатель не найден')
        if request.user.type == 'shop':
            raise serializers.ValidationError('Только для покупателей')
        
        ordered_items_data = validated_data.pop('ordered_items')
        contact = Contact.objects.filter(user_id=request.user.id).first()
        if contact is None:
            raise serializers.ValidationError('Контакты не указаны')
        order = Order.objects.create(user_id=request.user.id, state='new', **validated_data)
        try:
            for ordered_item_data in ordered_items_data:
                OrderItem.objects.create(order=order, contact=contact, **ordered_item_data)
        except (TypeError, ValueError):
            order.delete()
            raise
        except Exception:
            order.delete()
            raise serializers.ValidationError('Неизвестная ошибка')
        return order
    
    
    
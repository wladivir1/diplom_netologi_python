# shop/serializers.py
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from versatileimagefield.serializers import VersatileImageFieldSerializer

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
        fields = ('id','category', 'name', 'image')        


class ImageProductSerializer(serializers.ModelSerializer):
    """ Сериализатор изображения продукта """
    
    class Meta:
        model = Product
        fields = ('id','name', 'image')
        read_only_fields = ('id', 'name')


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
        """
        Calculates the total sum of an order item and checks for potential bugs.

        Arguments:
            obj: An OrderItem object

        Returns:
            The total sum of the order item

        Raises:
            ValueError: If obj is None, obj.product_info is None, obj.quantity is None,
                obj.quantity is <= 0, or obj.product_info.price is None.
            TypeError: If obj.product_info or obj.product_info.price is not a number.
        """
        if obj is None:
            raise ValueError("obj cannot be None")
        if obj.product_info is None:
            raise ValueError("obj.product_info cannot be None")
        if obj.quantity is None:
            raise ValueError("obj.quantity cannot be None")
        if obj.quantity <= 0:
            raise ValueError("obj.quantity must be > 0")
        if obj.product_info.price is None:
            raise ValueError("obj.product_info.price cannot be None")
        try:
            total_sum = obj.product_info.price * obj.quantity
        except TypeError as exc:
            raise TypeError(
                f"obj.product_info.price and obj.quantity must be numbers, but got "
                f"{type(obj.product_info.price).__name__} and {type(obj.quantity).__name__}"
            ) from exc
        return total_sum
    
    contact = ContactSerializer(read_only=True)
    #product_info = ProductInfoSerializer(read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ('id', 'product_info', 'quantity', 'total_sum', 'contact') 
        read_only_fields = ('id',)
        extra_kwargs = {
            'total_sum': {'read_only': True},
            'contact': {'read_only': True},
        }
        
       
class OrderSerializer(serializers.ModelSerializer):
    """ Сериализатор заказа """
    
    order_items = OrderItemSerializer(many=True, source='ordered_items')
    
    class Meta:
        model = Order
        fields = ('id', 'order_items', 'created_at',  'state')
        read_only_fields = ('id',)
        extra_kwargs = {
            'order_items': {'write_only': True},
            'state': {'read_only': True},
            'created_at': {'read_only': True},
        }
        validators = [
            UniqueTogetherValidator(
                queryset=Order.objects.all(),
                fields=('order_items',),
                message='Такой заказ уже существует'
            ),
        ]

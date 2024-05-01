import os
import yaml
import json

from django.conf import settings
from django.core.mail import send_mail, EmailMessage
from django.conf.global_settings import EMAIL_HOST_USER
from django.core.mail.message import EmailMultiAlternatives

from backend_api.celery import app
from shop.models import Order, OrderItem


@app.task()
def send_email(message: str, email: str, *args, **kwargs) -> str:
    """ Функция для отправки письма """
    title = 'Title'
    email_list = list()
    email_list.append(email)
    try:
        msg = EmailMultiAlternatives(subject=title, body=message, from_email=EMAIL_HOST_USER, to=email_list)
        msg.send()
        return f'Title: {msg.subject}, Message:{msg.body}'
    except Exception as e:
        raise e

@app.task()
def create_yml_json(order_id):
    """ Функция для создания yaml файла """
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist as e:
        raise ValueError(f'Order with id={order_id} does not exist') from e
    
    if order.state == 'new':
        # Gather information for the file
        products = OrderItem.objects.filter(order_id=order.id)
        # Check for null pointer references
        yaml_file_path = settings.BASE_DIR / 'fixtures' / 'orders' / 'new_order.yaml'
        json_file_path = settings.BASE_DIR / 'fixtures' / 'orders' / 'new_order.json'
        
        folder_path = os.path.join(settings.BASE_DIR, 'orders')
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        
        produc_info = []
        orders = []   
        for product in products:
            orders_id = product.order.id
            category = product.product_info.product.category.name
            product_info_id = product.product_info.id
            product_name = product.product_info.product.name
            quantity = product.quantity
            total_sum = product.product_info.price * quantity
            produc_info.append({
                'category': category,
                'product_info_id': product_info_id,
                'product_name': product_name,
                'quantity': quantity,
                'total_sum': total_sum
            })
            orders.append({
                'orders_id': orders_id,
                'order_items': produc_info,
            })

        # Create YAML file
        with open(yaml_file_path, 'w') as file:
            data = {
                "orders": orders
            }
            yaml.dump(data, file)
            
        # Create JSON file    
        with open(json_file_path, 'w') as file:
            data = {
                "orders": orders
            }
            json.dump(data, file, indent=4)

@app.task()           
def send_email_to_supplier(order_id):
    """ Функция для отправки письма контрагенту """
    
    order = Order.objects.get(id=order_id)

    if order.state == 'new':
        products = OrderItem.objects.filter(order_id=order.id)
        shop_email = products[0].product_info.shop.user.email
        
        subject = 'New Order Details'
        message = 'Please find the order file attached.'
        from_email = order.user.email
        
        email = EmailMessage(subject, message, from_email, [shop_email])
        
        # Attach the order file
        email.attach_file('fixtures/orders/new_order.yaml')

        # Send the email
        email.send()

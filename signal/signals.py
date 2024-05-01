from django.dispatch import receiver, Signal

from shop.tasks import send_email
from accounts.models import User
from versatileimagefield.image_warmer import VersatileImageFieldWarmer
from shop.models import Product
from backend_api.celery import app


new_order = Signal(
    providing_args=['user_id'],
)

@receiver(new_order)
def new_order_signal(user_id, **kwargs):
    """
    отправяем письмо при изменении статуса заказа
    """
    # send an e-mail to the user
    user = User.objects.get(id=user_id)
    title = "Обновление статуса заказа"
    message = 'Заказ подтвержден'
    email = user.email
    send_email.apply_async((title, message, email), countdown=5 * 60)

@app.task()    
@receiver(models.signals.post_delete, sender=User)
def delete_User_images(sender, instance, **kwargs):
    """
    Deletes User image renditions on post_delete.
    """
    # Deletes Image Renditions
    instance.avatar.delete_all_created_images()
    # Deletes Original Image
    instance.avatar.delete(save=False)

@app.task()
@receiver(models.signals.post_save, sender=User)
def warm_User_headshot_images(sender, instance, **kwargs):
    """Ensures User head shots are created post-save"""
    user_img_warmer = VersatileImageFieldWarmer(
        instance_or_queryset=instance,
        rendition_key_set='user_avatar',
        image_attr='avatar',
    )
    num_created, failed_to_create = user_img_warmer.warm()
    
@app.task()
@receiver(models.signals.post_save, sender=Product)
def warm_User_headshot_images(sender, instance, **kwargs):
    """Ensures Product head shots are created post-save"""
    product_img_warmer = VersatileImageFieldWarmer(
        instance_or_queryset=instance,
        rendition_key_set='product_image',
        image_attr='image',
    )
    num_created, failed_to_create = product_img_warmer.warm()
    
@app.task()    
@receiver(models.signals.post_delete, sender=Product)
def delete_Product_images(sender, instance, **kwargs):
    """
    Deletes Product image renditions on post_delete.
    """
    # Deletes Image Renditions
    instance.image.delete_all_created_images()
    # Deletes Original Image
    instance.image.delete(save=False)     

from django.dispatch import receiver, Signal

from shop.tasks import send_email
from accounts.models import User


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

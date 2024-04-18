import yaml

from django.conf.global_settings import EMAIL_HOST_USER
from django.core.mail.message import EmailMultiAlternatives

from backend_api.celery import app


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

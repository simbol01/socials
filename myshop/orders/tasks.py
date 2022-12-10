from myshop.celery import app
from django.core.mail import send_mail
from .models import Order
from celery import shared_task



@shared_task
def order_created(order_id):
    # send an email notification when an order is successfully created
    order = Order.objects.get(id=order_id)
    subject = 'Order nr. {}'.format(order_id)
    message = 'Dear {}, \n\n You have successfully placed your order.\
        Your order id is {}'.format(order.first_name, order.id)
    
    mail_sent = send_mail(subject, message, 'sambolu01@gmail.com',[order.email])
    return mail_sent
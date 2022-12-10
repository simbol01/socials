import braintree

from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.http import HttpResponse
from orders.models import Order
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
import weasyprint
from io import BytesIO

# Create your views here.

def payment_process(request):
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        nonce = request.POST.get('payment_method_nonce', None)

        # create and submit transaction
        result = braintree.Transaction.sale({
            'amount':'{:.2f}'.format(order.get_total_cost()),
            'payment_method_nonce':nonce,
            'options':{
                'submit_for_settlement': True
            }
        
        })
        if result.is_success:
            order.paid = True
            order.braintree_id = result.transaction.id
            order.save()

            # create an invoice email
            subject = "My Shop - Invoice no. {}".format(order.id)
            message = "Please find attachement below of the invoice of your recent purchase."
            email = EmailMessage(subject, message, 'sambolu009@gmail.com',[order.email])


            # generate your pdf
            html = render_to_string('orders/order/pdf.html',{
                'order':order
            })
            out = BytesIO()
            stylesheets = [weasyprint.CSS(settings.STATIC_ROOT + 'css/pdf.css')]
            weasyprint.HTML(string=html).write_pdf(out, stylesheets=stylesheets)

            # attach the pdf file to the email
            email.attach('order_{}.pdf'.format(order.id), out.getvalue(), 'application/pdf')

            #send email
            email.send()

            return redirect('payment:done')

        else:
            return redirect('payment:cancelled')
        
    else:
        #generate token
        token = braintree.ClientToken.generate()

        return render(request, 'payment/process.html',{
            'order':order,
            'client_token':token
        })


def payment_done(request):
    return render(request, 'payment/done.html')

def payment_cancelled(request):
    return render(request, 'payment/cancelled.html')


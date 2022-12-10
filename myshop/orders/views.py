

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from cart.cart import Cart
from .forms import OrderCreateForm
from .models import OrderItem, Order
from .tasks import order_created
from django.contrib.admin.views.decorators import staff_member_required
from django.template.loader import render_to_string
from django.conf import settings
from django.http import HttpResponse
from decimal import  Decimal
import weasyprint


# Create your views here.
def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if cart.coupon:
                order.coupon = cart.coupon
                order.discount = cart.coupon.discount
            order.save()
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product = item['product'],
                    quantity = item['quantity'], 
                    price = item['price']
                )
            cart.clear()
            # launch asynchronous task
            order_created.delay(order.id)
            # start a session for payment
            request.session['order_id'] = order.id

            # redirect to a payment gateway
            return redirect(reverse("payment:process"))

            ''' return render(request, 'orders/order/created.html',{
                'order':order
            })'''
            
        
    else:
        form = OrderCreateForm()
    
    return render(request, 'orders/order/create.html',{
        'cart':cart, 
        'form':form
    })

@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'admin/orders/order/detail.html',{
        'order':order
    })


@staff_member_required
def admin_order_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    total_cost = sum(Decimal(item.get_cost()) for item in order.items.all()) 
    if order.coupon:
        coupon = total_cost - order.get_total_cost()
        
    html = render_to_string('orders/order/pdf.html',
    {'order':order,'coupon':coupon, 'total_cost':total_cost})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename=\
        "order_{}.pdf"'.format(order.id)

    weasyprint.HTML(string=html).write_pdf(response,
    stylesheets=[weasyprint.CSS(settings.STATIC_ROOT + 'css/pdf.css')])

    return response
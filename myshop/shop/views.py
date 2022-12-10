from django.shortcuts import render, get_object_or_404
from .models import Category, Product
from cart.forms import CartAddProductForm

# Create your views here.
def product_list(request, category_slug = None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    template_name = "shop/product/list.html"
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=category)
    
    return render(request, template_name, {
        "categories":categories,
        "category":category,
        "products":products
    })


def product_detail(request, id, slug):
    template_name = 'shop/product/detail.html'
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    cart_product_form = CartAddProductForm()

    return render(request, template_name, {
        "product":product,
        'cart_product_form':cart_product_form
    })


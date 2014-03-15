from django.shortcuts import render
from django.views.decorators.http import require_safe

from shame.models import Product

def price(price):
    return '${:,.2f}'.format(price/100.0)

@require_safe
def index(request):
    products = [
        { 'name': product.name,
          'sku': product.sku,
          'price': price(product.price) }
        for product in
        Product.objects.filter(store=request.store)]
    return render(request, 'products.html', { 'products': products })

@require_safe
def detail(request, sku):
    product = Product.objects.get(sku=sku)
    return render(
        request,
        'detail.html',
        { 'product': { 'name': product.name, 'price': price(product.price) } })

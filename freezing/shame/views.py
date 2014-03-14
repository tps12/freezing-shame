from django.shortcuts import render

from shame.models import Product

def index(request):
    products = [
        { 'name': product.name,
          'price': '${:,.2f}'.format(product.price/100.0) }
        for product in
        Product.objects.filter(store=request.store)]
    return render(request, 'products.html', { 'products': products })

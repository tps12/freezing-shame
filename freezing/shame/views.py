from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods, require_safe

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
        { 'product': {
            'name': product.name,
            'sku': product.sku,
            'price': price(product.price) } })

@require_http_methods(['GET','HEAD','POST'])
def cart(request):
    if request.method == 'POST':
        try:
            product = Product.objects.get(
                store=request.store, sku=request.POST['sku'])
        except (KeyError, Product.DoesNotExist):
            return HttpResponse('Must specify valid product', status=400)

        cart = request.session['cart'] if 'cart' in request.session else {}
        basket = request.store.subdomain
        sku = product.sku
        if basket not in cart:
            cart[basket] = {}
        if sku not in cart[basket]:
            cart[basket][sku] = 0
        cart[basket][sku] += 1
        request.session['cart'] = cart

        return redirect('shame.views.index')
    else:
        try:
            cart = request.session['cart'][request.store.subdomain]
        except KeyError:
            cart = {}
        products = { product.sku: product for product in
                     Product.objects.filter(sku__in=cart.keys()) }
        basket = cart.items()
        contents = [{ 'name': products[sku].name,
                      'ea': products[sku].price,
                      'quantity': quantity }
                    for (sku, quantity) in basket]
        return render(
            request,
            'cart.html',
            { 'cart': {
                'contents': [{ 'name': item['name'],
                               'quantity': item['quantity'],
                               'ea': price(item['ea']),
                               'total': price(item['quantity'] * item['ea']) }
                             for item in contents],
                'total': price(sum([item['quantity'] * item['ea']
                                    for item in contents])) } })

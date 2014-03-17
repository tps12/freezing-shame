from urllib.parse import urlencode

from django.core.urlresolvers import reverse
from django.db.utils import IntegrityError
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template import loader
from django.views.decorators.http import require_http_methods, require_POST, require_safe

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from shame.models import price, LineItem, Order, Product

def renderwithstoretemplate(request, *args, **kwargs):
    if len(args) > 0:
        args = (('{};{}'.format(request.store, args[0]), args[0]),) + args[1:]
    return render(request, *args, **kwargs)

@require_safe
def index(request):
    products = [
        { 'name': product.name,
          'sku': product.sku,
          'price': price(product.price) }
        for product in
        Product.objects.filter(store=request.store)]
    try:
        cartsize = sum(
            request.session['cart'][request.store.subdomain].values())
    except KeyError:
        cartsize = 0
    return renderwithstoretemplate(
        request,
        'products.html',
        { 'products': products, 'cartsize': cartsize })

@require_safe
def detail(request, sku):
    product = Product.objects.get(sku=sku)
    return renderwithstoretemplate(
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
        return renderwithstoretemplate(
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

@login_required
@require_http_methods(['GET','HEAD','POST'])
def checkout(request):
    if request.method == 'POST':
        try:
            carts = request.session['cart']
        except KeyError:
            carts = {}
        try:
            cart = carts[request.store.subdomain]
            del carts[request.store.subdomain]
        except KeyError:
            cart = {}
        if len(cart) == 0:
            return HttpResponse('No items in cart', status=400)
        order = Order.objects.create(store=request.store, user=request.user)
        prices = { product.sku: product.price for product in
                   Product.objects.filter(sku__in=cart.keys()) }
        for sku, quantity in cart.items():
            for _ in range(quantity):
                LineItem.objects.create(order=order, sku=sku, price=prices[sku])
        request.session['cart'] = carts
        return redirect('shame.views.index')
    else:
        return redirect('shame.views.cart')

@require_POST
def logoff(request):
    logout(request)
    return redirect('shame.views.index')

@require_http_methods(['GET','HEAD','POST'])
def register(request):
    if request.method == 'POST':
        username, password = request.POST['username'], request.POST['password']
        try:
            if len(password) == 0:
                raise ValueError('Must provide password')
            User.objects.create_user(username, password=password)
        except ValueError as e:
            return HttpResponse(e, status=400)
        except IntegrityError:
            return redirect('?'.join((
                reverse('django.contrib.auth.views.login'),
                urlencode({
                    'username': username,
                    'next': request.POST['next'] }))))
        login(request, authenticate(username=username, password=password))
        return redirect(request.POST['next'])
    else:
        try:
            next = request.GET['next']
        except KeyError:
            next = None
        return renderwithstoretemplate(
            request,
            'registration/register.html',
            { 'next': next } if next else {})

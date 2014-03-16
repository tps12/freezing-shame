from django.test import TestCase

class CheckoutTest(TestCase):
    from django.test.client import Client
    Client = staticmethod(Client)

    from django.contrib.auth.models import User
    User = staticmethod(User)

    from shame.models import Store
    Store = staticmethod(Store)

    from shame.models import Product
    Product = staticmethod(Product)

    from shame.models import Order
    Order = staticmethod(Order)

    from shame.models import LineItem
    LineItem = staticmethod(LineItem)

    def test_requireslogin(self):
        store = self.Store(subdomain='the-store')
        store.save()

        product = self.Product(store=store, name='Thingy', price=123)
        product.save()

        client = self.Client()
        client.post(
            '/cart',
            { 'sku': product.sku },
            HTTP_HOST='the-store.example.biz')

        response = client.post('/checkout', HTTP_HOST='the-store.example.biz')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login', response['location'])

    def test_createsorder(self):
        store = self.Store(subdomain='the-store')
        store.save()

        product = self.Product(store=store, name='Thingy', price=123)
        product.save()

        client = self.Client()

        client.post(
            '/cart',
            { 'sku': product.sku },
            HTTP_HOST='the-store.example.biz')

        user = self.User.objects.create_user('test', password='secret')
        client.login(username=user.username, password='secret')
        client.post('/checkout', HTTP_HOST='the-store.example.biz')

        order = self.Order.objects.filter(store=store).order_by('-id')[0]
        self.assertEqual(order.user, user)

        from datetime import datetime, timezone
        self.assertAlmostEqual(
            (order.created - datetime.now(timezone.utc)).total_seconds(),
            0,
            places=1)

    def test_orderlines(self):
        store = self.Store(subdomain='the-store')
        store.save()

        a = self.Product(store=store, name='Thing A', price=123)
        a.save()

        b = self.Product(store=store, name='Thing B', price=456)
        b.save()

        client = self.Client()

        for product in a, a, b:
            client.post(
                '/cart',
                { 'sku': product.sku },
                HTTP_HOST='the-store.example.biz')

        user = self.User.objects.create_user('test', password='secret')
        client.login(username=user.username, password='secret')
        client.post('/checkout', HTTP_HOST='the-store.example.biz')

        order = self.Order.objects.filter(store=store).order_by('-id')[0]
        lines = self.LineItem.objects.filter(order=order)
        self.assertEqual(len(lines), 3)
        self.assertIn(a.sku, [line.sku for line in lines])
        self.assertIn(b.sku, [line.sku for line in lines])
        self.assertEqual(
            sum([line.price for line in lines]), 2 * a.price + b.price)

    def test_emptiescart(self):
        store = self.Store(subdomain='the-store')
        store.save()

        product = self.Product(store=store, name='Thingy', price=123)
        product.save()

        client = self.Client()
        user = self.User.objects.create_user('test', password='secret')
        client.login(username=user.username, password='secret')
        client.post(
            '/cart',
            { 'sku': product.sku },
            HTTP_HOST='the-store.example.biz')

        client.post('/checkout', HTTP_HOST='the-store.example.biz')

        response = client.get(
            '/cart',
            HTTP_HOST='the-store.example.biz')
        self.assertNotIn(b'Thingy', response.content)
        self.assertIn(b'$0.00', response.content)

    def test_emptiesstorecartonly(self):
        store1 = self.Store(subdomain='the-store')
        store1.save()

        a = self.Product(store=store1, name='Thing A', price=123)
        a.save()

        store2 = self.Store(subdomain='another-store')
        store2.save()

        b = self.Product(store=store2, name='Thing B', price=456)
        b.save()

        client = self.Client()
        user = self.User.objects.create_user('test', password='secret')
        client.login(username=user.username, password='secret')

        for store, product in (store1, a), (store1, a), (store2, b):
            client.post(
                '/cart',
                { 'sku': product.sku },
                HTTP_HOST='{}.example.biz'.format(store))

        client.post(
            '/cart',
            { 'sku': product.sku },
            HTTP_HOST='the-store.example.biz')

        client.post('/checkout', HTTP_HOST='the-store.example.biz')

        response = client.get(
            '/cart',
            HTTP_HOST='the-store.example.biz')
        self.assertNotIn(b'Thing A', response.content)
        self.assertIn(b'$0.00', response.content)

        response = client.get(
            '/cart',
            HTTP_HOST='another-store.example.biz')
        self.assertNotIn(b'$1.23', response.content)
        self.assertIn(b'$4.56', response.content)

    def test_redirectstoproducts(self):
        store = self.Store(subdomain='the-store')
        store.save()

        product = self.Product(store=store, name='Thingy', price=123)
        product.save()

        client = self.Client()
        user = self.User.objects.create_user('test', password='secret')
        client.login(username=user.username, password='secret')
        client.post(
            '/cart',
            { 'sku': product.sku },
            HTTP_HOST='the-store.example.biz')

        response = client.post('/checkout', HTTP_HOST='the-store.example.biz')

        self.assertEqual(response.status_code, 302)
        self.assertRegex(response['location'], r'the-store.example.biz/$')

    def test_emptycart(self):
        store = self.Store(subdomain='the-store')
        store.save()

        product = self.Product(store=store, name='Thingy', price=123)
        product.save()

        client = self.Client()
        user = self.User.objects.create_user('test', password='secret')
        client.login(username=user.username, password='secret')
        response = client.post(
            '/checkout', HTTP_HOST='the-store.example.biz')
        self.assertEqual(response.status_code, 400)

    def test_getredirects(self):
        store = self.Store(subdomain='the-store')
        store.save()

        product = self.Product(store=store, name='Thingy', price=123)
        product.save()

        client = self.Client()
        user = self.User.objects.create_user('test', password='secret')
        client.login(username=user.username, password='secret')
        response = client.get(
            '/checkout', HTTP_HOST='the-store.example.biz')
        self.assertEqual(response.status_code, 302)
        self.assertRegex(response['location'], r'/cart$')

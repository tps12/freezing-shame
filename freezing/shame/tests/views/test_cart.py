from django.test import TestCase

class CartTest(TestCase):
    from django.test.client import Client
    Client = staticmethod(Client)

    from shame.models import Store
    Store = staticmethod(Store)

    from shame.models import Product
    Product = staticmethod(Product)

    def test_addtocart(self):
        store = self.Store(subdomain='the-store')
        store.save()

        product = self.Product(store=store, name='Thingy', price=123)
        product.save()

        response = self.Client().post(
            '/cart',
            { 'sku': product.sku },
            HTTP_HOST='the-store.example.biz')
        self.assertLess(response.status_code, 400)

    def test_addrequiressku(self):
        store = self.Store(subdomain='the-store')
        store.save()

        product = self.Product(store=store, name='Thingy', price=123)
        product.save()

        response = self.Client().post(
            '/cart',
            { 'notasku': product.sku },
            HTTP_HOST='the-store.example.biz')
        self.assertEqual(response.status_code, 400)

    def test_addrequiresvalidsku(self):
        from uuid import uuid4

        store = self.Store(subdomain='the-store')
        store.save()

        product = self.Product(store=store, name='Thingy', price=123)
        product.save()

        response = self.Client().post(
            '/cart',
            { 'sku': uuid4() },
            HTTP_HOST='the-store.example.biz')
        self.assertEqual(response.status_code, 400)

    def test_productinstore(self):
        store = self.Store(subdomain='the-store')
        store.save()

        product = self.Product(store=store, name='Thingy', price=123)
        product.save()

        store = self.Store(subdomain='another-store')
        store.save()

        response = self.Client().post(
            '/cart',
            { 'sku': product.sku },
            HTTP_HOST='another-store.example.biz')
        self.assertEqual(response.status_code, 400)

    def test_showcart(self):
        store = self.Store(subdomain='the-store')
        store.save()

        response = self.Client().get('/cart', HTTP_HOST='the-store.example.biz')
        self.assertEqual(response.status_code, 200)

    def test_hasnewcontents(self):
        store = self.Store(subdomain='the-store')
        store.save()

        product = self.Product(store=store, name='Thingy', price=123)
        product.save()

        client = self.Client()
        client.post(
            '/cart',
            { 'sku': product.sku },
            HTTP_HOST='the-store.example.biz')

        response = client.get(
            '/cart',
            HTTP_HOST='the-store.example.biz')
        self.assertIn(b'Thingy', response.content)

    def test_pricesandtotals(self):
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

        response = client.get(
            '/cart',
            HTTP_HOST='the-store.example.biz')

        self.assertIn(b'$1.23', response.content)
        self.assertIn(b'$2.46', response.content) # == 2 * 1.23

        self.assertIn(b'$4.56', response.content)

        self.assertIn(b'$7.02', response.content) # == 2 * 1.23 + 4.56

    def test_onecartperstore(self):
        store1 = self.Store(subdomain='the-store')
        store1.save()

        a = self.Product(store=store1, name='Thing A', price=123)
        a.save()

        store2 = self.Store(subdomain='another-store')
        store2.save()

        b = self.Product(store=store2, name='Thing B', price=456)
        b.save()

        client = self.Client()

        for store, product in (store1, a), (store1, a), (store2, b):
            client.post(
                '/cart',
                { 'sku': product.sku },
                HTTP_HOST='{}.example.biz'.format(store))

        response = client.get(
            '/cart',
            HTTP_HOST='the-store.example.biz')
        self.assertIn(b'$1.23', response.content)
        self.assertNotIn(b'$4.56', response.content)

        response = client.get(
            '/cart',
            HTTP_HOST='another-store.example.biz')
        self.assertNotIn(b'$1.23', response.content)
        self.assertIn(b'$4.56', response.content)

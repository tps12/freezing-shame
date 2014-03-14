from django.test import TestCase

class StoreTest(TestCase):
    from shame.models import Store
    Store = staticmethod(Store)

    def test_str(self):
        self.assertEqual(str(self.Store(subdomain='whatever')), 'whatever')

class IndexTest(TestCase):
    from django.test.client import Client
    Client = staticmethod(Client)

    from shame.models import Store
    Store = staticmethod(Store)

    from shame.models import Product
    Product = staticmethod(Product)

    def test_products(self):
        store = self.Store(subdomain='the-store')
        store.save()

        product = self.Product(store=store, name='Thingy', price=123)
        product.save()

        response = self.Client().get('/', HTTP_HOST='the-store.example.biz')
        self.assertIn(b'Thingy', response.content)
        self.assertIn(b'$1.23', response.content)

class SubdomainTest(TestCase):
    from shame.models import Store
    Store = staticmethod(Store)

    from shame.middleware import Subdomain
    Subdomain = staticmethod(Subdomain)

    def test_setsubdomain(self):
        store = self.Store(subdomain='wherever')
        store.save()
        class Request(object):
            def __init__(self):
                self.META = { 'HTTP_HOST': 'wherever.example.biz' }
        request = Request()
        self.Subdomain().process_request(request)
        self.assertEqual(request.store, store)

    def test_subdomainnotfound(self):
        self.Store.objects.all().delete()
        class Request(object):
            def __init__(self):
                self.META = { 'HTTP_HOST': 'wherever.example.biz' }
        request = Request()
        self.Subdomain().process_request(request)
        self.assertIsNone(request.store)

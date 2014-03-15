from django.test import TestCase

class IndexTest(TestCase):
    from django.test.client import Client
    Client = staticmethod(Client)

    from shame.models import Store
    Store = staticmethod(Store)

    from shame.models import Product
    Product = staticmethod(Product)

    from xml.etree import ElementTree
    ElementTree = staticmethod(ElementTree)

    def test_products(self):
        store = self.Store(subdomain='the-store')
        store.save()

        product = self.Product(store=store, name='Thingy', price=123)
        product.save()

        response = self.Client().get('/', HTTP_HOST='the-store.example.biz')
        self.assertIn(b'Thingy', response.content)
        self.assertIn(b'$1.23', response.content)

    def test_linktoproduct(self):
        store = self.Store(subdomain='the-store')
        store.save()

        product = self.Product(store=store, name='Thingy', price=123)
        product.save()

        response = self.Client().get('/', HTTP_HOST='the-store.example.biz')
        for a in self.ElementTree.fromstring(response.content).iter('a'):
            if a.attrib['href'].endswith(product.sku):
                break
        else:
            self.fail()

    def test_product(self):
        store = self.Store(subdomain='the-store')
        store.save()

        product = self.Product(store=store, name='Thingy', price=123)
        product.save()

        response = self.Client().get(
            '/' + product.sku, HTTP_HOST='the-store.example.biz')
        self.assertIn(b'Thingy', response.content)
        self.assertIn(b'$1.23', response.content)

from django.test import TestCase

class ProductTest(TestCase):
    from django.test.client import Client
    Client = staticmethod(Client)

    from shame.models import Store
    Store = staticmethod(Store)

    from shame.models import Product
    Product = staticmethod(Product)

    from xml.etree import ElementTree
    ElementTree = staticmethod(ElementTree)

    def test_product(self):
        store = self.Store(subdomain='the-store')
        store.save()

        product = self.Product(store=store, name='Thingy', price=123)
        product.save()

        response = self.Client().get(
            '/' + product.sku, HTTP_HOST='the-store.example.biz')
        self.assertIn(b'Thingy', response.content)
        self.assertIn(b'$1.23', response.content)

    def test_cantpost(self):
        store = self.Store(subdomain='the-store')
        store.save()

        product = self.Product(store=store, name='Thingy', price=123)
        product.save()

        response = self.Client().post(
            '/' + product.sku, HTTP_HOST='the-store.example.biz')
        self.assertEqual(response.status_code, 405)

    def test_addbutton(self):
        store = self.Store(subdomain='the-store')
        store.save()

        product = self.Product(store=store, name='Thingy', price=123)
        product.save()

        response = self.Client().get(
            '/' + product.sku, HTTP_HOST='the-store.example.biz')
        for form in self.ElementTree.fromstring(response.content).iter('form'):
            if form.attrib['action'].endswith('/cart'):
                self.assertEqual(form.attrib['method'], 'POST')
                break
        else:
            self.fail()

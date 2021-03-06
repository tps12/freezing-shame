from django.test import TestCase

class ProductsTest(TestCase):
    from django.test.client import Client
    Client = staticmethod(Client)

    from django.contrib.auth.models import User
    User = staticmethod(User)

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

    def test_cantpost(self):
        store = self.Store(subdomain='the-store')
        store.save()

        response = self.Client().post('/', HTTP_HOST='the-store.example.biz')
        self.assertEqual(response.status_code, 405)

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

    def test_emptycart(self):
        store = self.Store(subdomain='the-store')
        store.save()

        response = self.Client().get('/', HTTP_HOST='the-store.example.biz')
        self.assertNotIn(b'Checkout', response.content)

    def test_linktocart(self):
        store = self.Store(subdomain='the-store')
        store.save()

        product = self.Product(store=store, name='Thingy', price=123)
        product.save()

        client = self.Client()
        client.post(
            '/cart',
            { 'sku': product.sku },
            HTTP_HOST='the-store.example.biz')

        response = client.get('/', HTTP_HOST='the-store.example.biz')
        for a in self.ElementTree.fromstring(response.content).iter('a'):
            if a.attrib['href'].endswith('/cart'):
                self.assertIn('Checkout', a.text)
                break
        else:
            self.fail()

    def test_loggedin(self):
        store = self.Store(subdomain='the-store')
        store.save()

        product = self.Product(store=store, name='Thingy', price=123)
        product.save()

        client = self.Client()
        user = self.User.objects.create_user('test', password='secret')
        client.login(username=user.username, password='secret')

        response = client.get('/', HTTP_HOST='the-store.example.biz')
        for form in self.ElementTree.fromstring(response.content).iter('form'):
            if form.attrib['action'].endswith('/accounts/logout/'):
                self.assertEqual(form.attrib['method'], 'POST')
                break
        else:
            self.fail()

    def test_loggedout(self):
        store = self.Store(subdomain='the-store')
        store.save()

        product = self.Product(store=store, name='Thingy', price=123)
        product.save()

        self.User.objects.create_user('test', password='secret')

        response = self.Client().get('/', HTTP_HOST='the-store.example.biz')
        for form in self.ElementTree.fromstring(response.content).iter('form'):
            if form.attrib['action'].endswith('/logout'):
                self.fail()

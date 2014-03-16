from django.test import TestCase

class RegisterTest(TestCase):
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

    def test_linkstologin(self):
        store = self.Store(subdomain='the-store')
        store.save()

        response = self.Client().get(
            '/accounts/register/',
            { 'next': '/wherever' },
            HTTP_HOST='the-store.example.biz')

        for a in self.ElementTree.fromstring(response.content).iter('a'):
            if '/accounts/login' in a.attrib['href']:
                self.assertIn('next=/wherever', a.attrib['href'])
                break
        else:
            self.fail()

    def test_usernamepassword(self):
        store = self.Store(subdomain='the-store')
        store.save()

        response = self.Client().get(
            '/accounts/register/',
            { 'next': '/somewhere' },
            HTTP_HOST='the-store.example.biz')

        for form in self.ElementTree.fromstring(response.content).iter('form'):
            if form.attrib['action'].endswith('/accounts/register/'):
                inputs = { input.attrib['name']: input
                           for input in form.iter('input')
                           if 'name' in input.attrib }
                self.assertIn('username', inputs)
                self.assertIn('password', inputs)
                break
        else:
            self.fail()

    def test_next(self):
        store = self.Store(subdomain='the-store')
        store.save()

        response = self.Client().get(
            '/accounts/register/',
            { 'next': '/somewhere' },
            HTTP_HOST='the-store.example.biz')

        for form in self.ElementTree.fromstring(response.content).iter('form'):
            if form.attrib['action'].endswith('/accounts/register/'):
                inputs = { input.attrib['name']: input
                           for input in form.iter('input')
                           if 'name' in input.attrib }
                self.assertEqual(inputs['next'].attrib['value'], '/somewhere')
                break
        else:
            self.fail()

    def test_postaction(self):
        store = self.Store(subdomain='the-store')
        store.save()

        response = self.Client().get(
            '/accounts/register/',
            { 'next': '/somewhere' },
            HTTP_HOST='the-store.example.biz')

        for form in self.ElementTree.fromstring(response.content).iter('form'):
            if form.attrib['action'].endswith('/accounts/register/'):
                self.assertEqual(form.attrib['method'], 'POST')
                break
        else:
            self.fail()

    def test_redirect(self):
        store = self.Store(subdomain='the-store')
        store.save()

        response = self.Client().post(
            '/accounts/register/',
            { 'username': 'bob',
              'password': 'something',
              'next': '/somewhere' },
            HTTP_HOST='the-store.example.biz')

        self.assertEqual(response.status_code, 302)
        self.assertRegex(response['location'], r'/somewhere$')

    def test_createsuser(self):
        store = self.Store(subdomain='the-store')
        store.save()

        response = self.Client().post(
            '/accounts/register/',
            { 'username': 'bob',
              'password': 'something',
              'next': '/somewhere' },
            HTTP_HOST='the-store.example.biz')

        self.assertIsNotNone(self.User.objects.get(username='bob'))

    def test_logsin(self):
        store = self.Store(subdomain='the-store')
        store.save()

        client = self.Client()
        client.post(
            '/accounts/register/',
            { 'username': 'bob',
              'password': 'something',
              'next': '/somewhere' },
            HTTP_HOST='the-store.example.biz')

        response = client.post('/checkout', HTTP_HOST='the-store.example.biz')
        self.assertNotEqual(response.status_code, 302)

    def test_invalidusername(self):
        store = self.Store(subdomain='the-store')
        store.save()

        client = self.Client()
        response = client.post(
            '/accounts/register/',
            { 'username': '',
              'password': 'something',
              'next': '/somewhere' },
            HTTP_HOST='the-store.example.biz')

        self.assertEqual(response.status_code, 400)

    def test_invalidpassword(self):
        store = self.Store(subdomain='the-store')
        store.save()

        client = self.Client()
        response = client.post(
            '/accounts/register/',
            { 'username': 'bob',
              'password': '',
              'next': '/somewhere' },
            HTTP_HOST='the-store.example.biz')

        self.assertEqual(response.status_code, 400)

    def test_exists(self):
        store = self.Store(subdomain='the-store')
        store.save()

        self.User.objects.create_user('bob')

        client = self.Client()
        response = client.post(
            '/accounts/register/',
            { 'username': 'bob',
              'password': 'secret',
              'next': '/somewhere' },
            HTTP_HOST='the-store.example.biz')

        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response['location'])
        self.assertRegex(response['location'], r'next=.*somewhere')
        self.assertIn('username=bob', response['location'])

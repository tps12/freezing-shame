from django.test import TestCase

class AdminTest(TestCase):
    from django.test.client import Client
    Client = staticmethod(Client)

    from django.contrib.auth.models import User
    User = staticmethod(User)

    from shame.models import LineItem
    LineItem = staticmethod(LineItem)

    from shame.models import Order
    Order = staticmethod(Order)

    from shame.models import Product
    Product = staticmethod(Product)

    from shame.models import Store
    Store = staticmethod(Store)

    from shame.models import StoreOwner
    StoreOwner = staticmethod(StoreOwner)

    from xml.etree import ElementTree
    ElementTree = staticmethod(ElementTree)

    # hack to parse non-XML
    @staticmethod
    def cleanentities(content):
        from functools import reduce
        return reduce(
            lambda content, mapping: content.replace(*mapping),
            {
                b'&nbsp;': b' ',
                b'&rsaquo;': b"'",
            }.items(),
            content)

    def test_superuserauth(self):
        user = self.User.objects.create_superuser(
            'test', 'root@localhost', 'secret')

        client = self.Client()
        client.login(username=user.username, password='secret')

        response = client.get('/admin/', HTTP_HOST='example.biz')
        for a in self.ElementTree.fromstring(response.content).iter('a'):
            if a.attrib['href'].endswith('/admin/auth/'):
                break
        else:
            self.fail()

    def test_superuserstores(self):
        store = self.Store.objects.create(subdomain='the-store')

        store = self.Store.objects.create(subdomain='another-store')

        user = self.User.objects.create_superuser(
            'test', 'root@localhost', 'secret')

        client = self.Client()
        client.login(username=user.username, password='secret')

        response = client.get('/admin/shame/store/', HTTP_HOST='example.biz')
        content = self.cleanentities(response.content)
        links = {}
        for tr in self.ElementTree.fromstring(content).iter('tr'):
            for a in tr.iter('a'):
                links[a.text] = a.attrib['href']
        self.assertIn('the-store', links)
        self.assertIn('another-store', links)

    def test_superuserproducts(self):
        store1 = self.Store.objects.create(subdomain='the-store')

        a = self.Product.objects.create(store=store1, name='Thing A', price=123)

        store2 = self.Store.objects.create(subdomain='another-store')

        b = self.Product.objects.create(store=store2, name='Thing B', price=456)

        user = self.User.objects.create_superuser(
            'test', 'root@localhost', 'secret')

        client = self.Client()
        client.login(username=user.username, password='secret')

        response = client.get('/admin/shame/product/', HTTP_HOST='example.biz')
        content = self.cleanentities(response.content)
        links = {}
        for tr in self.ElementTree.fromstring(content).iter('tr'):
            for a in tr.iter('a'):
                links[a.text] = a.attrib['href']
        self.assertIn('Thing A', links)
        self.assertIn('Thing B', links)

    def test_superuserorders(self):
        store1 = self.Store.objects.create(subdomain='the-store')

        customer = self.User.objects.create_user('customer')

        order1 = self.Order.objects.create(store=store1, user=customer)

        store2 = self.Store.objects.create(subdomain='another-store')

        order2 = self.Order.objects.create(store=store2, user=customer)

        user = self.User.objects.create_superuser(
            'test', 'root@localhost', 'secret')

        client = self.Client()
        client.login(username=user.username, password='secret')

        response = client.get('/admin/shame/order/', HTTP_HOST='example.biz')
        content = self.cleanentities(response.content)
        links = []
        for tr in self.ElementTree.fromstring(content).iter('tr'):
            for a in tr.iter('a'):
                links.append(a.attrib['href'])
        self.assertIn('/admin/shame/order/{}/'.format(order1.id), links)
        self.assertIn('/admin/shame/order/{}/'.format(order2.id), links)

    def test_superuserordercontents(self):
        store1 = self.Store.objects.create(subdomain='the-store')

        customer = self.User.objects.create_user('customer')

        order1 = self.Order.objects.create(store=store1, user=customer)

        for _ in range(3):
            self.LineItem.objects.create(order=order1, sku='hi', price=123)

        store2 = self.Store.objects.create(subdomain='another-store')

        order2 = self.Order.objects.create(store=store2, user=customer)

        for _ in range(5):
            self.LineItem.objects.create(order=order2, sku='hi', price=123)

        user = self.User.objects.create_superuser(
            'test', 'root@localhost', 'secret')

        client = self.Client()
        client.login(username=user.username, password='secret')

        response = client.get('/admin/shame/lineitem/', HTTP_HOST='example.biz')
        content = self.cleanentities(response.content)
        links = []
        for tr in self.ElementTree.fromstring(content).iter('tr'):
            for a in tr.iter('a'):
                links.append(a.attrib['href'])
        self.assertEqual(len(links), 3 + 5)

    def test_ownernoauth(self):
        store = self.Store.objects.create(subdomain='the-store')

        user = self.StoreOwner.objects.create_admin(
            'test', store, password='secret')

        client = self.Client()
        client.login(username=user.username, password='secret')

        response = client.get('/admin/', HTTP_HOST='example.biz')
        self.assertEqual(response.status_code, 200)
        for a in self.ElementTree.fromstring(response.content).iter('a'):
            if a.attrib['href'].endswith('/admin/auth/'):
                self.fail()

    def test_ownerstores(self):
        store = self.Store.objects.create(subdomain='the-store')

        store = self.Store.objects.create(subdomain='another-store')

        user = self.StoreOwner.objects.create_admin(
            'test', store, password='secret')

        client = self.Client()
        client.login(username=user.username, password='secret')

        response = client.get('/admin/shame/store/', HTTP_HOST='example.biz')
        content = self.cleanentities(response.content)
        links = {}
        for tr in self.ElementTree.fromstring(content).iter('tr'):
            for a in tr.iter('a'):
                links[a.text] = a.attrib['href']
        self.assertNotIn('the-store', links)
        self.assertIn('another-store', links)

    def test_ownerproducts(self):
        store1 = self.Store.objects.create(subdomain='the-store')

        a = self.Product.objects.create(store=store1, name='Thing A', price=123)

        store2 = self.Store.objects.create(subdomain='another-store')

        b = self.Product.objects.create(store=store2, name='Thing B', price=456)

        user = self.StoreOwner.objects.create_admin(
            'test', store1, password='secret')

        client = self.Client()
        client.login(username=user.username, password='secret')

        response = client.get('/admin/shame/product/', HTTP_HOST='example.biz')
        content = self.cleanentities(response.content)
        links = {}
        for tr in self.ElementTree.fromstring(content).iter('tr'):
            for a in tr.iter('a'):
                links[a.text] = a.attrib['href']
        self.assertIn('Thing A', links)
        self.assertNotIn('Thing B', links)

    def test_ownerorders(self):
        store1 = self.Store.objects.create(subdomain='the-store')

        customer = self.User.objects.create_user('customer')

        order1 = self.Order.objects.create(store=store1, user=customer)

        store2 = self.Store.objects.create(subdomain='another-store')

        order2 = self.Order.objects.create(store=store2, user=customer)

        user = self.StoreOwner.objects.create_admin(
            'test', store1, password='secret')

        client = self.Client()
        client.login(username=user.username, password='secret')

        response = client.get('/admin/shame/order/', HTTP_HOST='example.biz')
        content = self.cleanentities(response.content)
        links = []
        for tr in self.ElementTree.fromstring(content).iter('tr'):
            for a in tr.iter('a'):
                links.append(a.attrib['href'])
        self.assertIn('/admin/shame/order/{}/'.format(order1.id), links)
        self.assertNotIn('/admin/shame/order/{}/'.format(order2.id), links)

    def test_ownerordercontents(self):
        store1 = self.Store.objects.create(subdomain='the-store')

        customer = self.User.objects.create_user('customer')

        order1 = self.Order.objects.create(store=store1, user=customer)

        for _ in range(3):
            self.LineItem.objects.create(order=order1, sku='hi', price=123)

        store2 = self.Store.objects.create(subdomain='another-store')

        order2 = self.Order.objects.create(store=store2, user=customer)

        for _ in range(5):
            self.LineItem.objects.create(order=order2, sku='hi', price=123)

        user = self.StoreOwner.objects.create_admin(
            'test', store1, password='secret')

        client = self.Client()
        client.login(username=user.username, password='secret')

        response = client.get('/admin/shame/lineitem/', HTTP_HOST='example.biz')
        content = self.cleanentities(response.content)
        links = []
        for tr in self.ElementTree.fromstring(content).iter('tr'):
            for a in tr.iter('a'):
                links.append(a.attrib['href'])
        self.assertEqual(len(links), 3)

    def test_searchorder(self):
        store = self.Store.objects.create(subdomain='the-store')

        customer = self.User.objects.create_user('customer')

        order = self.Order.objects.create(store=store, user=customer)

        user = self.User.objects.create_superuser(
            'test', 'root@localhost', 'secret')

        client = self.Client()
        client.login(username=user.username, password='secret')

        response = client.get('/admin/shame/order/', HTTP_HOST='example.biz')
        content = self.cleanentities(response.content)
        for input in self.ElementTree.fromstring(content).iter('input'):
            if input.attrib['value'] == 'Search':
                break
        else:
            self.fail()

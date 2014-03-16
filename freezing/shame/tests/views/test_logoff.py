from django.test import TestCase

class LogoffTest(TestCase):
    from django.test.client import Client
    Client = staticmethod(Client)

    from django.contrib.auth.models import User
    User = staticmethod(User)

    from shame.models import Store
    Store = staticmethod(Store)

    def test_redirect(self):
        store = self.Store(subdomain='the-store')
        store.save()

        client = self.Client()
        user = self.User.objects.create_user('test', password='secret')
        client.login(username=user.username, password='secret')
        response = client.post(
            '/accounts/logout/',
            HTTP_HOST='the-store.example.biz')
        self.assertEqual(response.status_code, 302)
        self.assertRegex(response['location'], r'example.biz/$')

    def test_logsout(self):
        store = self.Store(subdomain='the-store')
        store.save()

        client = self.Client()
        user = self.User.objects.create_user('test', password='secret')
        client.login(username=user.username, password='secret')
        response = client.post(
            '/accounts/logout/',
            HTTP_HOST='the-store.example.biz')

        response = client.get('/', HTTP_HOST='the-store.example.biz')
        self.assertNotIn(b'Logout', response.content)

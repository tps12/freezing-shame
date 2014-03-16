from django.test import TestCase

class LoginTest(TestCase):
    from django.test.client import Client
    Client = staticmethod(Client)

    from shame.models import Store
    Store = staticmethod(Store)

    from xml.etree import ElementTree
    ElementTree = staticmethod(ElementTree)

    def test_linkstoregister(self):
        store = self.Store(subdomain='the-store')
        store.save()

        response = self.Client().get(
            '/accounts/login/',
            { 'next': '/wherever' },
            HTTP_HOST='the-store.example.biz')

        for a in self.ElementTree.fromstring(response.content).iter('a'):
            if '/accounts/register' in a.attrib['href']:
                self.assertIn('next=/wherever', a.attrib['href'])
                break
        else:
            self.fail()

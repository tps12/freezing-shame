from django.test import TestCase

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

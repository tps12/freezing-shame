from django.test import TestCase

class StoreTest(TestCase):
    from shame.models import Store
    Store = staticmethod(Store)

    def test_str(self):
        self.assertEqual(str(self.Store(subdomain='whatever')), 'whatever')

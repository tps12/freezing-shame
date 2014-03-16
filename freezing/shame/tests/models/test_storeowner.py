from django.test import TestCase

from shame.models import Store, StoreOwner

class StoreOwnerTest(TestCase):
    def test_storerequired(self):
        with self.assertRaises(ValueError):
            StoreOwner.objects.create_admin('someone', None)

    def test_staff(self):
        store = Store.objects.create()
        admin = StoreOwner.objects.create_admin('someone', store)
        self.assertTrue(admin.is_staff)

    def test_notsuperuser(self):
        store = Store.objects.create()
        admin = StoreOwner.objects.create_admin('someone', store)
        self.assertFalse(admin.is_superuser)

    def test_str(self):
        store = Store.objects.create(subdomain='whatever')
        admin = StoreOwner.objects.create_admin('someone', store)
        self.assertIn('whatever', str(admin))
        self.assertIn('someone', str(admin))

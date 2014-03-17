from django.test import TestCase

from django.core.exceptions import ValidationError

class StoreTest(TestCase):
    from shame.models import Store
    Store = staticmethod(Store)

    def test_legalsubdomain(self):
        with self.assertRaises(ValidationError):
            self.Store(subdomain="louie's").full_clean()
        with self.assertRaises(ValidationError):
            self.Store(subdomain="a space").full_clean()
        with self.assertRaises(ValidationError):
            self.Store(subdomain="-leading").full_clean()
        with self.assertRaises(ValidationError):
            self.Store(subdomain="trailing-").full_clean()
        self.Store(subdomain="legal-domain").full_clean()

    def test_str(self):
        self.assertEqual(str(self.Store(subdomain='whatever')), 'whatever')

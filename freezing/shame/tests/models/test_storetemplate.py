from django.test import TestCase

from django.core.exceptions import ValidationError

from shame.models import Store, StoreTemplate

class StoreTemplateTest(TestCase):

    def test_legaltemplate(self):
        store = Store.objects.create(subdomain='test')
        with self.assertRaises(ValidationError):
            StoreTemplate(
                store=store, name='something.html', content='something'
                ).full_clean()
        with self.assertRaises(ValidationError):
            StoreTemplate(
                store=store, name='somewhere/base.html', content='something'
                ).full_clean()
        for template in ['base.html', 'detail.html', 'cart.html',
                'products.html', 'registration/login.html',
                'registration/register.html']:
            StoreTemplate(
                store=store, name=template, content='something'
                ).full_clean()

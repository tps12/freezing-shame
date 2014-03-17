from uuid import uuid4

from django.test import TestCase, RequestFactory

from shame.models import Store, StoreTemplate
from shame.views import renderwithstoretemplate

class RenderWithStoreTemplateTest(TestCase):
    def test_usefile(self):
        request = RequestFactory().get('/some/page')
        request.store = object()

        response = renderwithstoretemplate(
            request,
            'products.html',
            { 'products': [{
                'name': 'thing',
                'sku': uuid4(),
                'price': 'free' }],
              'cartsize': 2 })
        self.assertIn(b'<html>', response.content)

    def test_usefilewhennostore(self):
        StoreTemplate.objects.create(
            store=Store.objects.create(subdomain='test'),
            name='products.html',
            content='empty template')

        request = RequestFactory().get('/some/page')
        request.store = None

        response = renderwithstoretemplate(
            request,
            'products.html',
            { 'products': [{
                'name': 'thing',
                'sku': uuid4(),
                'price': 'free' }],
              'cartsize': 2 })
        self.assertIn(b'<html>', response.content)

    def test_usedbtemplateforstore(self):
        store = Store.objects.create(subdomain='test')
        StoreTemplate.objects.create(
            store=store,
            name='products.html',
            content='empty template')

        request = RequestFactory().get('/some/page')
        request.store = store

        response = renderwithstoretemplate(
            request,
            'products.html',
            { 'products': [{
                'name': 'thing',
                'sku': uuid4(),
                'price': 'free' }],
              'cartsize': 2 })
        self.assertEqual(response.content, b'empty template')

from django.test import TestCase

from django.contrib.auth.models import User

from shame.models import LineItem, Order, Store

class LineItemTest(TestCase):
    def test_str(self):
        order = Order.objects.create(
            user=User.objects.create_user('someone'),
            store=Store.objects.create(subdomain='a-store'))
        item1, item2 = [str(item) for item in (
            order.lineitem_set.create(sku='abc', price=123),
            order.lineitem_set.create(sku='def', price=456))]

        self.assertIn(str(order) + ': 1', item1)
        self.assertIn('abc', item1)
        self.assertIn('$1.23', item1)

        self.assertIn(str(order) + ': 2', item2)
        self.assertIn('def', item2)
        self.assertIn('$4.56', item2)

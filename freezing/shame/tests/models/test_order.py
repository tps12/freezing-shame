from time import strftime

from django.test import TestCase

from django.contrib.auth.models import User

from shame.models import LineItem, Order, Store

class OrderTest(TestCase):
    def test_str(self):
        order = Order.objects.create(
            user=User.objects.create_user('someone'),
            store=Store.objects.create(subdomain='a-store'))
        order.lineitem_set.create(sku='abc', price=123)
        order.lineitem_set.create(sku='def', price=456)
        s = str(order)
        self.assertIn(strftime('%Y%m%d'), s)
        self.assertIn('someone', s)
        self.assertIn('a-store', s)
        self.assertIn('$5.79', s) # 1.23 + 4.56

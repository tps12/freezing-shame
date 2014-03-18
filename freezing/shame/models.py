from os import path, walk
from re import match
from uuid import uuid4

from django.core.validators import RegexValidator
from django.db import models

from django.contrib.auth.models import User, UserManager

def price(price):
    return '${:,.2f}'.format(price/100.0)

class Store(models.Model):
    subdomain = models.CharField(
        max_length=63,
        validators=[
            # allow letters and numbers, and hyphens but only in the middle
            RegexValidator(regex=r'^(?i)[a-z0-9]([-a-z0-9]*[a-z0-9])?$')])

    def __str__(self):
        return self.subdomain

templatedir = path.join('freezing', 'shame', 'templates', '')
class StoreTemplate(models.Model):
    templates = [
        path.join(dir, filename).replace(templatedir, '')
        for dir, _, filenames in walk(templatedir)
        for filename in filenames if match(r'^[^_].*\.html$', filename)]

    store = models.ForeignKey(Store)
    name = models.CharField(
        max_length=255,
        choices=[(t,t) for t in templates])
    content = models.TextField()

    class Meta:
        unique_together = ('store', 'name')

    def __str__(self):
        return '{} {} template'.format(self.store, self.name)

class StoreOwnerManager(UserManager):
    def create_admin(
            self, username, store, email=None, password=None, **extra_fields):
        return self._create_user(
            username, email, password, True, False, store=store,
            **extra_fields)

class StoreOwner(User):
    store = models.ForeignKey(Store)

    objects = StoreOwnerManager()

    def __str__(self):
        return '{} ({} admin)'.format(User.__str__(self), self.store)

class Product(models.Model):
    newsku = lambda: str(uuid4())
    sku = models.CharField(max_length=36, unique=True, default=newsku)
    name = models.CharField(max_length=64)
    price = models.IntegerField()
    store = models.ForeignKey(Store)

    def __str__(self):
        return self.name

class Order(models.Model):
    store = models.ForeignKey(Store)
    user = models.ForeignKey(User)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{:%Y%m%d%H%M%S} {} ({}) {}'.format(
            self.created,
            self.store,
            self.user,
            price(sum([li.price for li in self.lineitem_set.all()])))

class LineItem(models.Model):
    order = models.ForeignKey(Order)
    sku = models.CharField(max_length=36)
    price = models.IntegerField()

    def indexinorder(self):
        i = 0
        for item in self.order.lineitem_set.all():
            if item == self:
                return i
            i += 1
        raise ValueError

    def __str__(self):
        return '{}: {}, {}, {}'.format(
            self.order,
            self.indexinorder() + 1,
            self.sku,
            price(self.price))

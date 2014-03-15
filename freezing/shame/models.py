from uuid import uuid4

from django.db import models

class Store(models.Model):
    subdomain = models.CharField(max_length=63)

    def __str__(self):
        return self.subdomain

class Product(models.Model):
    newsku = lambda: str(uuid4())
    sku = models.CharField(max_length=36, unique=True, default=newsku)
    name = models.CharField(max_length=64)
    price = models.IntegerField()
    store = models.ForeignKey(Store)

    def __str__(self):
        return self.name

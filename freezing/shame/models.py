from django.db import models

class Store(models.Model):
    subdomain = models.CharField(max_length=63)

    def __str__(self):
        return self.subdomain

class Product(models.Model):
    name = models.CharField(max_length=64)
    price = models.IntegerField()
    store = models.ForeignKey(Store)

    def __str__(self):
        return self.name

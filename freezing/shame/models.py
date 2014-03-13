from django.db import models

class Store(models.Model):
    subdomain = models.CharField(max_length=63)

    def __str__(self):
        return self.subdomain

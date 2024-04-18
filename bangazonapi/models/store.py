from django.db import models
from .customer import User


class Store(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name="store")

    @property
    def products_sold(self):
        return self.owner.products.all().count()

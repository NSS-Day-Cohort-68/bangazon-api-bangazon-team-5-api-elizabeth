from django.db import models
from .customer import Customer, User


class Store(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    owner = models.OneToOneField(
        Customer, on_delete=models.CASCADE, related_name="store"
    )

    @property
    def products_sold(self):
        return self.owner.products.all().count()

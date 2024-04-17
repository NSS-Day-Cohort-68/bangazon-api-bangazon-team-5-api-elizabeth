from django.db import models
from bangazonapi.models.customer import Customer
from bangazonapi.models.store import Store


class Favorite(models.Model):

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)

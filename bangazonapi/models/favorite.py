from django.db import models
from bangazonapi.models.customer import User
from bangazonapi.models.store import Store


class Favorite(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)

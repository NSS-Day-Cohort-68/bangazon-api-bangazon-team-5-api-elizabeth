from tokenize import Token
from rest_framework.authtoken.models import Token
import datetime
import json
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from bangazonapi.models.payment import Payment


class PaymentTests(APITestCase):
    def setUp(self) -> None:
        """
        Create a new account and create sample category
        """
        # self.user = User.objects.create_user(
        #     username="steve",
        #     password="Admin8*",
        #     email="steve@stevebrownlee.com",
        #     first_name="Steve",
        #     last_name="Brownlee",
        # )
        # self.token = Token.objects.create(user=self.user)
        url = "/register"
        data = {
            "username": "steve",
            "password": "Admin8*",
            "email": "steve@stevebrownlee.com",
            "address": "100 Infinity Way",
            "phone_number": "555-1212",
            "first_name": "Steve",
            "last_name": "Brownlee",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.user = User.objects.get(username="steve", password="Admin8*")
        self.token = Token.objects.create(user=self.user)

    def test_create_payment_type(self):
        """
        Ensure we can add a payment type for a customer.
        """
        # Add product to order
        url = "/paymenttypes"
        data = {
            "merchant_name": "American Express",
            "account_number": "111-1111-1111",
            "expiration_date": "2024-12-31",
            "create_date": datetime.date.today(),
        }
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.post(url, data, format="json")
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(json_response["merchant_name"], "American Express")
        self.assertEqual(json_response["account_number"], "111-1111-1111")
        self.assertEqual(json_response["expiration_date"], "2024-12-31")
        self.assertEqual(json_response["create_date"], str(datetime.date.today()))

    # TODO: Delete payment type
    def test_delete_payment_type(self):
        payment = Payment.objects.create(
            merchant_name="American Express",
            account_number="111-1111-1111",
            expiration_date="2024-12-31",
        )
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)

        url = reverse("delete-payment", kwargs={"pk": payment.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        with self.assertRaises(Payment.DoesNotExist):
            Payment.objects.get(pk=payment.pk)

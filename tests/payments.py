import datetime
import json
from urllib import response
from rest_framework import status
from rest_framework.test import APITestCase
from bangazonapi.models.payment import Payment


class PaymentTests(APITestCase):
    def setUp(self) -> None:
        """
        Create a new account and create sample category
        """
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
        json_response = json.loads(response.content)
        self.token = json_response["token"]
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

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
    # def test_delete_payment_type(self, request, pk=None):
    #     url = "/delete-payment"
    #     data = {
    #         "merchant_name": "American Express",
    #         "account_number": "111-1111-1111",
    #         "expiration_date": "2024-12-31",
    #     }

    #     try:
    #         payment = Payment.objects.get(pk=pk)
    #         payment.delete()

    #         return Response({}, status=status.HTTP_204_NO_CONTENT)

    #     except Payment.DoesNotExist as ex:
    #         return Response({"message": ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

    #     except Exception as ex:
    #         return Response(
    #             {"message": ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
    #         )

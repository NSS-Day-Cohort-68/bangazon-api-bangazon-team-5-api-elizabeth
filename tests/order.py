import json
from datetime import date, datetime
from rest_framework import status
from rest_framework.test import APITestCase
from django.db import models
import urllib.parse

class OrderTests(APITestCase):
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
        self.customer = json.loads(response.content)
        self.token = json_response["token"]
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Create a product category
        url = "/productcategories"
        data = {"name": "Sporting Goods"}
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        self.category = json.loads(response.content)
        response = self.client.post(url, data, format='json')

        # Create a product
        url = "/products"
        data = { "name": "Kite", "price": 14.99, "quantity": 60, "description": "It flies high", "category_id": 1, "location": "Pittsburgh" }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.post(url, data, format='json')
        self.product = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        

        url = "/paymenttypes"
        data = {
            "name": "Kite",
            "price": 14.99,
            "quantity": 60,
            "description": "It flies high",
            "category_id": 1,
            "location": "Pittsburgh",
        }
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.post(url, data, format="json")
        json_response = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.paymenttype = json.loads(response.content)

        # Create a payment type
        url = "/paymenttypes"

        created = date.today()
        exp = date(created.year + 5, created.month, created.day)

        data = {
            "merchant_name": "Visa",
            "account_number": "testing12345678",
            "expiration_date": exp,
            "create_date": created,
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.paymenttype = json.loads(response.content)

    def test_add_product_to_order(self):
        """
        Ensure we can add a product to an order.
        """
        # Add product to order
        url = "/cart"
        data = {"product_id": 1}
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Get cart and verify product was added
        url = "/cart"
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.get(url, None, format="json")
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json_response["id"], 1)
        self.assertEqual(json_response["size"], 1)
        self.assertEqual(len(json_response["lineitems"]), 1)

    def test_remove_product_from_order(self):
        """
        Ensure we can remove a product from an order.
        """
        # Add product
        self.test_add_product_to_order()

        # Remove product from cart
        url = "/cart/1"
        data = {"product_id": 1}
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.delete(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Get cart and verify product was removed
        url = "/cart"
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.get(url, None, format="json")
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json_response["size"], 0)
        self.assertEqual(len(json_response["lineitems"]), 0)

    # TODO: Complete order by adding payment type

    # TODO: New line item is not added to closed order
    def test_add_item_to_new_open_order(self):
        """
        When the user has no open orders, ensure that a new cart is created when adding the first product rather than associating the product with a previously closed order.
        """

        # Establish authorization for the requests to come
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)

        # Get a product id from the testing database
        url = "/products"
        products_response = self.client.get(url, None, format="json")
        product_list = json.loads(products_response.content)
        product_id = product_list[0]["id"]

        # Add the product to the cart
        url = "/cart"
        product_data = {"product_id": product_id}
        response = self.client.post(url, product_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Get info about the current open cart
        response = self.client.get(url, None, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        cart_with_one_item = json.loads(response.content)
        cart_with_one_item_id = cart_with_one_item["id"]
        self.assertIsNone(cart_with_one_item["payment_type_info"])

        # Add another product to the cart
        response = self.client.post(url, product_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Get info about the current open cart again
        response = self.client.get(url, None, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        cart_with_two_items = json.loads(response.content)
        cart_with_two_items_id = cart_with_two_items["id"]
        self.assertIsNone(cart_with_one_item["payment_type_info"])

        # Verify that the cart id did not change when a second product was added
        self.assertEqual(cart_with_one_item_id, cart_with_two_items_id)

        # Complete the order by adding a payment type
        url = "/orders/" + str(cart_with_one_item_id)
        data = {"payment_type": self.paymenttype["id"]}

        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Try to get the current open order. Expect a 404 because there is no open order.
        url = "/cart"
        response = self.client.get(url, None, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Get all orders and verify that there is 1 order in the testing database
        url = "/orders"
        response = self.client.get(url, None, format="json")
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify that there is only one order
        self.assertEqual(len(json_response), 1)

        # Verify that there are two products on this order
        self.assertEqual(len(json_response[0]["lineitems"]), 2)

        # Verify that the payment info matches the paymenttype created in setUp()
        self.assertEqual(json_response[0]["payment_type_info"], self.paymenttype)

        # Add a product to cart again. This time, expect a new order to be opened.
        url = "/cart"
        response = self.client.post(url, product_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Get info about the current open cart
        response = self.client.get(url, None, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        new_cart_with_one_item = json.loads(response.content)
        new_cart_with_one_item_id = new_cart_with_one_item["id"]
        new_cart_with_one_item_lineitems = new_cart_with_one_item["lineitems"]
        self.assertEqual(len(new_cart_with_one_item_lineitems), 1)

        # Verify that the new cart has no payment type
        self.assertIsNone(new_cart_with_one_item["payment_type_info"])

        # Verify that the first cart and second cart have different id's
        self.assertNotEqual(cart_with_one_item_id, new_cart_with_one_item_id)

        # Get orders and verify that there are now 2 orders in the testing database
        url = "/orders"
        response = self.client.get(url, None, format="json")
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(json_response), 2)
    def test_complete_order(self):
        """
        Ensure we can complete an order by updating the payment.
        """
        # Add product to order
        url = "/cart"
        data = { 'product_id': self.product["id"] }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Get cart and verify product was added
        url = "/cart"
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.get(url, None, format='json')
        self.order = json.loads(response.content)
        json_response = json.loads(response.content)
        

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json_response["id"], 1)
        self.assertEqual(json_response["size"], 1)
        self.assertEqual(len(json_response["lineitems"]), 1)


        # Update order with payment 

        today = str(datetime.date.today())


        url = f"/orders/{self.order["id"]}"
        data = { "payment_type": self.paymenttype["id"]} 
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Get order and verify payment was added
        url = f"/orders/{self.order["id"]}"
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.get(url, None, format='json')
        customer_url = json_response["customer"]
        customer_id = int(urllib.parse.urlparse(customer_url).path.split('/')[-1])
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertEqual(json_response["customer"], self.customer["id"])
        self.assertEqual(customer_id, self.customer["id"])
        self.assertEqual(json_response["created_date"], today)
        self.assertEqual(json_response["payment_type_info"]["id"], self.paymenttype["id"])
        self.assertEqual(json_response["payment_type_info"]["url"], "http://testserver/paymenttypes/1")
        self.assertEqual(json_response["payment_type_info"]["merchant_name"], "American Express")
        self.assertEqual(json_response["payment_type_info"]["account_number"], "111-1111-1111")
        self.assertEqual(json_response["payment_type_info"]["expiration_date"], "2024-12-31")
        self.assertGreaterEqual(json_response["payment_type_info"]["create_date"], today)
        self.assertEqual(json_response["lineitems"][0]["id"],  1)
        self.assertEqual(json_response["lineitems"][0]["product"]["name"],  "Kite")
        self.assertEqual(json_response["lineitems"][0]["product"]["price"],  14.99)
        self.assertEqual(json_response["lineitems"][0]["product"]["quantity"],  60)
        self.assertEqual(json_response["lineitems"][0]["product"]["description"],  "It flies high")
        self.assertEqual(json_response["lineitems"][0]["product"]["category_id"],  self.category["id"])
        self.assertEqual(json_response["lineitems"][0]["product"]["location"],  "Pittsburgh")

    # TODO: New line item is not added to closed order

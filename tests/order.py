import json
from rest_framework import status
from rest_framework.test import APITestCase


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
        self.token = json_response["token"]
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Create a product category
        url = "/productcategories"
        data = {"name": "Sporting Goods"}
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.post(url, data, format="json")

        # Create a product
        url = "/products"
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
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_add_product_to_order(self):
        """
        Ensure we can add a product to an order.
        """
        # Add product to order
        url = "/cart"
        data = {"product_id": 1}
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

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
        When the user has no open orders, ensure that a new order is created when adding the first product rather than associating the product with a previously closed order.
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
        print(response)

        # # Get info about the current open cart
        # response = self.client.get(url, None, format="json")
        # first_cart = json.loads(response.content)
        # first_cart_id = first_cart.id
        # first_cart_lineitems = first_cart.lineitems
        # self.assertEqual(len(first_cart_lineitems), 1)
        # self.assertIsNone(first_cart.payment_type)

        # # Add another product to the cart
        # self.client.post(url, product_data, format="json")

        # # Complete the order

        # # Get orders and verify that len(response) is 1
        # url = "/orders"
        # self.client.credentials(HTTP_AUTHORIZATION="Token" + self.token)
        # response = self.client.get(url, None, format="json")
        # json_response = json.loads(response.content)

        # self.assertEqual(len(json_response), 1)

        # # Add product to order again
        # self.test_add_product_to_order()

        # # Get orders and verify that len(response) is 2
        # response = self.client.get(url, None, format="json")
        # json_response = json.loads(response.content)

        # self.assertEqual(len(json_response), 2)
        # self.assertIsNotNone(json_response[0].payment_type)
        # # Verify that response[1].payment_type is null
        # self.assertIsNone(json_response[1].payment_type)

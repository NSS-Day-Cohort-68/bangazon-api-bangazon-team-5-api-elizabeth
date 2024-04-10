import json
import datetime
from rest_framework import status
from rest_framework.test import APITestCase
from bangazonapi.models.product import Product
from bangazonapi.models.productrating import ProductRating


class ProductTests(APITestCase):
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

        url = "/productcategories"
        data = {"name": "Sporting Goods"}
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)

        response = self.client.post(url, data, format="json")
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(json_response["name"], "Sporting Goods")

        """
        Create test product
        """
        self.product = Product.objects.create(
            name="Test Product",
            price=1000.00,
            quantity=2,
            description="This is a test product",
            category_id=1,
            location="Narnia",
            customer_id=1,
        )

    def test_create_product(self):
        """
        Ensure we can create a new product.
        """
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
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(json_response["name"], "Kite")
        self.assertEqual(json_response["price"], 14.99)
        self.assertEqual(json_response["quantity"], 60)
        self.assertEqual(json_response["description"], "It flies high")
        self.assertEqual(json_response["location"], "Pittsburgh")

    def test_update_product(self):
        """
        Ensure we can update a product.
        """
        self.test_create_product()

        url = "/products/1"
        data = {
            "name": "Kite",
            "price": 24.99,
            "quantity": 40,
            "description": "It flies very high",
            "category_id": 1,
            "created_date": datetime.date.today(),
            "location": "Pittsburgh",
        }
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(url, data, format="json")
        json_response = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json_response["name"], "Kite")
        self.assertEqual(json_response["price"], 24.99)
        self.assertEqual(json_response["quantity"], 40)
        self.assertEqual(json_response["description"], "It flies very high")
        self.assertEqual(json_response["location"], "Pittsburgh")

    def test_get_all_products(self):
        """
        Ensure we can get a collection of products.
        """
        self.test_create_product()
        self.test_create_product()
        self.test_create_product()

        product_count = Product.objects.count()

        url = "/products"

        response = self.client.get(url, None, format="json")
        json_response = json.loads(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(json_response), product_count)

    def test_delete_product(self):
        product = Product.objects.create(
            name="Test Product",
            price=10.00,
            description="Test description",
            quantity=20,
            category_id=1,
            location="Anytown, usa",
            customer_id=1,
        )
        url = f"/products/1"

        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        with self.assertRaises(Product.DoesNotExist):
            Product.objects.get(id=self.product.id)

    # TODO: Product can be rated. Assert average rating exists.

    # def test_avg_rating(self):
    #     self.test_create_product()
    #     url = "/products"
    #     data = {
    #         "name": "Kite",
    #         "price": 14.99,
    #         "quantity": 60,
    #         "description": "It flies high",
    #         "category_id": 1,
    #         "location": "Pittsburgh",
    #     }
    #     response = self.client.post(url, data, format="json")

    # setup - create product

    # can you add a rating to a product?

    # does the avg_rating key exist?

    # does the avg_rating work?

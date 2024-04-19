"""View module for handling requests about products"""

from rest_framework.decorators import action
from bangazonapi.models.recommendation import Recommendation
from bangazonapi.models.productrating import ProductRating
from bangazonapi.models.like import Like
import base64
from django.core.files.base import ContentFile
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from bangazonapi.models import Product, Customer, ProductCategory, Store
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404


class ProductSerializer(serializers.ModelSerializer):
    """JSON serializer for products"""

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "price",
            "number_sold",
            "description",
            "quantity",
            "created_date",
            "location",
            "image_path",
            "average_rating",
            "can_be_rated",
            "customer_id",
            "category_id",
        )
        depth = 1


class ProductLikeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Like

    fields = "liker" "product"
    depth = 1


class Products(ViewSet):
    """Request handlers for Products in the Bangazon Platform"""

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def create(self, request):
        """
        @api {POST} /products POST new product
        @apiName CreateProduct
        @apiGroup Product

        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611

        @apiParam {String} name Short form name of product
        @apiParam {Number} price Cost of product
        @apiParam {String} description Long form description of product
        @apiParam {Number} quantity Number of items to sell
        @apiParam {String} location City where product is located
        @apiParam {Number} category_id Category of product
        @apiParamExample {json} Input
            {
                "name": "Kite",
                "price": 14.99,
                "description": "It flies high",
                "quantity": 60,
                "location": "Pittsburgh",
                "category_id": 4
            }

        @apiSuccess (200) {Object} product Created product
        @apiSuccess (200) {id} product.id Product Id
        @apiSuccess (200) {String} product.name Short form name of product
        @apiSuccess (200) {String} product.description Long form description of product
        @apiSuccess (200) {Number} product.price Cost of product
        @apiSuccess (200) {Number} product.quantity Number of items to sell
        @apiSuccess (200) {Date} product.created_date City where product is located
        @apiSuccess (200) {String} product.location City where product is located
        @apiSuccess (200) {String} product.image_path Path to product image
        @apiSuccess (200) {Number} product.average_rating Average customer rating of product
        @apiSuccess (200) {Number} product.number_sold How many items have been purchased
        @apiSuccess (200) {Object} product.category Category of product
        @apiSuccessExample {json} Success
            {
                "id": 101,
                "url": "http://localhost:8000/products/101",
                "name": "Kite",
                "price": 14.99,
                "number_sold": 0,
                "description": "It flies high",
                "quantity": 60,
                "created_date": "2019-10-23",
                "location": "Pittsburgh",
                "image_path": null,
                "average_rating": 0,
                "category": {
                    "url": "http://localhost:8000/productcategories/6",
                    "name": "Games/Toys"
                }
            }
        """
        try:
            product_category = ProductCategory.objects.get(
                pk=request.data["category_id"]
            )
        except ProductCategory.DoesNotExist:
            return Response()

        customer = Customer.objects.get(user=request.auth.user)

        product_data = {
            "name": request.data["name"],
            "price": request.data["price"],
            "description": request.data["description"],
            "quantity": request.data["quantity"],
            "location": request.data["location"],
            "category": product_category,
            "customer": customer,
        }

        serializer = ProductSerializer(data=product_data, context={"request": request})

        if serializer.is_valid():

            new_product = Product(
                name=serializer.validated_data["name"],
                price=serializer.validated_data["price"],
                description=serializer.validated_data["description"],
                quantity=serializer.validated_data["quantity"],
                location=serializer.validated_data["location"],
                category=product_category,
                customer=customer,
            )

            customer = Customer.objects.get(user=request.auth.user)
            new_product.customer = customer

            new_product.category = product_category

            new_product.save()

            if "image_path" in request.data:
                format, imgstr = request.data["image_path"].split(";base64,")
                ext = format.split("/")[-1]
                data = ContentFile(
                    base64.b64decode(imgstr),
                    name=f'{new_product.id}-{request.data["name"]}.{ext}',
                )

            serializer = ProductSerializer(new_product, context={"request": request})

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """
        @api {GET} /products/:id GET product
        @apiName GetProduct
        @apiGroup Product

        @apiParam {id} id Product Id

        @apiSuccess (200) {Object} product Created product
        @apiSuccess (200) {id} product.id Product Id
        @apiSuccess (200) {String} product.name Short form name of product
        @apiSuccess (200) {String} product.description Long form description of product
        @apiSuccess (200) {Number} product.price Cost of product
        @apiSuccess (200) {Number} product.quantity Number of items to sell
        @apiSuccess (200) {Date} product.created_date City where product is located
        @apiSuccess (200) {String} product.location City where product is located
        @apiSuccess (200) {String} product.image_path Path to product image
        @apiSuccess (200) {Number} product.average_rating Average customer rating of product
        @apiSuccess (200) {Number} product.number_sold How many items have been purchased
        @apiSuccess (200) {Object} product.category Category of product
        @apiSuccessExample {json} Success
            {
                "id": 101,
                "url": "http://localhost:8000/products/101",
                "name": "Kite",
                "price": 14.99,
                "number_sold": 0,
                "description": "It flies high",
                "quantity": 60,
                "created_date": "2019-10-23",
                "location": "Pittsburgh",
                "image_path": null,
                "average_rating": 0,
                "category": {
                    "url": "http://localhost:8000/productcategories/6",
                    "name": "Games/Toys"
                }
            }
        """
        try:
            product = Product.objects.get(pk=pk)
            serializer = ProductSerializer(product, context={"request": request})
            return Response(serializer.data)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def update(self, request, pk=None):
        """
        @api {PUT} /products/:id PUT changes to product
        @apiName UpdateProduct
        @apiGroup Product

        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611

        @apiParam {id} id Product Id to update
        @apiSuccessExample {json} Success
            HTTP/1.1 204 No Content
        """
        product = Product.objects.get(pk=pk)
        product.name = request.data["name"]
        product.price = request.data["price"]
        product.description = request.data["description"]
        product.quantity = request.data["quantity"]
        product.created_date = request.data["created_date"]
        product.location = request.data["location"]

        customer = Customer.objects.get(user=request.auth.user)
        product.customer = customer

        product_category = ProductCategory.objects.get(pk=request.data["category_id"])
        product.category = product_category
        product.save()

        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        """
        @api {DELETE} /products/:id DELETE product
        @apiName DeleteProduct
        @apiGroup Product

        @apiHeader {String} Authorization Auth token
        @apiHeaderExample {String} Authorization
            Token 9ba45f09651c5b0c404f37a2d2572c026c146611

        @apiParam {id} id Product Id to delete
        @apiSuccessExample {json} Success
            HTTP/1.1 204 No Content
        """
        try:
            product = Product.objects.get(pk=pk)
            product.delete()

            return Response({}, status=status.HTTP_204_NO_CONTENT)

        except Product.DoesNotExist as ex:
            return Response({"message": ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response(
                {"message": ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def list(self, request):
        """
        @api {GET} /products GET all products
        @apiName ListProducts
        @apiGroup Product

        @apiSuccess (200) {Object[]} products Array of products
        @apiSuccessExample {json} Success
            [
                {
                    "id": 101,
                    "url": "http://localhost:8000/products/101",
                    "name": "Kite",
                    "price": 14.99,
                    "number_sold": 0,
                    "description": "It flies high",
                    "quantity": 60,
                    "created_date": "2019-10-23",
                    "location": "Pittsburgh",
                    "image_path": null,
                    "average_rating": 0,
                    "category": {
                        "url": "http://localhost:8000/productcategories/6",
                        "name": "Games/Toys"
                    }
                }
            ]
        """
        products = Product.objects.all()

        # Support filtering by category and/or quantity
        category = self.request.query_params.get("category", None)
        quantity = self.request.query_params.get("quantity", None)
        order = self.request.query_params.get("order_by", None)
        direction = self.request.query_params.get("direction", None)
        store = self.request.query_params.get("store", None)
        number_sold = self.request.query_params.get("number_sold", None)
        min_price = self.request.query_params.get("min_price", None)
        name = self.request.query_params.get("name", None)
        location = self.request.query_params.get("location", None)
        customer = self.request.query_params.get("customer", None)

        if order is not None:
            order_filter = order

            if direction is not None:
                if direction == "desc":
                    order_filter = f"-{order}"

            products = products.order_by(order_filter)

        if category is not None:
            products = products.filter(category__id=category)

        if quantity is not None:
            products = products.order_by("-created_date")[: int(quantity)]

        if store is not None:
            found_store = Store.objects.get(pk=store)
            products = products.filter(customer=found_store.owner)

        if number_sold is not None:

            def sold_filter(product):
                if product.number_sold >= int(number_sold):
                    return True
                return False

            products = filter(sold_filter, products)

        if min_price is not None:
            products = products.filter(price__gte=min_price)

        if name is not None:
            products = products.filter(name__icontains=name)

        if location is not None:
            products = products.filter(location__icontains=location)

        if customer is not None:
            products = products.filter(customer=customer)

        serializer = ProductSerializer(
            products, many=True, context={"request": request}
        )
        return Response(serializer.data)

    @action(methods=["post"], detail=True)
    def recommend(self, request, pk=None):
        """Recommend products to other users"""

        if request.method == "POST":
            rec = Recommendation()
            rec.recommender = Customer.objects.get(user=request.auth.user)
            rec.customer = Customer.objects.get(user__id=request.data["recipient"])
            rec.product = Product.objects.get(pk=pk)

            rec.save()

            return Response(None, status=status.HTTP_204_NO_CONTENT)

        return Response(None, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(methods=["post"], detail=True)
    def rate_product(self, request, pk=None):
        if request.method == "POST":
            product_rating = ProductRating()
            product_rating.product = Product.objects.get(pk=pk)
            product_rating.customer = Customer.objects.get(user=request.auth.user)
            product_rating.rating = request.data["score"]

            product_rating.save()

            return Response(None, status=status.HTTP_201_CREATED)

    @action(methods=["post", "delete", "get"], detail=True)
    def like(self, request, pk=None):

        liker = get_object_or_404(Customer, user=request.auth.user)
        product = get_object_or_404(Product, pk=pk)

        if request.method == "POST":
            try:
                # Check if the user already liked the product
                existing_like = Like.objects.get(product=product, liker=liker)
                return Response(None, status=status.HTTP_405_METHOD_NOT_ALLOWED)
            except Like.DoesNotExist:
                # If there is no existing like, create a new one
                like = Like(liker=liker, product=product)
                like.save()
                return Response(None, status=status.HTTP_204_NO_CONTENT)

        if request.method == "GET":
            existing_like = Like.objects.filter(product=product, liker=liker).exists()
            return Response({"liked": existing_like}, status=status.HTTP_200_OK)

        elif request.method == "DELETE":
            try:
                # Try to delete the like
                like = Like.objects.get(product=product, liker=liker)
                like.delete()
                return Response(None, status=status.HTTP_204_NO_CONTENT)
            except Like.DoesNotExist:
                return Response(None, status=status.HTTP_404_NOT_FOUND)

    @action(methods=["get"], detail=False, url_path="liked")
    def liked(self, request):
        """
        Retrieves all products liked by the current user.
        """
        liker = Customer.objects.get(user=request.auth.user)
        liked_products = Like.objects.filter(liker=liker).values_list(
            "product", flat=True
        )
        products = Product.objects.filter(id__in=liked_products)

        serializer = ProductSerializer(
            products, many=True, context={"request": request}
        )
        return Response(serializer.data)

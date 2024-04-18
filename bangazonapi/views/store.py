from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from bangazonapi.models import Customer, Store, Product
from bangazonapi.views.product import ProductSerializer
from .profile import CustomerSerializer


class StoreProductsSerializer(serializers.ModelSerializer):
    """JSON serializer for stores"""

    owner = CustomerSerializer(many=False, read_only=True)
    products = ProductSerializer(many=True)

    class Meta:
        model = Store
        fields = ("id", "name", "description", "owner", "products", "products_sold")


class StoreSerializer(serializers.ModelSerializer):
    """JSON serializer for stores"""

    owner = CustomerSerializer(many=False, read_only=True)

    class Meta:
        model = Store
        fields = ("id", "name", "description", "owner")


class Stores(ViewSet):

    def create(self, request):
        current_user = Customer.objects.get(user=request.auth.user)

        try:
            new_store = Store.objects.create(
                name=request.data["name"],
                description=request.data["description"],
                owner=current_user,
            )
        except (IntegrityError, ValueError, ValidationError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = StoreSerializer(new_store, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request):
        stores = Store.objects.all()
        serializer = StoreSerializer(stores, many=True, context={"request": request})
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            store = Store.objects.get(pk=pk)
            products = store.owner.products.all()
            store.products = products
            serializer = StoreProductsSerializer(
                store, many=False, context={"request": request}
            )
            return Response(serializer.data)
        except Store.DoesNotExist as ex:
            return Response({"message": ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

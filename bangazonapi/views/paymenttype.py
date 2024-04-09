"""View module for handling requests about customer payment types"""

from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from bangazonapi import models
from bangazonapi.models import Payment, Customer


class PaymentSerializer(serializers.HyperlinkedModelSerializer):
    """JSON serializer for Payment

    Arguments:
        serializers
    """

    class Meta:
        model = Payment
        url = serializers.HyperlinkedIdentityField(
            view_name="payment", lookup_field="id"
        )
        fields = (
            "id",
            "url",
            "merchant_name",
            "account_number",
            "expiration_date",
            "create_date",
        )


class Payments(ViewSet):

    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized payment instance
        """
        user = request.user
        customer = get_object_or_404(Customer, user=user)

        new_payment = Payment.objects.create(
            merchant_name=request.data.get("merchant_name"),
            account_number=request.data.get("account_number"),
            expiration_date=request.data.get("expiration_date"),
            create_date=timezone.now(),
            customer=customer,
        )

        serializer = PaymentSerializer(new_payment, context={"request": request})

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single payment type

        Returns:
            Response -- JSON serialized payment_type instance
        """
        try:
            payment_type = Payment.objects.get(pk=pk)
            serializer = PaymentSerializer(payment_type, context={"request": request})
            return Response(serializer.data)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def destroy(self, request, pk=None):
        """Handle DELETE requests for a single payment type

        Returns:
            Response -- 200, 404, or 500 status code
        """
        try:
            payment = Payment.objects.get(pk=pk)
            payment.delete()

            return Response({}, status=status.HTTP_204_NO_CONTENT)

        except Payment.DoesNotExist as ex:
            return Response({"message": ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response(
                {"message": ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def list(self, request):
        """Handle GET requests to payment type resource"""
        payment_types = Payment.objects.all()

        customer_id = self.request.query_params.get("customer", None)

        if customer_id is not None:
            payment_types = payment_types.filter(customer__id=customer_id)

        serializer = PaymentSerializer(
            payment_types, many=True, context={"request": request}
        )
        return Response(serializer.data)

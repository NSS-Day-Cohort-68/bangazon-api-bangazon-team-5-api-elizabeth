from django.shortcuts import render
from bangazonapi.models import Order


def report(request):
    unpaid_orders = Order.objects.filter(payment_type=None)
    report_data = [{"order_id": order.id} for order in unpaid_orders]

    return render(request, "index.html", {"report_data": report_data})

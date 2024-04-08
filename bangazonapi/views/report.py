from django.shortcuts import render
from bangazonapi.models import Order, Customer


def report(request):

    unpaid_orders = Order.objects.filter(payment_type=None)
    # order_user = Customer.objects.filter(customer_id = id)
    report_data = [
        {"order_id": order.id, "customer_name": order.customer_id}
        for order in unpaid_orders
    ]

    return render(request, "index.html", {"report_data": report_data})

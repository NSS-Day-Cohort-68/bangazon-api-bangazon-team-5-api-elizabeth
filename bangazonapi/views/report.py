from django.shortcuts import render
from bangazonapi.models import Order, Customer
from django.contrib.auth.models import User


def report(request):

    unpaid_orders = Order.objects.filter(payment_type=None)

    report_data = [
        {"order_id": order.id, "customer_name": user.first_name + " " + user.last_name}
        for order in unpaid_orders
        for customer in Customer.objects.filter(id=order.customer_id)
        for user in User.objects.filter(id=customer.user_id)
    ]

    return render(request, "index.html", {"report_data": report_data})

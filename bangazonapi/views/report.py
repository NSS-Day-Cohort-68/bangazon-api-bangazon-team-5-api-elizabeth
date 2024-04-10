from django.shortcuts import render
from bangazonapi.models import Order, Customer, OrderProduct, Product
from django.contrib.auth.models import User


def report(request):
    unpaid_orders = Order.objects.filter(payment_type=None)
    report_data = []

    for order in unpaid_orders:
        customer = Customer.objects.get(id=order.customer_id)
        user = User.objects.get(id=customer.user_id)
        order_products = OrderProduct.objects.filter(order_id=order.id)

        total_cost = sum(
            product.price
            for order_product in order_products
            for product in Product.objects.filter(id=order_product.product_id)
        )

        report_data.append(
            {
                "order_id": order.id,
                "customer_name": f"{user.first_name} {user.last_name}",
                "total_cost": total_cost,
            }
        )

    return render(request, "index.html", {"report_data": report_data})


def expensive_products_report(request):
    expensive_products = Product.objects.filter(price__gte=1000)
    return render(
        request,
        "expensive_products_report.html",
        {"expensive_products": expensive_products},
    )

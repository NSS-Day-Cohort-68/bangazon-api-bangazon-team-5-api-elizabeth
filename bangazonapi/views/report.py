from django.shortcuts import render
from bangazonapi.models import Order, Customer, OrderProduct, Product, Favorite
from django.contrib.auth.models import User


def order_reports(request):
    status = request.GET.get("status")
    if status == "incomplete":
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

        data = {
            "status": status,
            "report_data": report_data,
            "html": {
                "title": "Unpaid Orders Report",
                "heading": "Unpaid Orders Report",
            },
        }

        return render(request, "index.html", data)

    if status == "complete":

        completed_orders = Order.objects.filter(payment_type__isnull=False)

        report_data = []
        for order in completed_orders:
            lineitems = order.lineitems.all()

            total_cost_of_order = 0
            for lineitem in lineitems:
                total_cost_of_order += lineitem.product.price

            table_data = {
                "order_id": order.id,
                "customer_name": f"{order.customer.user.first_name} {order.customer.user.last_name}",
                "total_paid": total_cost_of_order,
                "payment_type": order.payment_type.merchant_name,
            }
            report_data.append(table_data)

        data = {
            "status": status,
            "report_data": report_data,
            "html": {
                "title": "Completed Orders Report",
                "heading": "Completed Orders Report",
            },
        }

        return render(request, "index.html", data)


def expensive_products_report(request):
    expensive_products = Product.objects.filter(price__gte=1000)
    return render(
        request,
        "expensive_products_report.html",
        {"expensive_products": expensive_products},
    )


def inexpensive_products_report(request):
    inexpensive_products = Product.objects.filter(price__lte=999)
    return render(
        request,
        "inexpensive_products_report.html",
        {"inexpensive_products": inexpensive_products},
    )

def favorite_stores_report(request):
    favorite_stores = Favorite.objects.all()
    return render(
        request,
        "favorite_stores_report.html",
        {"favorite_stores": favorite_stores}
    )
import stripe
from django.conf import settings
from django.urls import reverse
from django.db import transaction
from django.core.mail import send_mail

from bookstore.services.warehouse_client import reserve_stock
from .models import Order, OrderItem
from .tasks import send_order_confirmation_email

# Залишаємо ініціалізацію ключа як приклад
stripe.api_key = str(settings.STRIPE_SECRET_KEY).encode("ascii", "ignore").decode("ascii").strip()


def create_order(cart, cleaned_data):
    with transaction.atomic():
        order = Order.objects.create(
            name=cleaned_data.get("name", ""),
            email=cleaned_data["email"],
            address=cleaned_data["address"],
        )

        # Позиції замовлення
        order_items = [
            OrderItem(
                order=order,
                book=item["book"],
                price=item["price"],
                quantity=item["quantity"],
            )
            for item in cart
        ]
        OrderItem.objects.bulk_create(order_items)

        # Резервуємо/списуємо залишки на складі (web_b) через REST API
        for item in cart:
            reserve_stock(book_id=item['book'].id, amount=item['quantity'])

        # Очищуємо кошик після успішного створення замовлення та резервування
        cart.clear()

        transaction.on_commit(
            lambda: send_order_confirmation_email.delay(
                order.id, order.name, order.email
            )
        )

        # Відправка Email клієнту
        subject = f'Замовлення №{order.id}'
        message = (
            f'Вітаю, {order.name}!\n\n'
            f'Ви успішно оформили замовлення у нашій книгарні. ID замовлення: {order.id}.'
        )
        send_mail(subject, message, 'from@bookstore.com', [order.email])

        return order


def create_stripe_checkout_session(request, order):
    # success_url = request.build_absolute_uri(reverse('payment:completed'))
    # cancel_url = request.build_absolute_uri(reverse('payment:canceled'))
    #
    # line_items = []
    # for item in order.item.all():
    #     sku_val = item.book.sku if item.book.sku else f"ID-{item.book.id}"
    #     safe_product_name = f"Book SKU: {sku_val}"
    #
    #     raw_sku = str(item.book.sku or '')
    #     safe_sku = raw_sku.encode('ascii', 'ignore').decode('ascii').strip()
    #
    #     safe_book_id = str(item.book.id).encode('ascii', 'ignore').decode('ascii').strip()
    #
    #     line_items.append({
    #         'price_data': {
    #             'currency': 'uah',
    #             'product_data': {
    #                 'name': safe_product_name,
    #                 'metadata': {
    #                     'sku': safe_sku,
    #                     'book_id': safe_book_id,
    #                 },
    #             },
    #             'unit_amount': int(item.price * 100),
    #         },
    #         'quantity': item.quantity,
    #     })
    #
    # session = stripe.checkout.Session.create(
    #     payment_method_types=['card'],
    #     line_items=line_items,
    #     mode='payment',
    #     success_url=str(success_url),
    #     cancel_url=str(cancel_url),
    #     client_reference_id=str(order.id).encode('ascii', 'ignore').decode('ascii'),
    # )
    # return session.url

    success_url = request.build_absolute_uri(reverse('payment:completed'))
    return success_url
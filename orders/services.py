import stripe
from django.conf import settings
from django.urls import reverse
from django.db import transaction
from django.core.mail import send_mail
from .models import Order, OrderItem

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_order(cart, cleaned_data):
    with transaction.atomic():
        order = Order.objects.create(
            name=cleaned_data.get('name', ''),
            email=cleaned_data['email'],
            address=cleaned_data['address']
        )

        # позиції замовлення
        order_items = []
        for item in cart:
            order_items.append(
                OrderItem(
                    order=order,
                    book=item['book'],
                    price=item['price'],
                    quantity=item['quantity']
                )
            )
        OrderItem.objects.bulk_create(order_items)

        # Очищуємо кошик після успішного створення
        cart.clear()

        # Відправка Email клієнту
        subject = f'Замовлення №{order.id}'
        message = f'Вітаю, {order.name}!\n\nВи успішно оформили замовлення у нашій книгарні. ID замовлення: {order.id}.'
        send_mail(subject, message, 'from@bookstore.com', [order.email])

        return order


def create_stripe_checkout_session(request, order):
    # створення платіжної сесії
    success_url = request.build_absolute_uri(reverse('payment:completed'))
    cancel_url = request.build_absolute_uri(reverse('payment:canceled'))

    line_items = []
    for item in order.item.all():
        title_str = str(item.book.title)
        safe_title = item.book.title.encode('ascii', 'ignore').decode('ascii')
        if not safe_title:
            safe_title = f"Book #{item.book.id}"
        line_items.append({
            'price_data': {
                'currency': 'uah',
                'product_data': {
                    'name': item.book.title,
                },
                'unit_amount': int(item.price * 100),  # у копійках
            },
            'quantity': item.quantity,
        })

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url=success_url,
        cancel_url=cancel_url,
        client_reference_id=order.id,
    )
    return session.url
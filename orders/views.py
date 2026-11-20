from django.contrib import messages
from django.shortcuts import render, redirect
from bookstore.services.warehouse_client import WarehouseServiceError
from .cart import Cart
from .services import create_order, create_stripe_checkout_session
from .forms import OrderCreateForm


def order_create(request):
    cart = Cart(request)

    # Якщо кошик порожній
    if len(cart) == 0:
        return redirect('catalog:book_list')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            try:
                # 1. Створюємо замовлення та резервуємо залишки на складі (web_b)
                order = create_order(cart, form.cleaned_data)

                # 2. Генеруємо посилання на оплату Stripe
                stripe_url = create_stripe_checkout_session(request, order)

                # 3. Перенаправляємо користувача на сторінку оплати Stripe
                return redirect(stripe_url, code=303)
            except WarehouseServiceError as exc:
                messages.error(request, str(exc))
    else:
        form = OrderCreateForm()

    return render(request, 'orders/order_create.html', {'cart': cart, 'form': form})
# AI Code Review

## 1. Catalog Book List View (`catalog/views.py`)

* **Оригінальний код:**
  ```python
  def book_list(request):
      books = Book.objects.all()
      return render(request, 'catalog/book_list.html', {'books': books})
  
- **Рекомендації AI:**
  - Додати пагінацію (`Paginator`), щоб сторінка не завантажувала всі книги з бази за один раз.
  - Використовувати `select_related` для оптимізації запитів до бази даних.

- **Фінальний код:**
  ```python
  from django.core.paginator import Paginator
  from django.shortcuts import render
  from .models import Book

  def book_list(request):
      """Повертає список книг каталогу з пагінацією та оптимізацією запитів."""
      book_queryset = Book.objects.select_related('category').all()
      paginator = Paginator(book_queryset, 10)
      page_number = request.GET.get('page')
      books = paginator.get_page(page_number)
      return render(request, 'catalog/book_list.html', {'books': books})
  
---

## 2. Order Creation Logic (`orders/services.py`)

- **Оригінальний код:**
  ```python
  def create_order(cart, user):
      order = Order.objects.create(user=user)
      for item in cart:
          OrderItem.objects.create(order=order, book=item['book'], quantity=item['quantity'])
      return order
  
- **Рекомендації AI:**
  - Обгорнути процес створення замовлення в транзакцію (`transaction.atomic()`).
  - Використовувати `bulk_create` для масового створення елементів.

- **Фінальний код:**
  ```python
  from django.db import transaction
  from .models import Order, OrderItem

  def create_order(cart, user):
      """Атомарно створює замовлення та всі пов'язані позиції товарів."""
      with transaction.atomic():
          order = Order.objects.create(user=user)
          order_items = [
              OrderItem(
                  order=order,
                  book=item['book'],
                  price=item['price'],
                  quantity=item['quantity']
              )
              for item in cart
          ]
          OrderItem.objects.bulk_create(order_items)
          return order
  
---

## 3. Cart Session Manager (`cart/cart.py`)

- **Оригінальний код:**
  ```python
  class Cart:
      def __init__(self, request):
          self.session = request.session
          cart = self.session.get('cart')
          if not cart:
              cart = self.session['cart'] = {}
          self.cart = cart
  
- **Рекомендації AI:**
  - Додати типи даних (Type Hints) для зручності читання та підтримки IDE.
  - Додати метод збереження сесії.

- **Фінальний код:**
  ```python
  from django.http import HttpRequest

  class Cart:
      """Клас для керування покупками в кошику користувача через сесію."""
      def __init__(self, request: HttpRequest):
          self.session = request.session
          cart = self.session.get('cart')
          if not cart:
              cart = self.session['cart'] = {}
          self.cart = cart

      def save(self):
          """Оновлює сесію користувача."""
          self.session.modified = True
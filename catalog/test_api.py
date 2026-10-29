from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from catalog.models import Book, Category

User = get_user_model()


class BookAPITests(APITestCase):

    def setUp(self):
        # Робимо тестові дані, які будуть використовуватися в наших тестах
        self.category1 = Category.objects.create(name='Fiction', slug='fiction')
        self.category2 = Category.objects.create(name='Science', slug='science')

        self.book1 = Book.objects.create(
            title='Django for Beginners',
            author='William S. Vincent',
            price=400.00,
            category=self.category1,
            description='Learn Django from scratch'
        )
        self.book2 = Book.objects.create(
            title='Python Tricks',
            author='Dan Bader',
            price=600.00,
            category=self.category2,
            description='Clean Python code'
        )

        # Створив користувачів (простого та адміна)
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.admin_user = User.objects.create_superuser(username='admin', password='adminpassword')

        # URL для списку та детального перегляду книг у DRF роутері (basename='book')
        self.book_list_url = reverse('book-list')
        self.book_detail_url = lambda pk: reverse('book-detail', kwargs={'pk': pk})

    # --- тест перегляду (GET) ---

    def test_get_book_list(self):
        """Тест списку книг"""
        response = self.client.get(self.book_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Перевіряємо, що повернулося дві книги (з урахуванням пагінації через results)
        self.assertEqual(len(response.data['results']), 2)

    def test_get_book_detail(self):
        """Тест-інформація про конкретну книгу"""
        response = self.client.get(self.book_detail_url(self.book1.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.book1.title)

    def test_filter_books_by_category(self):
        """Тест фільтрація книг по категорії"""
        response = self.client.get(self.book_list_url, {'category': self.category1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], self.book1.title)

    def test_search_books_by_title(self):
        """Тест-пошук книг по назві"""
        response = self.client.get(self.book_list_url, {'search': 'Python'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], self.book2.title)

    def test_order_books_by_price(self):
        """Тест-сортування книг по ціні"""
        response = self.client.get(self.book_list_url, {'ordering': 'price'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['price'], '400.00')

    # --- тест створення (POST) ---

    def test_create_book_unauthenticated(self):
        """Тест неавторизований користувач має обмеження прав"""
        data = {
            'title': 'New Book',
            'author': 'Author',
            'price': 500.00,
            'category_id': self.category1.id
        }
        response = self.client.post(self.book_list_url, data)
        # Залежно від вашого Permission class це може бути 401 або 403
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_create_book_authenticated(self):
        """Тест авторизований користувач вдало створює книгу"""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'title': 'Advanced Django',
            'author': 'Super Author',
            'price': 750.00,
            'category_id': self.category1.id,
            'description': 'Deep dive'
        }
        response = self.client.post(self.book_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 3)

    # --- тести оновлення (PUT/PATCH) ---

    def test_update_book(self):
        """Тест оновлення існуючої книги адміном"""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'title': 'Updated Title',
            'author': 'William S. Vincent',
            'price': 450.00,
            'category_id': self.category1.id
        }
        response = self.client.put(self.book_detail_url(self.book1.id), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.title, 'Updated Title')

    # --- тест видалення (DELETE) ---

    def test_delete_book(self):
        """Тест видалення книги адміном"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.book_detail_url(self.book1.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Book.objects.count(), 1)

    def test_cors_headers(self):
        """Перевірка наявності CORS заголовків"""
        response = self.client.get(self.book_list_url, HTTP_ORIGIN='http://localhost:3000')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Access-Control-Allow-Origin', response.headers)
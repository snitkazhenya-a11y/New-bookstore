from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.BookListView.as_view(), name='book_list'),
    path('books/', views.BookListView.as_view(), name='book_list_alt'),
    path('books/<int:pk>/', views.BookDetailView.as_view(), name='book_detail'),
    path('books/create/', views.BookCreateView.as_view(), name='book_create'),
    path('books/<int:pk>/update/', views.BookUpdateView.as_view(), name='book_update'),
    path('books/<int:pk>/delete/', views.BookDeleteView.as_view(), name='book_delete'),
    path('async/books/', views.async_book_list_view, name='async_book_list'),
    path('async/books/<int:pk>/', views.async_book_detail_view, name='async_book_detail'),
    path('async/books/expensive/', views.async_expensive_books_count, name='async_expensive_count'),
]
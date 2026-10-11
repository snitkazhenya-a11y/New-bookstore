from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Book, Category
from django.http import JsonResponse
from django.http import HttpResponse

class BookListView(ListView):
    model = Book
    template_name = 'catalog/book_list.html'
    context_object_name = 'books'
    paginate_by = 6

    def get_queryset(self):
        queryset = super().get_queryset()
        category_id = self.request.GET.get('category')
        search_query = self.request.GET.get('q')

        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if search_query:
            queryset = queryset.filter(title__icontains=search_query)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['selected_category'] = self.request.GET.get('category', '')
        context['search_query'] = self.request.GET.get('q', '')
        return context

class BookDetailView(DetailView):
    model = Book
    template_name = 'catalog/book_detail.html'
    context_object_name = 'book'

class BookCreateView(CreateView):
    model = Book
    fields = ['title', 'author', 'category', 'price', 'description', 'stock']
    template_name = 'catalog/book_form.html'
    success_url = reverse_lazy('catalog:book_list')

class BookUpdateView(UpdateView):
    model = Book
    fields = ['title', 'author', 'category', 'price', 'description', 'stock']
    template_name = 'catalog/book_update.html'
    success_url = reverse_lazy('catalog:book_list')

class BookDeleteView(DeleteView):
    model = Book
    template_name = 'catalog/book_delete.html'
    success_url = reverse_lazy('catalog:book_list')

async def async_book_list_view(request):
    books = [book async for book in Book.objects.all().alist()]
    data = [{"title": book.title, "price": str(book.price)} for book in books]
    return JsonResponse({"books": data})

async def async_book_detail_view(request):
    try:
        book = await Book.objects.aget(pk=pk)
        return JsonResponse({
            "title": book.title,
            "description": book.description,
            "price": str(book.price),
        })
    except Book.DoesNotExist:
        return JsonResponse({"error": "Книгу не знайдено"}, status=400)

async def async_expensive_book_count(request):
    count = await Book.objects.filter(price__gt=500).acount()
    return JsonResponse({"expensive_book_count": count})

async def async_expensive_books_count(request):
    return HttpResponse("OK")


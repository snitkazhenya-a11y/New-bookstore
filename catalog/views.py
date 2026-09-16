from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Book, Category

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



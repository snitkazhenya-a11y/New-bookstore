from django.contrib import admin
from .models import Category, Book

class BookInline(admin.TabularInline):
    model = Book
    extra = 1
    fields = ('title', 'author', 'price', 'stock')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'get_books_count')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    inlines = [BookInline]

    def get_books_count(self, obj):
        return obj.books.count()
    get_books_count.short_description = "Кількість книг"

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'price', 'stock')
    list_filter = ('category', 'price', 'stock')
    search_fields = ('title', 'author', 'description')
    list_editable = ('price', 'stock')
    ordering = ('title',)
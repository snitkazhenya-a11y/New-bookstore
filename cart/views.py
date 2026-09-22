from django.shortcuts import get_object_or_404, redirect, render
from catalog.models import Book

def cart_detail(request):
    cart = request.session.get('cart', {})
    return render(request, 'cart/cart_detail.html', {'cart': cart})

def cart_add(request, book_id):
    cart = request.session.get('cart', {})
    book_id_str = str(book_id)
    if book_id_str in cart:
        cart[book_id_str]['quantity'] += 1
    else:
        book = get_object_or_404(Book, id=book_id)
        cart[book_id_str] = {
            'title': book.title,
            'price': str(book.price),
            'quantity': 1,
        }
    request.session['cart'] = cart
    request.session.modified = True
    return redirect('cart:cart_detail')
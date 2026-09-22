from django.shortcuts import render, redirect, get_object_or_404
from catalog.models import Book

def cart_detail(request):
    cart = request.session.get('cart', {})
    return render(request, 'cart/cart_detail.html', {'cart': cart})

def cart_add(request, book_id):
    cart = request.session.get('cart', {})
    book_id_str = str(book_id)
    quantity = int(request.POST.get('quantity', 1))
    book = get_object_or_404(Book, id=book_id)

    if book_id_str in cart:
        cart[book_id_str]['quantity'] += quantity
    else:
        book = get_object_or_404(Book, id=book_id)
        cart[book_id_str] = {
            'title': book.title,
            'price': str(book.price),
            'quantity': quantity,
        }
    request.session['cart'] = cart
    request.session.modified = True
    return redirect('cart:cart_detail')

def cart_remove(request, book_id):
    cart = request.session.get('cart', {})
    book_id_str = str(book_id)

    if book_id_str in cart:
        del cart[book_id_str]
        request.session['cart'] = cart
        request.session.modified = True

    return redirect('cart:cart_detail')
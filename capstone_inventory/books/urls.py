from django.urls import path
from .views import BookListView, checkout_book, return_book


urlpatterns = [
    path('', BookListView.as_view(), name='book-list'),
    path('checkout/<int:book_id>/', checkout_book, name='checkout-book'),
    path('return/<int:transaction_id>/', return_book, name='return-book'),
]

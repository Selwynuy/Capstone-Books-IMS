from django.urls import path
from .views import BookListView, checkout_book, return_book, BookDetailView


urlpatterns = [
    path('', BookListView.as_view(), name='book-list'),
    path('checkout/<int:book_id>/', checkout_book, name='checkout-book'),
    path('return/<int:transaction_id>/', return_book, name='return-book'),
    path('book/<int:pk>/', BookDetailView.as_view(), name='book-detail'),
]

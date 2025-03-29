from django.urls import path
from .views import BookListView, checkout_book, return_book
from .admin_views import borrower_dashboard
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', BookListView.as_view(), name='book-list'),
    path('checkout/<int:book_id>/', checkout_book, name='checkout-book'),
    path('return/<int:transaction_id>/',
         login_required(return_book), name='return-book'),
    path('admin/borrower-dashboard/',
         borrower_dashboard, name='borrower-dashboard'),

]

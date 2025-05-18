from django.urls import path
from . import views

urlpatterns = [
    path('', views.LandingPageView.as_view(), name='landing'),  # Root is now the landing page
    path('books/', views.BookListView.as_view(), name='book_list'),
    path('book/<int:pk>/', views.BookDetailView.as_view(), name='book_detail'),
    path('checkout/<int:book_id>/', views.checkout_book, name='checkout_book'),
    path('return/<int:book_id>/', views.return_book, name='return_book'),
]

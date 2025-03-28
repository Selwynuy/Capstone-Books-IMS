from django.views.generic import ListView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Book, Transaction
from datetime import date, timedelta
from django.utils import timezone
from django.contrib import messages


class BookListView(ListView):
    model = Book
    template_name = 'books/book_list.html'
    context_object_name = 'books'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get("q")
        if search_query:
            return queryset.filter(
                Q(title__icontains=search_query) |
                Q(author__icontains=search_query) |
                Q(category__icontains=search_query))
        return queryset


def checkout_book(request, pk):
    book = Book.objects.get(pk=pk)
    if request.method == 'POST':
        Transaction.objects.create(
            book=book,
            borrower_name=request.POST.get('borrower_name'),
            borrower_id=request.POST.get('borrower_id'),
            due_date=date.today() + timedelta(days=3)
        )
        book.status = 'CHECKED_OUT'
        book.save()
        return redirect('book-list')
    return render(request, 'books/checkout_form.html', {'book': book})


def return_book(request, transaction_id):
    transaction = get_object_or_404(Transaction, pk=transaction_id)

    if request.method == 'POST':
        is_original_borrower = request.POST.get('borrowerToggle') == 'on'

        # Validate original borrower if toggle is on
        if is_original_borrower:
            if request.POST.get('borrower_id', '') != transaction.borrower_id:
                messages.error(request, "Invalid borrower ID")
                return redirect('return-book', transaction_id=transaction_id)
            # Auto-fill returner info for original borrower
            returner_name = transaction.borrower_name
            returner_id = transaction.borrower_id
        else:
            # Validate third-party returner info
            returner_name = request.POST.get('returner_name', '').strip()
            returner_id = request.POST.get('returner_id', '').strip()
            if not returner_name or not returner_id:
                messages.error(request, "Please provide returner information")
                return redirect('return-book', transaction_id=transaction_id)

        # Common processing
        transaction.returned_date = timezone.now()
        transaction.condition_notes = request.POST.get(
            'condition_notes', '').strip()
        transaction.returner_name = returner_name
        transaction.returner_id = returner_id
        transaction.save()

        transaction.book.status = 'AVAILABLE'
        transaction.book.save()

        messages.success(request, "Book returned successfully")
        return redirect('book-list')

    return render(request, 'books/return_book.html', {
        'transaction': transaction,
        'now': timezone.now().date()
    })


class OverdueBooksView(ListView):
    model = Transaction
    template_name = 'books/overdue_list.html'
    context_object_name = 'transactions'

    def get_queryset(self):
        return Transaction.objects.filter(
            returned_date__isnull=True,
            due_date__lt=timezone.now().date()
        )

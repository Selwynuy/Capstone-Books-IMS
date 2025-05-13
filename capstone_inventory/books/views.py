from django.views.generic import ListView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Book, Transaction, CustomUser
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
                Q(authors__name__icontains=search_query) |
                Q(panelists__name__icontains=search_query) |
                Q(abstract__icontains=search_query)
            ).distinct()
        return queryset

    def render_to_response(self, context, **response_kwargs):
        if getattr(self.request, 'htmx', False):
            return render(self.request, 'books/partials/book_grid.html', context)
        return super().render_to_response(context, **response_kwargs)


def checkout_book(request, book_id):
    book = get_object_or_404(Book, pk=book_id)

    if request.method == 'POST':
        borrower_id = request.POST.get('borrower_id').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()

        # Get or create borrower with all details
        borrower, created = CustomUser.objects.get_or_create(
            borrower_id=borrower_id,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'username': borrower_id,  # Required field
                'is_borrower': True
            }
        )

        # Update names if borrower exists but names weren't set
        if not created and (not borrower.first_name or not borrower.last_name):
            borrower.first_name = first_name
            borrower.last_name = last_name
            borrower.save()

        Transaction.objects.create(
            book=book,
            borrower=borrower,
            due_date=timezone.now().date() + timedelta(days=3)
        )

        book.status = 'CHECKED_OUT'
        book.borrower = borrower
        book.save()

        return redirect('book-list')

    return render(request, 'books/checkout_form.html', {
        'book': book,
        'authors': book.authors.all()  # Pass authors to template
    })


def return_book(request, transaction_id):
    transaction = get_object_or_404(Transaction, pk=transaction_id)

    if request.method == 'POST':
        is_original_borrower = request.POST.get('borrowerToggle') == 'on'
        borrower_id = request.POST.get('borrower_id', '').strip()

        if is_original_borrower:
            # Case-insensitive comparison with stored ID
            if not borrower_id or not borrower_id.upper() == transaction.borrower.borrower_id.upper():
                messages.error(
                    request, "The borrower ID doesn't match the original checkout")
                return render(request, 'books/return_form.html', {
                    'transaction': transaction,
                    'now': timezone.now().date()
                })

            # Use original borrower as returner
            returner = transaction.borrower
        else:
            # Handle third-party return
            returner_id = request.POST.get('returner_id', '').strip()
            if not returner_id:
                messages.error(request, "Returner ID is required")
                return redirect('return-book', transaction_id=transaction.id)

            returner, _ = CustomUser.objects.get_or_create(
                borrower_id=returner_id,
                defaults={'is_borrower': True}
            )

        # Process return
        transaction.returned_date = timezone.now()
        transaction.returner = returner
        transaction.condition_notes = request.POST.get('condition_notes', '')
        transaction.save()

        messages.success(request, "Book returned successfully")
        return redirect('book-list')

    return render(request, 'books/return_book.html', {
        'transaction': transaction,
        'now': timezone.now().date()
    })

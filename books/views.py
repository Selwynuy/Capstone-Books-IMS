from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, TemplateView
from django.contrib import messages
from django.db.models import Q
from .models import Book, Transaction, Author, Panelist, Adviser

class LandingPageView(TemplateView):
    template_name = 'books/landing.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['authors'] = Author.objects.all()
        context['panelists'] = Panelist.objects.all()
        context['advisers'] = Adviser.objects.all()
        return context

class BookListView(ListView):
    model = Book
    template_name = 'books/book_list.html'
    context_object_name = 'books'
    paginate_by = 12

    def get_queryset(self):
        queryset = Book.objects.all().prefetch_related('authors', 'panelists').select_related('adviser')
        
        search_query = self.request.GET.get('search')
        search_type = self.request.GET.get('search_type', 'all')
        author_id = self.request.GET.get('author')
        adviser_id = self.request.GET.get('adviser')
        availability = self.request.GET.get('availability')
        
        # Search by type
        if search_query:
            if search_type == 'title':
                queryset = queryset.filter(title__icontains=search_query)
            elif search_type == 'author':
                queryset = queryset.filter(authors__name__icontains=search_query)
            elif search_type == 'panelist':
                queryset = queryset.filter(panelists__name__icontains=search_query)
            else:  # 'all'
                queryset = queryset.filter(
                    Q(title__icontains=search_query) |
                    Q(authors__name__icontains=search_query) |
                    Q(panelists__name__icontains=search_query) |
                    Q(adviser__name__icontains=search_query)
                ).distinct()
        
        # Filter by author
        if author_id:
            queryset = queryset.filter(authors__id=author_id)
        
        # Filter by adviser
        if adviser_id:
            queryset = queryset.filter(adviser__id=adviser_id)
        
        # Filter by availability
        if availability == 'available':
            queryset = queryset.filter(transaction__isnull=True)
        elif availability == 'checked_out':
            queryset = queryset.filter(transaction__returned_at__isnull=True)
        
        return queryset

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('HX-Request'):
            return render(self.request, 'books/partials/book_grid.html', context)
        return super().render_to_response(context, **response_kwargs)

class BookDetailView(TemplateView):
    template_name = 'books/book_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['book'] = get_object_or_404(Book, pk=kwargs['pk'])
        return context

def checkout_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    
    # Check if book is already checked out
    existing_transaction = Transaction.objects.filter(book=book, returned_at__isnull=True).first()
    if existing_transaction:
        messages.error(request, f'This book is already checked out by {existing_transaction.borrower_name}.')
        return redirect('book_list')
    
    if request.method == 'POST':
        borrower_id = request.POST.get('borrower_id')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        borrower_name = f"{first_name} {last_name}"
        
        # Create the transaction
        Transaction.objects.create(
            book=book,
            borrower_id=borrower_id,
            borrower_name=borrower_name
        )
        
        messages.success(request, f'Successfully checked out "{book.title}" to {borrower_name}.')
        return redirect('book_list')
    
    return render(request, 'books/checkout_form.html', {'book': book})

def return_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    transaction = get_object_or_404(Transaction, book=book, returned_at__isnull=True)
    
    if request.method == 'POST':
        # Mark the book as returned
        from django.utils import timezone
        transaction.returned_at = timezone.now()
        transaction.save()
        
        messages.success(request, f'Successfully returned "{book.title}".')
        return redirect('book_list')
    
    return render(request, 'books/return_book.html', {
        'book': book,
        'transaction': transaction
    }) 
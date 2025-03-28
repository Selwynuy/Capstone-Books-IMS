from django.contrib import admin
from .models import Book, Transaction


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'date_added')
    list_filter = ('status',)
    search_fields = ('title', 'author')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('book', 'borrower_name', 'checkout_date',
                    'returned_date', 'condition_notes')
    list_filter = ('returned_date',)
    search_fields = ('book__title', 'borrower_name')

    fieldsets = (
        (None, {
            'fields': ('book', 'borrower_name', 'borrower_id')
        }),
        ('Dates', {
            'fields': ('checkout_date', 'due_date', 'returned_date')
        }),
        ('Return Information', {
            'fields': ('returner_name', 'returner_id', 'condition_notes'),
            'classes': ('collapse',)
        }),
    )

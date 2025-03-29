# books/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Book, Transaction


@admin.register(CustomUser)
class UserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_staff', 'is_borrower')}),
    )
    list_display = ('get_full_name', 'borrower_id', 'is_staff', 'is_borrower')
    search_fields = ('first_name', 'last_name', 'borrower_id')

    # For adding new users in admin
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('borrower_id', 'password1', 'password2', 'is_staff'),
        }),
    )
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or "No name provided"
    get_full_name.short_description = 'Name'


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'get_borrower_name')
    list_filter = ('status',)
    search_fields = ('title', 'author', 'borrower__first_name', 'borrower__last_name')

    def get_borrower_name(self, obj):
        return obj.borrower.get_full_name() if obj.borrower else "None"
    get_borrower_name.short_description = 'Borrower'

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('book', 'get_borrower_name', 'checkout_date', 'due_date', 'returned_date')
    list_filter = ('checkout_date', 'returned_date')
    search_fields = ('book__title', 'borrower__first_name', 'borrower__last_name')
    
    def get_borrower_name(self, obj):
        return obj.borrower.get_full_name()
    get_borrower_name.short_description = 'Borrower'
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Book, Transaction, Author, Panelist, Adviser
from django.db import models
from django import forms
from django.utils.html import format_html


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


class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    icon_name = 'user-pen'


class PanelistAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    icon_name = 'users'


class AdviserAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    icon_name = 'user-tie'


class BookAdminForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = '__all__'

    def clean_approval_sheet(self):
        file = self.cleaned_data.get('approval_sheet', False)
        if file and not file.name.lower().endswith('.pdf'):
            raise forms.ValidationError("Only PDF files are allowed.")
        return file


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    form = BookAdminForm
    list_display = ('title', 'display_authors', 'status',
                    'get_adviser', 'get_borrower_name', 'approval_sheet_available')
    list_filter = ('status',)
    search_fields = ('title', 'authors__name',
                     'borrower__first_name', 'borrower__last_name')
    filter_horizontal = ('authors', 'panelists')
    icon_name = 'book'
    exclude = ("borrower",)
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'rows': 5, 'cols': 60})},
    }
    readonly_fields = ('approval_sheet_link',)
    fields = (
        'title', 'authors', 'panelists', 'adviser', 'cover_image', 'status', 'abstract', 'keywords',
        'approval_sheet', 'approval_sheet_link',
    )

    def display_authors(self, obj):
        return ", ".join([author.name for author in obj.authors.all()])
    display_authors.short_description = 'Authors'

    def get_adviser(self, obj):
        return obj.adviser.name if obj.adviser else "None"
    get_adviser.short_description = 'Adviser'

    def get_borrower_name(self, obj):
        return obj.borrower.get_full_name() if obj.borrower else "None"
    get_borrower_name.short_description = 'Borrower'

    def approval_sheet_link(self, obj):
        if obj.approval_sheet:
            return format_html('<a href="{}" download>Download Approval Sheet</a>', obj.approval_sheet.url)
        return "No file"
    approval_sheet_link.short_description = "Approval Sheet"

    def approval_sheet_available(self, obj):
        if obj.approval_sheet:
            return format_html(
                '<a href="{}" target="_blank" style="margin-right:10px;">Preview</a>'
                '<a href="{}" download>Download</a>',
                obj.approval_sheet.url,
                obj.approval_sheet.url
            )
        return "No file"
    approval_sheet_available.short_description = "Approval Sheet"
    approval_sheet_available.allow_tags = True


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('book', 'get_borrower_name',
                    'checkout_date', 'due_date', 'returned_date')
    list_filter = ('checkout_date', 'returned_date')
    search_fields = ('book__title', 'borrower__first_name',
                     'borrower__last_name')
    readonly_fields = ('returned_date',)
    icon_name = 'exchange-alt'

    def get_borrower_name(self, obj):
        return obj.borrower.get_full_name()
    get_borrower_name.short_description = 'Borrower'


# Register the new models
admin.site.register(Author, AuthorAdmin)
admin.site.register(Panelist, PanelistAdmin)
admin.site.register(Adviser, AdviserAdmin)

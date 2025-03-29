from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    # For regular users (borrowers)
    is_borrower = models.BooleanField(default=True)
    borrower_id = models.CharField(
        max_length=20, unique=True, blank=True, null=True)

    # For proper display in admin
    def __str__(self):
        if self.is_borrower:
            return f"{self.get_full_name()} ({self.borrower_id})" if self.borrower_id else self.username
        return self.username

    # For admin - no borrower_id needed
    def save(self, *args, **kwargs):
        if not self.is_borrower:
            self.borrower_id = None
        super().save(*args, **kwargs)

    def get_full_name(self):
        name = f"{self.first_name} {self.last_name}".strip()
        return name if name else f"Borrower {self.borrower_id}"


class Book(models.Model):
    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('CHECKED_OUT', 'Checked Out'),
    ]

    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    cover_image = models.ImageField(
        upload_to='book_covers/',
        blank=True,
        null=True
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='AVAILABLE'
    )
    date_added = models.DateTimeField(auto_now_add=True)
    borrower = models.ForeignKey(
        CustomUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    def __str__(self):
        return f"{self.title} by {self.author}"


class Transaction(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrower = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    checkout_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()
    returned_date = models.DateTimeField(blank=True, null=True)
    condition_notes = models.TextField(blank=True)
    returner = models.ForeignKey(
        CustomUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='returns'
    )

    def __str__(self):
        return f"{self.book.title} - {self.borrower.get_full_name()}"

    def save(self, *args, **kwargs):
        if self.returned_date:
            self.book.status = 'AVAILABLE'
            self.book.save()
        super().save(*args, **kwargs)

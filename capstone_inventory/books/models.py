from django.db import models
from django.utils import timezone


class Book(models.Model):
    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('CHECKED_OUT', 'Checked Out'),
    ]

    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    cover_image = models.ImageField(
        upload_to='book_covers/', blank=True, null=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='AVAILABLE')
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} by {self.author}"


class Transaction(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrower_name = models.CharField(max_length=100)
    borrower_id = models.CharField(max_length=20)
    checkout_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField()  # Will be set at checkout
    returned_date = models.DateTimeField(blank=True, null=True)
    condition_notes = models.TextField(blank=True)  # Only for returns
    returner_name = models.CharField(max_length=100, blank=True)
    returner_id = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.book.title} - {self.borrower_name}"
    
    def save(self, *args, **kwargs):
        if self.returned_date:
            self.book.status = 'AVAILABLE'
            self.book.save()
        super().save(*args, **kwargs)

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    # For regular users (borrowers)
    is_borrower = models.BooleanField(default=True)
    borrower_id = models.CharField(
        max_length=20, unique=True, blank=True, null=True)

    def __str__(self):
        if self.is_borrower:
            return f"{self.get_full_name()} ({self.borrower_id})" if self.borrower_id else self.username
        return self.username

    def save(self, *args, **kwargs):
        if not self.is_borrower:
            self.borrower_id = None
        super().save(*args, **kwargs)

    def get_full_name(self):
        name = f"{self.first_name} {self.last_name}".strip()
        return name if name else f"Borrower {self.borrower_id}"


class Person(models.Model):
    """Base model for authors, panelists, and advisers"""
    name = models.CharField(max_length=200)

    class Meta:
        # This makes it an abstract base class (won't create DB table)
        abstract = True

    def __str__(self):
        return self.name


class Author(Person):
    """Model specifically for book authors"""
    pass


class Panelist(Person):
    """Model for panelists associated with books"""
    pass


class Adviser(Person):
    """Model for advisers associated with books"""
    pass


class Book(models.Model):
    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('CHECKED_OUT', 'Checked Out'),
    ]

    title = models.CharField(max_length=200)
    authors = models.ManyToManyField(Author, related_name='books')
    panelists = models.ManyToManyField(Panelist, blank=True)
    adviser = models.ForeignKey(
        Adviser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
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
        on_delete=models.SET_NULL,
        related_name='borrowed_books'
    )

    def __str__(self):
        author_names = ", ".join([str(author)
                                 for author in self.authors.all()])
        return f"{self.title} by {author_names}"


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
        if self.returned_date and not self.book.status == 'AVAILABLE':
            self.book.status = 'AVAILABLE'
            self.book.save()
        super().save(*args, **kwargs)

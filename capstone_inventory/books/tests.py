from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import Book, Author, Panelist, Adviser, CustomUser, Transaction

# Create your tests here.

class BookModelTest(TestCase):
    def setUp(self):
        self.author = Author.objects.create(name="Test Author")
        self.panelist = Panelist.objects.create(name="Test Panelist")
        self.adviser = Adviser.objects.create(name="Test Adviser")
        self.book = Book.objects.create(
            title="Test Book",
            abstract="Test Abstract",
            status="AVAILABLE"
        )
        self.book.authors.add(self.author)
        self.book.panelists.add(self.panelist)
        self.book.adviser = self.adviser
        self.book.save()

    def test_book_creation(self):
        self.assertEqual(self.book.title, "Test Book")
        self.assertEqual(self.book.status, "AVAILABLE")
        self.assertEqual(self.book.authors.first(), self.author)
        self.assertEqual(self.book.panelists.first(), self.panelist)
        self.assertEqual(self.book.adviser, self.adviser)

    def test_book_str_representation(self):
        expected_str = f"Test Book by Test Author"
        self.assertEqual(str(self.book), expected_str)

class TransactionTest(TestCase):
    def setUp(self):
        self.author = Author.objects.create(name="Test Author")
        self.book = Book.objects.create(
            title="Test Book",
            status="AVAILABLE"
        )
        self.book.authors.add(self.author)
        self.borrower = CustomUser.objects.create(
            username="testuser",
            borrower_id="B001",
            is_borrower=True,
            first_name="Test",
            last_name="User"
        )

    def test_checkout_process(self):
        transaction = Transaction.objects.create(
            book=self.book,
            borrower=self.borrower,
            due_date=timezone.now().date() + timedelta(days=3)
        )
        self.book.status = "CHECKED_OUT"
        self.book.borrower = self.borrower
        self.book.save()

        self.assertEqual(self.book.status, "CHECKED_OUT")
        self.assertEqual(self.book.borrower, self.borrower)
        self.assertEqual(transaction.book, self.book)
        self.assertEqual(transaction.borrower, self.borrower)

    def test_return_process(self):
        transaction = Transaction.objects.create(
            book=self.book,
            borrower=self.borrower,
            due_date=timezone.now().date() + timedelta(days=3)
        )
        self.book.status = "CHECKED_OUT"
        self.book.borrower = self.borrower
        self.book.save()

        # Process return
        transaction.returned_date = timezone.now()
        transaction.returner = self.borrower
        transaction.condition_notes = "Good condition"
        transaction.save()

        self.assertEqual(transaction.returned_date.date(), timezone.now().date())
        self.assertEqual(transaction.returner, self.borrower)
        self.assertEqual(transaction.condition_notes, "Good condition")

class ViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.author = Author.objects.create(name="Test Author")
        self.book = Book.objects.create(
            title="Test Book",
            status="AVAILABLE"
        )
        self.book.authors.add(self.author)
        self.borrower = CustomUser.objects.create(
            username="testuser",
            borrower_id="B001",
            is_borrower=True,
            first_name="Test",
            last_name="User"
        )

    def test_book_list_view(self):
        response = self.client.get(reverse('book-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'books/book_list.html')
        self.assertContains(response, "Test Book")

    def test_checkout_view(self):
        response = self.client.post(
            reverse('checkout-book', args=[self.book.id]),
            {
                'borrower_id': 'B001',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        self.assertEqual(response.status_code, 302)  # Redirect after successful checkout
        self.book.refresh_from_db()
        self.assertEqual(self.book.status, "CHECKED_OUT")
        self.assertEqual(self.book.borrower, self.borrower)

    def test_return_view(self):
        # First checkout the book
        transaction = Transaction.objects.create(
            book=self.book,
            borrower=self.borrower,
            due_date=timezone.now().date() + timedelta(days=3)
        )
        self.book.status = "CHECKED_OUT"
        self.book.borrower = self.borrower
        self.book.save()

        # Then return it
        response = self.client.post(
            reverse('return-book', args=[transaction.id]),
            {
                'borrowerToggle': 'on',
                'borrower_id': 'B001',
                'condition_notes': 'Good condition'
            }
        )
        self.assertEqual(response.status_code, 302)  # Redirect after successful return
        transaction.refresh_from_db()
        self.book.refresh_from_db()
        self.assertIsNotNone(transaction.returned_date)
        self.assertEqual(self.book.status, "AVAILABLE")

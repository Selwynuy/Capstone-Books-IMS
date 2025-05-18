# Capstone Books Inventory Management System

A modern web-based library and inventory management system for capstone books, built with Django and Jazzmin.

## Features
- Book catalog with search, checkout, and return
- Custom user model for borrowers
- Admin interface with beautiful Jazzmin UI and icons
- Responsive, modern UI for users
- Book details, authors, panelists, advisers, and transactions
- HTMX-powered search for instant results
- **Admin-only approval sheet PDF upload, preview, and download for each book**

## Setup Instructions

### 1. Clone the repository
```
git clone https://github.com/Selwynuy/Capstone-Books-Inventory-Management-System.git
cd Capstone-Books-Inventory-Management-System
```

### 2. Create and activate a virtual environment
```
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```
pip install -r requirements.txt
```

### 4. Apply migrations
```
python manage.py migrate
```

### 5. Create a superuser (admin)
```
python manage.py createsuperuser
```

### 6. Run the development server
```
python manage.py runserver
```

### 7. Access the application
- User interface: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- Admin interface: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## Documentation

### Overview
Capstone Books Inventory Management System is designed to help academic institutions manage their capstone book collections. It provides:
- A searchable, filterable catalog of books
- Book checkout and return workflows
- Tracking of borrowers, advisers, authors, and panelists
- Admin management of all records

### Main Components
- **Books**: Each book has a title, authors, panelists, adviser, cover image, abstract, and status (available/checked out).
- **Authors, Panelists, Advisers**: Linked to books for full academic context.
- **Custom Users**: Borrowers are tracked with custom user fields.
- **Transactions**: Every checkout and return is logged as a transaction.
- **Admin Dashboard**: Enhanced with Jazzmin for a modern, icon-rich experience.
- **HTMX Search**: Instant search/filtering of books without page reloads.

### How It Works
- Users can browse and search the catalog, view book details, and check out or return books.
- Admins can add/edit/delete books, authors, panelists, advisers, and users from the admin interface.
- All actions are logged and visible in the admin dashboard.

### Customization
- To change the admin UI, edit `JAZZMIN_SETTINGS` in `settings.py`.
- To add new fields or features, update the models in `books/models.py` and run migrations.

### Admin Usage: Approval Sheet PDF
Admins can upload an "Approval Sheet" (PDF only) for each book in the Django admin:
- When adding or editing a book, use the "Approval Sheet" field to upload a PDF file.
- In the book list, if a PDF is present, you will see **Preview** and **Download** links in the "Approval Sheet" column.
    - **Preview** opens the PDF in a new tab for viewing or printing.
    - **Download** saves the PDF to your computer.
- Only PDF files are accepted. Regular users cannot see or access approval sheets.

---

## License
This project is for educational purposes. Please adapt as needed for your institution.

## Important Notes

- **Database file (`db.sqlite3`)**: This file should NOT be tracked by Git. If you see it in your repository, remove it and add `db.sqlite3` to your `.gitignore` file.
- **After deleting `db.sqlite3`**: Run migrations to recreate the database structure:
  ```
  python capstone_inventory/manage.py migrate
  ```
  Then, create a superuser if needed:
  ```
  python capstone_inventory/manage.py createsuperuser
  ```

- **Return Book Logic**: The return process now always shows the correct borrower and dates by fetching the latest unreturned transaction for a book. The return URL is now `/return/<book_id>/`.

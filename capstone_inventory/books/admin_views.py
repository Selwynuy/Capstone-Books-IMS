from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from django.contrib.auth.models import User
from books.models import Transaction
from django.utils import timezone

@user_passes_test(lambda u: u.is_staff)
def borrower_dashboard(request):
    borrowers = User.objects.filter(user_type='BORROWER')
    
    context = {
        'borrowers_count': borrowers.count(),
        'active_loans_count': Transaction.objects.filter(returned_date__isnull=True).count(),
        'overdue_count': Transaction.objects.filter(
            returned_date__isnull=True,
            due_date__lt=timezone.now().date()
        ).count(),
        'new_today_count': User.objects.filter(
            date_registered__date=timezone.now().date(),
            user_type='BORROWER'
        ).count(),
        'recent_borrowers': borrowers.order_by('-date_registered')[:10]
    }
    return render(request, 'admin/user_dashboard.html', context)
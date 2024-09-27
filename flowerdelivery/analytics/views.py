# analytics/views.py
from django.shortcuts import render
from django.utils.timezone import now
from django.db.models import Sum, Count
from flower_orders.models import Order


# Страница аналитики
def analytics_view(request):
    today = now().date()

    # Статистика за день
    daily_stats = Order.objects.filter(created_at__date=today).aggregate(
        total_sales=Sum('total_price'),
        total_orders=Count('id')
    )

    # Статистика за месяц
    month_start = today.replace(day=1)
    monthly_stats = Order.objects.filter(created_at__date__gte=month_start).aggregate(
        total_sales=Sum('total_price'),
        total_orders=Count('id')
    )

    # Статистика за год
    year_start = today.replace(month=1, day=1)
    yearly_stats = Order.objects.filter(created_at__date__gte=year_start).aggregate(
        total_sales=Sum('total_price'),
        total_orders=Count('id')
    )

    # Подготовка данных для шаблона
    context = {
        'daily_sales': daily_stats['total_sales'] or 0,
        'daily_orders': daily_stats['total_orders'] or 0,
        'monthly_sales': monthly_stats['total_sales'] or 0,
        'monthly_orders': monthly_stats['total_orders'] or 0,
        'yearly_sales': yearly_stats['total_sales'] or 0,
        'yearly_orders': yearly_stats['total_orders'] or 0,
    }

    return render(request, 'analytics/analytics.html', context)


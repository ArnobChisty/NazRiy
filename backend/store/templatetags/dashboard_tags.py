from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django import template
from django.utils import timezone

from store.models import Order, OrderItem, Product

register = template.Library()


def _month_shift(value: date, offset: int) -> date:
    index = value.year * 12 + value.month - 1 + offset
    return date(index // 12, index % 12 + 1, 1)


@register.simple_tag
def nazriy_dashboard():
    active_orders = Order.objects.exclude(status='cancelled')
    today = timezone.localdate()
    current_month = today.replace(day=1)
    previous_month = _month_shift(current_month, -1)
    next_month = _month_shift(current_month, 1)

    revenue = active_orders.aggregate(value=Sum('total'))['value'] or Decimal('0')
    order_count = active_orders.count()
    average_order = revenue / order_count if order_count else Decimal('0')
    month_revenue = active_orders.filter(created_at__date__gte=current_month, created_at__date__lt=next_month).aggregate(value=Sum('total'))['value'] or Decimal('0')
    previous_revenue = active_orders.filter(created_at__date__gte=previous_month, created_at__date__lt=current_month).aggregate(value=Sum('total'))['value'] or Decimal('0')
    growth = ((month_revenue - previous_revenue) / previous_revenue * 100) if previous_revenue else (Decimal('100') if month_revenue else Decimal('0'))

    first_chart_month = _month_shift(current_month, -5)
    monthly_rows = active_orders.filter(created_at__date__gte=first_chart_month).annotate(month=TruncMonth('created_at')).values('month').annotate(revenue=Sum('total'), orders=Count('id')).order_by('month')
    monthly_map = {row['month'].date().replace(day=1): row for row in monthly_rows}
    monthly_sales = []
    for offset in range(-5, 1):
        month = _month_shift(current_month, offset)
        row = monthly_map.get(month, {})
        monthly_sales.append({
            'label': month.strftime('%b'),
            'full_label': month.strftime('%B %Y'),
            'revenue': row.get('revenue') or Decimal('0'),
            'orders': row.get('orders') or 0,
        })
    max_monthly = max((item['revenue'] for item in monthly_sales), default=Decimal('0')) or Decimal('1')
    for item in monthly_sales:
        item['height'] = max(4, round(float(item['revenue'] / max_monthly * 100)))
    chart_points = ' '.join(
        f'{index * 20},{96 - round(float(item["revenue"] / max_monthly * 80))}'
        for index, item in enumerate(monthly_sales)
    )

    status_rows = {row['status']: row['count'] for row in Order.objects.values('status').annotate(count=Count('id'))}
    status_meta = [
        ('confirmed', 'Confirmed', '#d6ad55'),
        ('shipped', 'Shipped', '#82998b'),
        ('delivered', 'Delivered', '#e9e3da'),
        ('cancelled', 'Cancelled', '#7c2e3f'),
    ]
    total_status = sum(status_rows.values()) or 1
    status_data = []
    cursor = 0.0
    gradient_parts = []
    for key, label, color in status_meta:
        count = status_rows.get(key, 0)
        share = count / total_status * 100
        end = cursor + share
        gradient_parts.append(f'{color} {cursor:.2f}% {end:.2f}%')
        status_data.append({'key': key, 'label': label, 'color': color, 'count': count, 'share': round(share)})
        cursor = end

    low_stock = Product.objects.filter(stock_quantity__lte=5).order_by('stock_quantity', 'name')
    top_products = list(
        OrderItem.objects.exclude(order__status='cancelled')
        .values('product_id', 'product_name')
        .annotate(revenue=Sum('line_total'), units=Sum('quantity'))
        .order_by('-revenue')[:5]
    )
    max_product_revenue = max((item['revenue'] for item in top_products), default=Decimal('0')) or Decimal('1')
    for item in top_products:
        item['width'] = max(4, round(float(item['revenue'] / max_product_revenue * 100)))

    local_now = timezone.localtime()
    greeting = 'morning' if local_now.hour < 12 else ('afternoon' if local_now.hour < 17 else 'evening')
    return {
        'revenue': revenue,
        'order_count': order_count,
        'average_order': average_order,
        'month_revenue': month_revenue,
        'growth': growth,
        'customer_count': get_user_model().objects.filter(orders__isnull=False).distinct().count(),
        'product_count': Product.objects.count(),
        'stock_units': Product.objects.aggregate(value=Sum('stock_quantity'))['value'] or 0,
        'low_stock_count': low_stock.count(),
        'low_stock': low_stock[:5],
        'orders_today': Order.objects.filter(created_at__date=today).count(),
        'attention_count': Order.objects.filter(status__in=['confirmed', 'shipped']).count(),
        'monthly_sales': monthly_sales,
        'chart_points': chart_points,
        'status_data': status_data,
        'status_gradient': ', '.join(gradient_parts),
        'top_products': top_products,
        'recent_orders': Order.objects.select_related('user').prefetch_related('items')[:7],
        'generated_at': local_now,
        'greeting': greeting,
    }

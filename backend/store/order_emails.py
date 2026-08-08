import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from .models import Order, OrderEmailLog

logger = logging.getLogger(__name__)


def send_order_confirmation(order_id):
    """Send and audit a customer order-confirmation email.

    Delivery failures are recorded for staff and never invalidate an order that
    has already been committed to the database.
    """
    order = (
        Order.objects.select_related('user', 'payment')
        .prefetch_related('items')
        .get(pk=order_id)
    )
    subject = f'NazRiy order #{order.id} confirmed'
    context = {
        'order': order,
        'items': order.items.all(),
        'store_url': settings.FRONTEND_URL.rstrip('/'),
    }
    message = EmailMultiAlternatives(
        subject=subject,
        body=render_to_string('email/order_confirmation.txt', context),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[order.email],
        reply_to=[settings.EMAIL_HOST_USER] if settings.EMAIL_HOST_USER else None,
    )
    message.attach_alternative(
        render_to_string('email/order_confirmation.html', context),
        'text/html',
    )

    try:
        message.send(fail_silently=False)
    except Exception as exc:  # The order must remain valid if SMTP is unavailable.
        OrderEmailLog.objects.create(
            order=order,
            recipient=order.email,
            subject=subject,
            status='failed',
            error_message=str(exc)[:500],
        )
        logger.exception('Order confirmation email failed for order %s.', order.id)
        return False

    OrderEmailLog.objects.create(
        order=order,
        recipient=order.email,
        subject=subject,
        status='sent',
    )
    return True

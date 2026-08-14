from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from django.utils import timezone

from .models import DiscountCampaign, Order


MONEY = Decimal('0.01')
FREE_DELIVERY_THRESHOLD = Decimal('2000.00')
STANDARD_DELIVERY_CHARGE = Decimal('80.00')


class DiscountValidationError(ValueError):
    pass


@dataclass(frozen=True)
class DiscountQuote:
    campaign: DiscountCampaign
    code: str
    discount_amount: Decimal
    delivery_charge: Decimal
    total: Decimal


def money(value):
    return Decimal(value).quantize(MONEY, rounding=ROUND_HALF_UP)


def delivery_charge_for(subtotal):
    return Decimal('0.00') if subtotal >= FREE_DELIVERY_THRESHOLD else STANDARD_DELIVERY_CHARGE


def quote_discount(*, code, subtotal, user, lock=False):
    normalized = str(code or '').strip().upper()
    if not normalized:
        raise DiscountValidationError('Enter a promo code.')

    campaigns = DiscountCampaign.objects
    if lock:
        campaigns = campaigns.select_for_update()
    try:
        campaign = campaigns.get(discount_code__iexact=normalized)
    except DiscountCampaign.DoesNotExist as error:
        raise DiscountValidationError('This promo code is invalid.') from error

    now = timezone.now()
    if not campaign.active:
        raise DiscountValidationError('This promo code is not active.')
    if campaign.starts_at and campaign.starts_at > now:
        raise DiscountValidationError('This promo code is not active yet.')
    if campaign.ends_at and campaign.ends_at < now:
        raise DiscountValidationError('This promo code has expired.')

    subtotal = money(subtotal)
    if subtotal < campaign.minimum_order_amount:
        shortfall = money(campaign.minimum_order_amount - subtotal)
        raise DiscountValidationError(f'Add ৳{shortfall:,.2f} more to use this promo code.')

    used_orders = campaign.orders.exclude(status='cancelled')
    if campaign.usage_limit is not None and used_orders.count() >= campaign.usage_limit:
        raise DiscountValidationError('This promo code has reached its usage limit.')
    if user and campaign.per_customer_limit and used_orders.filter(user=user).count() >= campaign.per_customer_limit:
        raise DiscountValidationError('You have already used this promo code.')

    delivery = delivery_charge_for(subtotal)
    if campaign.discount_type == 'free_delivery':
        discount = delivery
    elif campaign.discount_type == 'fixed':
        discount = min(money(campaign.discount_value), subtotal)
    else:
        discount = money(subtotal * campaign.discount_value / Decimal('100'))
        if campaign.maximum_discount_amount is not None:
            discount = min(discount, money(campaign.maximum_discount_amount))

    if discount <= 0:
        raise DiscountValidationError('This promo code does not apply to the current order.')
    total = money(subtotal + delivery - discount)
    if total <= 0:
        raise DiscountValidationError('This promo code would reduce the payable total to zero. Contact NazRiy for assistance.')
    return DiscountQuote(
        campaign=campaign,
        code=campaign.discount_code.upper(),
        discount_amount=money(discount),
        delivery_charge=money(delivery),
        total=total,
    )

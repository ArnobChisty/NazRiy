"""Server-side client for bKash Tokenized Checkout.

All credentials and provider calls remain in Django. The browser only receives
the hosted bKash checkout URL returned by the create-payment operation.
"""

import json
from hashlib import sha256
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.cache import cache


class BkashGatewayError(Exception):
    pass


class BkashGateway:
    REQUIRED_SETTINGS = (
        'BKASH_GATEWAY_APP_KEY',
        'BKASH_GATEWAY_APP_SECRET',
        'BKASH_GATEWAY_USERNAME',
        'BKASH_GATEWAY_PASSWORD',
    )

    @classmethod
    def configured(cls):
        return bool(
            settings.BKASH_GATEWAY_ENABLED
            and all(getattr(settings, name, '') for name in cls.REQUIRED_SETTINGS)
        )

    def __init__(self):
        if not self.configured():
            raise BkashGatewayError('Automated bKash checkout is not configured.')
        self.base_url = settings.BKASH_GATEWAY_BASE_URL
        self.timeout = settings.BKASH_GATEWAY_TIMEOUT

    def _request(self, path, payload, headers=None):
        request_headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        request_headers.update(headers or {})
        request = Request(
            f'{self.base_url}{path}',
            data=json.dumps(payload).encode('utf-8'),
            headers=request_headers,
            method='POST',
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                body = response.read().decode('utf-8')
        except HTTPError as error:
            try:
                provider_message = json.loads(error.read().decode('utf-8')).get('statusMessage')
            except (ValueError, AttributeError):
                provider_message = None
            raise BkashGatewayError(provider_message or 'bKash rejected the payment request.') from error
        except (URLError, TimeoutError, OSError) as error:
            raise BkashGatewayError('The bKash payment service is temporarily unavailable.') from error

        try:
            result = json.loads(body)
        except ValueError as error:
            raise BkashGatewayError('bKash returned an invalid response.') from error
        if not isinstance(result, dict):
            raise BkashGatewayError('bKash returned an invalid response.')
        return result

    def _token(self):
        identity = sha256(
            f'{settings.BKASH_GATEWAY_ENVIRONMENT}:{settings.BKASH_GATEWAY_APP_KEY}'.encode('utf-8')
        ).hexdigest()[:24]
        cache_key = f'nazriy:bkash-token:{identity}'
        token = cache.get(cache_key)
        if token:
            return token

        response = self._request('/token/grant', {
            'app_key': settings.BKASH_GATEWAY_APP_KEY,
            'app_secret': settings.BKASH_GATEWAY_APP_SECRET,
        }, {
            'username': settings.BKASH_GATEWAY_USERNAME,
            'password': settings.BKASH_GATEWAY_PASSWORD,
        })
        token = response.get('id_token')
        if not token:
            raise BkashGatewayError(response.get('statusMessage') or 'bKash authentication failed.')
        try:
            lifetime = max(60, min(int(response.get('expires_in', 3600)) - 60, 3500))
        except (TypeError, ValueError):
            lifetime = 3500
        cache.set(cache_key, token, timeout=lifetime)
        return token

    def _authenticated_request(self, path, payload):
        return self._request(path, payload, {
            'Authorization': self._token(),
            'X-APP-Key': settings.BKASH_GATEWAY_APP_KEY,
        })

    def create_payment(self, *, amount, invoice, payer_reference, callback_url):
        return self._authenticated_request('/create', {
            'mode': '0011',
            'payerReference': payer_reference,
            'callbackURL': callback_url,
            'amount': f'{amount:.2f}',
            'currency': 'BDT',
            'intent': 'sale',
            'merchantInvoiceNumber': invoice,
        })

    def execute_payment(self, payment_id):
        return self._authenticated_request('/execute', {'paymentID': payment_id})

    def query_payment(self, payment_id):
        return self._authenticated_request('/payment/status', {'paymentID': payment_id})

    def verify_completed_payment(self, payment_id):
        executed = self.execute_payment(payment_id)
        if self.is_completed(executed):
            return executed
        queried = self.query_payment(payment_id)
        if self.is_completed(queried):
            return queried
        message = queried.get('statusMessage') or executed.get('statusMessage')
        raise BkashGatewayError(message or 'bKash has not confirmed this payment.')

    @staticmethod
    def is_completed(payload):
        return (
            str(payload.get('statusCode', '')) == '0000'
            and str(payload.get('transactionStatus', '')).lower() == 'completed'
        )


def safe_provider_payload(payload):
    """Persist useful audit fields without tokens, credentials, or customer secrets."""
    allowed = {
        'paymentID', 'trxID', 'transactionStatus', 'amount', 'currency',
        'intent', 'merchantInvoiceNumber', 'paymentExecuteTime',
        'statusCode', 'statusMessage',
    }
    return {key: payload[key] for key in allowed if key in payload}

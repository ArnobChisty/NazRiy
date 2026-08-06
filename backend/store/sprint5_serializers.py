from rest_framework import serializers

from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    method_label = serializers.CharField(source='get_method_display', read_only=True)
    status_label = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'method', 'method_label', 'amount', 'status', 'status_label',
            'provider_reference', 'failure_reason', 'attempts', 'created_at', 'updated_at',
        ]


class PaymentActionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['submit', 'cancel'])
    transaction_id = serializers.RegexField(
        r'^[A-Za-z0-9]{8,32}$',
        required=False,
        trim_whitespace=True,
        error_messages={
            'invalid': 'Enter a valid bKash transaction ID using 8–32 letters and numbers.',
        },
    )
    request_id = serializers.UUIDField()

    def validate(self, attrs):
        if attrs['action'] == 'submit' and not attrs.get('transaction_id'):
            raise serializers.ValidationError({
                'transaction_id': 'The bKash transaction ID is required.',
            })
        return attrs

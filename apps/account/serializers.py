from rest_framework import serializers


class AmountSerializer(serializers.Serializer):
    amount = serializers.IntegerField(min_value=1)

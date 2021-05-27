from django.conf import settings
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Account
from .serializers import AmountSerializer
from .tasks import notify_balance
from .exceptions import NotEnoughPointsError
from .helpers import get_object_or_404


class GetCustomerBalanceAPIView(APIView):

    def get(self, request, customer, service):
        account = get_object_or_404(Account, customer_id=customer, service_id=service, is_active=True)
        return Response({'detail': account.balance}, status=status.HTTP_200_OK)


class IncreaseCustomerBalanceAPIView(APIView):
    serializer_class = AmountSerializer

    def post(self, request, customer, service):
        account = get_object_or_404(Account, customer_id=customer, service_id=service, is_active=True)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = serializer.validated_data['amount']
        account.balance_increase(amount)
        account.date_increase = timezone.now()
        account.save()
        if account.balance >= settings.MAX_BALANCE_VALUE:
            notify_balance.delay(account.balance, customer, service)
        return Response({'detail': account.balance}, status=status.HTTP_200_OK)


class DecreaseCustomerBalanceAPIView(APIView):
    serializer_class = AmountSerializer

    def post(self, request, customer, service):
        account = get_object_or_404(Account, customer_id=customer, service_id=service, is_active=True)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        amount = serializer.validated_data['amount']
        try:
            account.balance_decrease(amount)
            account.date_decrease = timezone.now()
            account.save()
        except NotEnoughPointsError as error:
            return Response({'detail': f'Error: {error}'}, status=status.HTTP_400_BAD_REQUEST)
        if account.balance <= settings.MIN_BALANCE_VALUE:
            notify_balance.delay(account.balance, customer, service)
        return Response({'detail': account.balance}, status=status.HTTP_200_OK)

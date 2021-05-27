from django.db import models
from django.conf import settings

from .managers import ActiveAccountsManager
from .exceptions import NegativeAmountError, NotEnoughPointsError


class Account(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    service = models.ForeignKey('Service', on_delete=models.CASCADE)
    balance = models.PositiveIntegerField(default=0, blank=True)
    date_increase = models.DateTimeField(null=True, blank=True)
    date_decrease = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, blank=True)
    is_active = models.BooleanField(default=True, blank=True)

    objects = models.Manager()
    active = ActiveAccountsManager()

    def balance_increase(self, amount):
        if not isinstance(amount, int):
            raise TypeError('Pass integer as amount')
        if amount <= 0:
            raise NegativeAmountError('Pass integer value more than 0')
        self.balance += amount

    def balance_decrease(self, amount):
        if not isinstance(amount, int):
            raise TypeError('Pass integer as amount')
        if amount <= 0:
            raise NegativeAmountError('Pass integer value more than 0')
        if self.balance < amount:
            raise NotEnoughPointsError('Not enough points')
        self.balance -= amount

    class Meta:
        ordering = ['-date_increase', '-date_decrease']


class NameCreatedModelMixin(models.Model):
    name = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True, blank=True)

    class Meta:
        abstract = True


class Service(NameCreatedModelMixin):
    description = models.TextField()
    client = models.ForeignKey('Client', on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'client'], name='unique_client_service'),
        ]


class Client(NameCreatedModelMixin):
    email = models.EmailField(max_length=254)


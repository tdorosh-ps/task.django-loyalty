from datetime import timedelta

from django.utils import timezone
from django.contrib.auth import get_user_model

from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from oauth2_provider.models import AccessToken

from ..models import Account, Service, Client


User = get_user_model()


class AccountAPIViewsTests(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client.objects.create(name='Test_Client', email='test_client_email')
        cls.service = Service.objects.create(name='Test_Service', description='test_descr', client=cls.client)
        cls.user = User.objects.create(username='test_user', password='test_password')
        cls.token = AccessToken.objects.create(token='access_token', scope='read write',
                                               expires=timezone.now() + timedelta(days=1))
        cls.api_client = APIClient()
        cls.api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + cls.token.token)

    def setUp(self):
        super().setUp()
        self.account = Account.objects.create(customer=self.user, service=self.service, balance=100)

    def test_get_customer_balance(self):
        response = self.api_client.get(reverse('accounts:balance_get', args=[self.user.id, self.service.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], self.account.balance)

    def test_increase_customer_balance(self):
        initial_balance = self.account.balance
        data = {'amount': 50}
        response = self.api_client.post(reverse('accounts:balance_increase',
                                                args=[self.user.id, self.service.id]), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.account.refresh_from_db()
        self.assertEqual(response.data['detail'], self.account.balance)
        self.assertEqual(self.account.balance, initial_balance + data['amount'])

    def test_decrease_customer_balance_failed(self):
        initial_balance = self.account.balance
        data = {'amount': 150}
        self.assertLess(initial_balance, data['amount'])
        response = self.api_client.post(reverse('accounts:balance_decrease',
                                                args=[self.user.id, self.service.id]), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.account.balance, initial_balance)

    def test_decrease_customer_balance_successful(self):
        initial_balance = self.account.balance
        data = {'amount': 50}
        self.assertLess(data['amount'], initial_balance)
        response = self.api_client.post(reverse('accounts:balance_decrease',
                                                args=[self.user.id, self.service.id]), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.account.refresh_from_db()
        self.assertEqual(response.data['detail'], self.account.balance)
        self.assertEqual(self.account.balance, initial_balance - data['amount'])

    def tearDown(self):
        self.account.delete()
        super().tearDown()

    @classmethod
    def tearDownClass(cls):
        cls.api_client.force_authenticate(token=None)
        cls.token.delete()
        cls.user.delete()
        cls.service.delete()
        cls.client.delete()
        super().tearDownClass()

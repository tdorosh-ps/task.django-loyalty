from django.test import TestCase
from django.contrib.auth import get_user_model

from ..models import Account, Service, Client
from ..exceptions import NegativeAmountError, NotEnoughPointsError


User = get_user_model()


class AccountModelTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client.objects.create(name='Test_Client', email='test_client_email')
        cls.service = Service.objects.create(name='Test_Service', description='test_descr', client=cls.client)
        cls.user = User.objects.create(username='test_user', password='test_password')

    def setUp(self):
        super().setUp()
        self.account = Account.objects.create(customer=self.user, service=self.service, balance=100)

    # Test balance_increase method
    def test_balance_increase_with_negative_amount(self):
        initial_balance = self.account.balance
        self.assertRaises(NegativeAmountError, self.account.balance_increase, -100)
        self.assertEqual(self.account.balance, initial_balance)

    def test_balance_increase_with_zero_amount(self):
        initial_balance = self.account.balance
        self.assertRaises(NegativeAmountError, self.account.balance_increase, 0)
        self.assertEqual(self.account.balance, initial_balance)

    def test_balance_increase_with_not_int_amount(self):
        initial_balance = self.account.balance
        self.assertRaises(TypeError, self.account.balance_increase, 'amount')
        self.assertEqual(self.account.balance, initial_balance)

    def test_balance_increase_with_positive_amount(self):
        initial_balance = self.account.balance
        increase_amount = 45
        self.account.balance_increase(increase_amount)
        self.assertEqual(self.account.balance, initial_balance + increase_amount)

    # Test balance_decrease method
    def test_balance_decrease_with_amount_grater_than_initial(self):
        initial_balance = self.account.balance
        decrease_amount = self.account.balance + 50
        self.assertLess(initial_balance, decrease_amount)
        self.assertRaises(NotEnoughPointsError, self.account.balance_decrease, decrease_amount)
        self.assertEqual(self.account.balance, initial_balance)

    def test_balance_decrease_with_the_same_amount_as_initial(self):
        initial_balance = decrease_amount = self.account.balance
        self.assertEqual(decrease_amount, initial_balance)
        self.account.balance_decrease(decrease_amount)
        self.assertEqual(self.account.balance, 0)

    def test_balance_decrease_with_amount_less_than_initial(self):
        initial_balance = self.account.balance
        decrease_amount = self.account.balance - 40
        self.assertGreater(initial_balance, decrease_amount)
        self.account.balance_decrease(decrease_amount)
        self.assertEqual(self.account.balance, initial_balance - decrease_amount)

    def tearDown(self):
        self.account.delete()
        super().tearDown()

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        cls.service.delete()
        cls.client.delete()
        super().tearDownClass()


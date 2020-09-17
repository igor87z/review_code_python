from django.test import TestCase
from django.contrib.auth.models import User
from .exceptions import TransactionNotExecute, MoneyNotEnough
from .models import UserFinance

class TestTransaction(TestCase):
    """Тестирование класса транзакции"""

    def setUp(self):
        """Подготовка данных для тестирования"""
        self.user_1 = User.objects.create_user(username='user #1', password='qwerty')
        self.user_2 = User.objects.create_user(username='user #2', password='qwerty')
        self.user_3 = User.objects.create_user(username='user #3', password='qwerty')
        self.user_finance_1 = UserFinance.objects.create(user=self.user_1, inn=123, balance=100)
        self.user_finance_2 = UserFinance.objects.create(user=self.user_2, inn=134, balance=10)
        self.user_finance_3 = UserFinance.objects.create(user=self.user_3, inn=134, balance=20)

    def test_donor(self):
        """Проверка функции поиска отправителя"""
        transaction = Transaction(self.user_1.id, 100, 134)
        self.assertEqual(donor, transaction.donor())

    def test_recepients(self):
        """Проверка функции поиска получателей"""
        transaction = Transaction(self.user_1.id, 100, 134)
        self.assertEqual([self.user_finance_2, self.user_finance_3], transaction.recepients())

    def test_not_enough_money(self):
        """Проверка исключения при перерводе сумма большей, чем баланс отправителя"""
        transaction = Transaction(self.user_1.id, 1000, 134)
        with self.assertRaises(MoneyNotEnough):
            transaction.action()

    def test_not_exists_recepients(self):
        """Проверка исключения при перерводе не существующим получателям"""
        transaction = Transaction(self.user_1.id, 100, 127)
        with self.assertRaises(TransactionNotExecute):
            transaction.action()

    def test_transaction(self):
        """Проверка проведения платежа"""
        transaction = Transaction(self.user_1.id, 100, 134)
        transaction.action()
        assertEqual(UserFinance.objects.get(id=self.user_1.id).balance, 0)
        assertEqual(UserFinance.objects.get(id=self.user_2.id).balance, 60)
        assertEqual(UserFinance.objects.get(id=self.user_3.id).balance, 70)

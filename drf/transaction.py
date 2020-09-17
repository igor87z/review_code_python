"""Модуль транзакции"""

from decimal import Decimal

from .exceptions import TransactionNotExecute, MoneyNotEnough
from .models import UserFinance


class Transaction:
    """Transaction переводит средства между счетами пользователей"""

    def __init__(self, user_from_id, amount, inn):
        super(Transaction, self).__init__()
        self.user_from_id = user_from_id
        self.amount = amount
        self.inn = inn

    def donor(self):
        """Пользователь, со счета которого переводятся средства. Выбирается по идентифактору"""
        return UserFinance.objects.get(id=self.user_from_id)

    def recepients(self):
        """Пользователи, на счета которых переводятся средства. Выбираются по ИНН"""
        return UserFinance.objects.filter(inn=self.inn)

    def make_payment(self, user, amount):
        """Зачисление(если amount положительное) или вычетание(если amount отрицательное)
        средств на счет/со счета пользователя"""
        user.account += amount
        user.save()

    def make_trasactions(self, donor, recepients, amount):
        """Проведение транзакции: со счета donor списывается сумма amount
        и распределяется в равных долях между всеми recepients(получаетлями), найденными ИНН"""
        sum_part = round(amount / len(recepients), 2)
        self.make_payment(donor, -amount)
        for user in recepients:
            self.make_payment(user, sum_part)

    def action(self):
        """Проведение транзакции: поиск отправителя, получателей и перевод средств"""
        donor = self.donor()
        recepients = self.recepients()

        if not donor or not recepients:
            raise TransactionNotExecute()

        if donor.amount < self.amount:
            raise MoneyNotEnough()

        self.make_trasactions(donor, recepients, Decimal(self.amount))

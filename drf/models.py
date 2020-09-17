"""Модуль моделей для БД"""

from django.contrib.auth.models import User
from django.db import models


class UserFinance(models.Model):
    """Финансовая информация пользователя: ИНН и баланс"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    inn = models.IntegerField(verbose_name='ИНН')
    balance = models.FloatField(verbose_name='Баланс')

    def __str__(self):
        return f'{self.id} {self.inn}'

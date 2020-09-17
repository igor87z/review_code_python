"""Модуль сериализаторов"""

from rest_framework import serializers
from .models import UserFinance


class CashierCheck(serializers.Serializer):
    """Сериализатор для проведения транзакции: отправитель, ИНН получателей и сумма"""
    user_from = serializers.PrimaryKeyRelatedField(queryset=UserFinance.objects.all())
    inn_to = serializers.IntegerField()
    amount = serializers.DecimalField()

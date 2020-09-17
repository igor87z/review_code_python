"""Модуль вьюшек для обработки запросов"""

from rest_framework import viewsets, permissions
from rest_framework.response import Response

from .serializers import CashierCheck
from .tarnsaction import Transaction


class Cashbox(viewsets.ViewSet):
    """Класс для обработки запросов проведения платежей."""
    permission_classes = (permissions.AllowAny,)
    serializer_class = CashierCheck

    def create(self, request):
        """Проведение платежа"""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(True)

        try:
            transaction = Transaction(request.data['user_from'],
                                      request.data['amount'],
                                      request.data['inn_to'])
            transaction.action()
        except MoneyNotEnough:
            response = 'На счёте недостаточно средств'
        except TransactionNotExecute:
            response = 'Перевод не выполнен'
        except Exception:
            response = 'Ошибка'
        else:
            response = serializer.data

        return Response(response)

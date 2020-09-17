"""Модуль классов ошибок"""


class TransactionNotExecute(Exception):
    """Ошибка должна инициироваться, когда транзакция по каким-либо причинам
    не может быть выполнена, например, не найден отправитель или получатели платежа"""
    def __init__(self):
        super(TransactionNotExecute, self).__init__()


class MoneyNotEnough(TransactionNotExecute):
    """Ошибка должна инициироваться, когда на балансе отправителя недостаточно
    средств для совершения платежа"""
    def __init__(self):
        super(MoneyNotEnough, self).__init__()

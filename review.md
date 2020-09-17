# Общая критика

- Нет комментариев к методам, классам и модулям. Кода, конечно, немного и многое и так понятно, но все же минус.

- Я бы использовал аннотации типов и модуль typing в купе с mypy и pylint.

# Django REST Framework, drf/

## models.py

- Имя класса Users не подходящее. Обычно используется единственное число, во-первых. Во-вторых, название не отражает сути, что именно в данном классе/модели хранится. Предлагаю: UserFinance.

- Для поля user verbose_name выбран не подходящий. Лучше будет: Пользователь.

- Для поля account я бы использовал DecimalField, а не FloatField. Decimal более подходящий тип для хранения финансовой информации. Так же выбор наименования, я склоняюсь к balance вместо account. В verbose_name лучше написать: Баланс.

- Метод \_\_str\_\_. Не указана точная версия Python. Если 3.6+, я бы склонилися к f-строкам:
```python
	return f'{self.id} {self.inn}'
```
Если же должно работать на более ранних версиях интерпритатора, то убрать перевод self.id к str:
```python
	return '{id} {inn}'.format(id=self.id, inn=self.inn)
```
не совсем ясна необходимость использования именованных параметров, я бы оставил просто
```python
	return '{} {}'.format(self.id, self.inn)
```
строка небольшая и легко читается в таком варианте. Повторений, которые так же могли обосновать использование именованных параметров, нет.

- Оформление кода: лишние пробелы после знака равенства/оператора присвоения(не соответствует PEP8):
```python
user =      models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Юзер')
inn =       models.IntegerField(verbose_name='ИНН')
account =   models.FloatField(verbose_name='Счёт')
```
лучше один пробел:
```python
user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Юзер')
inn = models.IntegerField(verbose_name='ИНН')
account = models.FloatField(verbose_name='Счёт')
```


## serializers.py

- Поле inn_to. Вот здесь я не совсем понял: в условии задачи "Поле для ввода ИНН пользователей, на счета которых будут переведены деньги", ИНН во множественом числе или нет? Если да, то:
```python
	serializers.ListField(
		child=serializers.IntegerField()
	)
```

- Поле amount, я бы использовал DecimalField

- Оформление кода: лишние пробелы перед знаком равенства/оператором присвоения(не соответствует PEP8):
```python
user_from = serializers.PrimaryKeyRelatedField(queryset=Users.objects.all())
inn_to    = serializers.IntegerField()
amount    = serializers.FloatField()
```
лучше один пробел:
```python
user_from = serializers.PrimaryKeyRelatedField(queryset=Users.objects.all())
inn_to = serializers.IntegerField()
amount = serializers.FloatField()
```

- Оформление кода: между последним import'ом(```from .models import Users```) и классом(```class TransferSerializer(serializers.Serializer):```) только одна пустая строка, по PEP8 положено 2


## tests.py

- Нет тестов

## urls.py


## views.py

- Порядок import я бы переписал так(от общего к частному: Django -> DRF -> проект):
```python
from django.contrib.auth.models import User
from rest_framework import viewsets, permissions
from rest_framework.response import Response

from .serializers import TransferSerializer
from .models import Users
```


- Метод create получился довольно большим. Я считаю, что, во-первых, нужно разбить на ряд методов: 1) получение и проверка данных из post-запроса; 2) поиск пользователя, со счета которого переводим; 3) поиск пользователей, которым зачисляем; 4) перевод. При этом в TransferViewSet оставил бы только (1). 2 - 4 вынести в отдельный класс.
- Преобразование к float значения amount я бы заменил на Decimal.
- Не совсем ясна необходимость инициализации 0 переменной sum_part. Ниже задается значение. Именно это нулевое значение ни разу не используется.
```python
sum_part = 0
```

- Так же не понятно почему, если не удалось найти запись в Users(не будем сейчас учитывать мою критику models.py), возвращается 'На счёте недостаточно средств':
```python
# ищем сумму на счёте пользователя
us = user_from.users_set.all()

if us:
	# ...
else:
    acc_sum = 0
    return Response('На счёте недостаточно средств')
```

- Когда с баланса донора вычитаем сумму платежа, логичнее использовать ```amount``` вместо ```sum_part * users_count```
```python
result_sum = float(res_user.account) - sum_part * users_count
# =>
result_sum = float(res_user.account) - amount
```

- Сделал бы примерно так(не учитываем критику models.py):
```python
# views.py

from rest_framework import viewsets, permissions
from rest_framework.response import Response
from django.contrib.auth.models import User

from .serializers import TransferSerializer
from .models import Users
from .transaction import *

class TransferViewSet(viewsets.ViewSet):
	permission_classes = (permissions.AllowAny,)
	serializer_class = TransferSerializer

	def create(self, request):
		serializer = self.serializer_class(data=request.data)
		#  Не стал заносить в try, так как не понятно: должно ли падать исключение с 400 возвратом или нет. Опять к общей критике: нет комментариев.
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


# transaction.py

from decimal import Decimal


class TransactionNotExecute(Exception):
	def __init__(self):
		super(TransactionNotExecute, self).__init__()


class MoneyNotEnough(Exception):
	def __init__(self):
		super(ClassName, self).__init__()
		

class Transaction:
	"""Transaction переводит средства между счетами пользователей"""

	def __init__(self, user_from_id, amount, inn):
		super(Transaction, self).__init__()
		self.user_from_id = user_from_id
		self.amount = Decimal(amount)
		self.inn = inn

	def donor(self):
		return Users.objects.get(id=self.user_from_id)

	def recepients(self):
		return Users.objects.filter(inn=self.inn)

	def make_payment(self, user, amount):
		user.account += amount
		user.save()

	def make_trasactions(self, donor, recepients, amount):
		sum_part = round(self.amount / len(recepients), 2)
		self.make_payment(donor, -self.amount)
		for user in recepients:
			self.make_payment(user, sum_part)

	def action(self):
		donor = self.donor()
		recepients = self.recepients()

		if not donor or not recepients:
			raise TransactionNotExecute()

		if donor.amount < self.amount:
			raise MoneyNotEnough()

		self.make_trasactions(donor, recepients, amount)
```

- Имя TransferViewSet на мой взгляд избыточно, "ViewSet" я бы отрезал, то есть остается Transfer и его бы вероятно сменил на Cashier или Cashbox.

# Django, django/

## forms.py

- Оформление кода: между последним import'ом(```from .models import Users```) и классом(```class TransferForm(forms.Form):```) только одна пустая строка, по PEP8 положено 2

- Оформление кода: лишние пробелы перед знаком равенства/оператором присвоения(не соответствует PEP8):
```python
user_from  = forms.ModelChoiceField(queryset=Users.objects.all(), empty_label='От кого')
inn_to      = forms.IntegerField(label='Кому')
amount      = forms.FloatField()
```
лучше один пробел:
```python
user_from = forms.ModelChoiceField(queryset=Users.objects.all(), empty_label='От кого')
inn_to = forms.IntegerField(label='Кому')
amount = forms.FloatField()
```

- Для поля amount я бы использовал DecimalField, а не FloatField. Decimal более подходящий тип для хранения финансовой информации. Для amount не указан label.

- Метод \_\_str\_\_. Не указана точная версия Python. Если 3.6+, я бы склонилися к f-строкам:
```python
	return f'{self.id} {self.inn}'
```
Если же должно работать на более ранних версиях интерпритатора, то убрать перевод self.id к str:
```python
	return '{id} {inn}'.format(id=self.id, inn=self.inn)
```
не совсем ясна необходимость использования именованных параметров, я бы оставил просто
```python
	return '{} {}'.format(self.id, self.inn)
```
строка небольшая и легко читается в таком варианте. Повторений, которые так же могли обосновать использование именованных параметров, нет.

## models.py

- Оформление кода: лишние пробелы после знака равенства/оператора присвоения(не соответствует PEP8):
```python
user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Юзер')
inn = models.IntegerField(verbose_name='ИНН')
account = models.FloatField(verbose_name='Счёт')
```
лучше один пробел:
```python
user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Юзер')
inn = models.IntegerField(verbose_name='ИНН')
account = models.FloatField(verbose_name='Счёт')
```

- Метод \_\_str\_\_. Не указана точная версия Python. Если 3.6+, я бы склонилися к f-строкам:
```python
	return f'{self.id} {self.inn}'
```
Если же должно работать на более ранних версиях интерпритатора, то убрать перевод self.id к str:
```python
	return '{id} {inn}'.format(id=self.id, inn=self.inn)
```
не совсем ясна необходимость использования именованных параметров, я бы оставил просто
```python
	return '{} {}'.format(self.id, self.inn)
```
строка небольшая и легко читается в таком варианте. Повторений, которые так же могли обосновать использование именованных параметров, нет.

- Поле user, неудачный verbose_name. Я считаю, что нужно остановиться либо на англоязычном "User", либо переводе "Пользователь". Транслит неудачный вариант.

- Для поля account я бы использовал DecimalField, а не FloatField. Decimal более подходящий тип для хранения финансовой информации. Наименование поля тоже не совсем удачной на мой взгляд, выбрал бы balance. verbose_name тоже не очень, я бы выбрал "Баланс", в "Счет" ожидаешь увидеть номер счета, например, но не сумму.

## tests.py

- Нет тестов

## views.py

- Порядок import я бы переписал так(от общего к частному: Django -> DRF -> проект):
```python
from django.contrib.auth.models import User
from django.views.generic.edit import FormView
from .models import Users
from .forms import TransferForm
```

- Лишняя пустая строка:
```python
class TransferView(FormView):
    
    form_class = TransferForm
```
Аналогично в методе get:
```python
ctx['userlist'] = self.userlist()

return self.render_to_response(ctx)
```
Аналогичные случаи в других методах из этого же файла выделяют логические блоки. Приведенные выше 2 случая на мой взгляд этого не делают.

- Метод post очень большой и в него затянута бизнес-логика. Надо разбить аналогично TransferViewSet из views.py из drf.

- Использование ```sum_part * users_count``` вместо amount. В общем, таже критика, что и views.py из drf.

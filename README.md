Это пет проект в котором я создал Django приложение с основным функционалом финансовой биржи:
1. Регистрация, авторизация
2. Выставление сделок
3. Торговый стакан

Также реализована симуляция торгов с помощью запросов в API. Подключение пользователя происходит с помощью websocket, все транзакции отображаются в релаьном времени.

Для запуска симуляции торгов:
```
from services.broker_service import *
create_deposits(100)
start_trading()
```


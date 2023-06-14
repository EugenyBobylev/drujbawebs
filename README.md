Файл переменных окружения называется .env
базовый url это BASE_URL
путь ка шаблонам jinja2 это TEMPLATES_DIR


#### requirements
```shell
pip install --upgrade pip
pip install aiogram
pip install python-dotenv
pip install fastapi
pip install uvicorn
pip install SQLAlchemy
pip install psycopg2-binary
pip install alembic
pip install pytest
pip install pytest-asyncio
pip install requests
pip install jinja2
pip install telethon
```

**Create new Revision**
```shell
alembic revision --autogenerate -m "..."
```
**Running migration:**
```shell
alembic upgrade head
```
**Running uvicorn:**
```shell
uvicorn backend.api:app --forwarded-allow-ips='*' --uds /tmp/uvicorn.sock
```

в тестовой среде можно для работы системы нужно запустить
 - start_api.py   (FastAPI)
 - start_bot.py   (Aiogram 2.x)
что бы вебаппы нормально работали в тестовой среде необходимо 
использовать какой-либо сервис для проброса из вне на 127.0.0.1
я использую ngrock

База данных postgres запускается в контейнере см. docker-compose.yml

Тарифы:
1. Пробный тариф - бесплатный при первом входе
2. Знакомый - от 1 до 5 сборов 250 ₽ за сбор
3. Приятель - от 6 до 49 сборов 200 ₽ за сбор
4. Напарник-  от 50 до 99 150 ₽ за сбор
5. Лучший друг - от 100 сборов и более 100 ₽ за сбор



прокси для аккаунтов с которых создаются чаты должны прописываться
в файлах json


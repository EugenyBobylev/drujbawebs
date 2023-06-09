Файл переменных окружения называется .env
базовый url это BASE_URL
путь к шаблонам jinja2 это TEMPLATES_DIR

структура:
 - **alembic**           инф. для миграции БД
- **backend**            FastApi (работа с webapp)
- **backend/templates**  шаблоны html тут должны лежать в итоге, сейчас лежат голые html без верстки
- **backend/new_templates**  шаблоны с версткой, сейчас переносится логика из шаблонов лежащих в template
- **backend/static**         статический контент html, по итогу вся статика должна быть тут
- **bot**      telegram bot
- **db**       модели для БД
- **logs**     логи
- **srv**      версии скриптов котоые используются на сервере, для информации
- **tests**    тесты (это не unit tests)         

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

** if you received message "alembic target database is not up to date"
```shell
alembic stamp head
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

**пересобрать контейнер и запустить в фоне**
```shell
docker-compose up -d --build
```

**поднять контейнер в фоне**
```shell
docker-compose up -d
```

**запуск/остановка работы контейнера**
```shell
docker-compose start
docker-compose stop
```

**Важно! После создания БД необходимо залить информацию в табл. text, запустив тест**
tests/bl_tests.py/test_init_texts_tbl()

Тарифы:
1. Пробный тариф - бесплатный при первом входе
2. Знакомый - от 1 до 5 сборов 250 ₽ за сбор
3. Приятель - от 6 до 49 сборов 200 ₽ за сбор
4. Напарник-  от 50 до 99 150 ₽ за сбор
5. Лучший друг - от 100 сборов и более 100 ₽ за сбор



прокси для аккаунтов с которых создаются чаты должны прописываться
в файлах json.

Если нужно вкл/выкл. создание чатов, то это делается в 
bl/start_fund(fund_id: int)


**ngrock win**

Authtoken saved to configuration file: C:\Users\xxx\AppData\Local/ngrok/ngrok.yml

**web-app routes**

| Route | web-app | html tempate |
| -- | -- | -- |
| /UserRegistration | webapp_1 | userRegistration.html |
| /CompanyRegistration | webapp_3 | companyRegistration2.html |

**вызовы api из web-app**

| web-app | html template | api route   | notes |
| -- | -- | --- | --- |
| webapp_1 | userRegistration.html | /api/user/  |
| webapp_3 | companyRegistration2.html | api/company/ | 


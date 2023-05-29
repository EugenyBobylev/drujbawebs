import os
from dataclasses import dataclass
from pathlib import Path


from dotenv import load_dotenv, dotenv_values


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Config(metaclass=SingletonMeta):
    def __init__(self):
        ok = load_dotenv('.env')
        # Telethon
        self.api_hash: str = os.getenv('API_HASH') if ok else None
        self.api_id: int = os.getenv('API_ID') if ok else None
        # telegram bot
        self.token: str = os.getenv('TOKEN') if ok else None
        # CloudPayments
        self.payment_username: str = os.getenv('PAYMENT_USERNAME') if ok else None
        self.payment_password: str = os.getenv('PAYMENT_PASSWORD') if ok else None
        # Postgres
        self.db: str = os.getenv('DB') if ok else None
        self.db_user = os.getenv('DB_USER') if ok else None
        self.db_password: str = os.getenv('DB_PASSWORD') if ok else None
        self.db_host: str = os.getenv('DB_GHOST') if ok else '127.0.0.1'
        self.db_port: int = os.getenv('DB_PORT') if ok else 5432
        # Fast API
        self.api_host: str = os.getenv('API_HOST') if ok else '127.0.0.1'
        self.base_url: str = os.getenv('BASE_URL') if ok else None

    def get_postgres_url(self):
        """
        Create url to connect to Postgres
        :return: url
        """
        user = self.db_user
        password = self.db_password
        host = self.db_host
        port = self.db_port
        db = self.db
        url = f"postgresql://{user}:{password}@{host}:{port}/{db}"
        return url
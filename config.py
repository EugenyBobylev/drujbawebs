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
        script_path = os.path.abspath(__file__)
        env_path = Path(script_path).parent / '.env'

        ok = load_dotenv(env_path)
        # Telethon
        self.api_hash: str = os.getenv('API_HASH')
        self.api_id: int = os.getenv('API_ID')
        # telegram bot
        self.token: str = os.getenv('TOKEN')
        # CloudPayments
        self.payment_username: str = os.getenv('PAYMENT_USERNAME')
        self.payment_password: str = os.getenv('PAYMENT_PASSWORD')
        # Postgres
        self.db: str = os.getenv('DB')
        self.db_user = os.getenv('DB_USER')
        self.db_password: str = os.getenv('DB_PASSWORD', None)
        self.db_host: str = os.getenv('DB_GHOST', '127.0.0.1')
        self.db_port: int = os.getenv('DB_PORT', 5432)
        # Fast API
        self.api_host: str = os.getenv('API_HOST', '127.0.0.1')
        self.base_url: str = os.getenv('BASE_URL')
        # Logging
        self.app_dir: str = str(Path(script_path).parent)
        self.logs_dir: str = os.getenv('LOGS_DIR', '')

        self.api_log_path = f'{self.app_dir}/{self.logs_dir}/api.log'
        self.bot_log_path = f'{self.app_dir}/{self.logs_dir}/bot.log'

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
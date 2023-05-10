import os
from dataclasses import dataclass
from pathlib import Path


from dotenv import load_dotenv, dotenv_values


@dataclass
class BotConfig:
    _instance: 'BotConfig' = None

    token: str = None
    payment_username: str = None
    payment_password: str = None
    db: str = None
    db_user = None
    db_password: str = None
    db_host: str = '127.0.0.1'
    db_port: int = 5432
    base_url: str = None

    def __init__(self):
        raise RuntimeError('Call instance() instead')

    @classmethod
    def instance(cls, env_filename: str = '.env') -> 'BotConfig':
        if cls._instance is None:
            script_path = os.path.abspath(__file__)
            env_path = Path(script_path).parent / '.env'
            cls._instance = cls.__new__(cls)
            if env_filename and env_path.exists():
                load_dotenv()
                env_config = dotenv_values(env_path)
                cls._instance.token = env_config['TOKEN']
                cls._instance.payment_username = env_config['PAYMENT_USERNAME']
                cls._instance.payment_password = env_config['PAYMENT_PASSWORD']
                cls._instance.db_host = env_config.get('DB_HOST', '127.0.0.1')
                cls._instance.db_port = env_config.get('DB_PORT', 5432)
                cls._instance.db = env_config['DB']
                cls._instance.db_user = env_config['DB_USER']
                cls._instance.db_password = env_config['DB_PASSWORD']
                cls._instance.base_url = env_config['BASE_URL']
        return cls._instance

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

from sqlalchemy import create_engine, Connection
from config import BotConfig


def test_connect_to_postgres():
    config = BotConfig.instance()
    url = config.get_postgres_url()
    engine = create_engine(url, pool_size=50, echo=False)
    assert engine is not None

    with engine.connect() as conn:
        assert conn is not None
        assert not conn.closed


def test_create_user():
    config = BotConfig.instance()
    url = config.get_postgres_url()
    print(url)

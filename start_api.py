import uvicorn

from backend.api import app
from config import BotConfig

if __name__ == '__main__':
    config = BotConfig.instance()
    uvicorn.run(app, host=config.api_host, port=8000)

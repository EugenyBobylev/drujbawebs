import uvicorn

from backend.api import app
from config import BotConfig

if __name__ == '__main__':
    uvicorn.run(app, host="localhost", port=8000)

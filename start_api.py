import uvicorn

from backend.api import app
from config import Config

if __name__ == '__main__':
    config = Config()
    uvicorn.run(app, host=config.api_host, port=8000)

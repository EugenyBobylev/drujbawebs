import urllib
import urllib.parse
from functools import wraps

import uvicorn
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware

from starlette.responses import Response

from config import BotConfig
from model import WebAppInitData
from utils import check_webapp_signature, decode_base64_str


class User(BaseModel):
    name: str
    timezone: int

    def __repr__(self):
        return f'name={self.name}; timezone={self.timezone}'


app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def auth(func):
    @wraps(func)
    def wrapper(*args, **kvargs):
        if 'authorization' in kvargs:
            authorization = kvargs['authorization']
            decoded_str = decode_base64_str(authorization)
            init_data = urllib.parse.unquote(decoded_str)
            if config.token is None:
                raise HTTPException(status_code=501, detail="BotConfig is unavailable")
            ok = check_webapp_signature(config.token, init_data)
            if not ok:
                raise HTTPException(status_code=401, detail="Query ID is wrong or user is not Unauthorized")
        result = func(*args, **kvargs)
        return result
    return wrapper


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get('/query/{query_id}')
async def get_query_id(query_id: str, response: Response):
    # response.headers["Allow-Origins"] = "*"
    # response.headers["Allow-Credentials"] = "true"
    # response.headers["Access-Control-Allow-Origin"] = "*"
    # response.headers["Access-Control-Allow-Headers"] = "origin, x-requested-with, content-type, authorization"
    # response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS,DELETE,PUT"
    return {
        'query_id': query_id,
        'message': 'Hello World',
    }


@app.post('/user/')
@auth
def create_new_user(user: User, authorization: str | None = Header(convert_underscores=True)):
    web_init = WebAppInitData.form_auth_header(authorization)
    return {
        'code': 200,
        'message': 'User successful created',
    }


if __name__ == '__main__':
    config = BotConfig.instance()
    uvicorn.run(app, host="localhost", port=8000)

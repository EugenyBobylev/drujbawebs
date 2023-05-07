import urllib
import urllib.parse
from functools import wraps

import uvicorn
from fastapi import FastAPI, Header, HTTPException

from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.templating import Jinja2Templates

from telegram_api import send_answer_web_app_query
from model import WebAppInitData, User
from config import BotConfig
from utils import check_webapp_signature, decode_base64_str


app = FastAPI()

templates = Jinja2Templates(directory="templates")

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


@app.get('/UserRegistration')
async def get_user_registration_html(request: Request,  response: Response):
    headers = {
        'ngrok-skip-browser-warning': '100',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0'
    }
    host = BotConfig.instance().base_url
    return templates.TemplateResponse('userRegistration.html',
                                      context={'request': request, 'host': host}, headers=headers)


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
    r = send_answer_web_app_query(web_init.query_id, user.dict())
    assert 200 == r.status_code
    # return {
    #     'code': 200,
    #     'message': 'User successful created',
    # }


if __name__ == '__main__':
    config = BotConfig.instance()
    uvicorn.run(app, host="localhost", port=8000)

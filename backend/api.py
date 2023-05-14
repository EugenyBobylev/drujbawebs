import urllib
import urllib.parse
from functools import wraps

from fastapi import FastAPI, Header, HTTPException
from fastapi.encoders import jsonable_encoder
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.status import HTTP_204_NO_CONTENT
from starlette.templating import Jinja2Templates

import db
from backend import send_answer_web_app_query
from backend.models import User, Fundraising, WebAppInitData
from config import BotConfig
from db import Account
from utils import check_webapp_signature, decode_base64_str

config = BotConfig.instance()
app = FastAPI()

templates = Jinja2Templates(directory="backend/templates")

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


# ****************************************
# Тестовый мусор
# ****************************************
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


# ****************************************
# Вызов WebApps
# ****************************************
@app.get('/UserRegistration')
async def get_user_registration_html(request: Request,  response: Response):
    headers = {
        'ngrok-skip-browser-warning': '100',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0'
    }
    host = BotConfig.instance().base_url
    return templates.TemplateResponse('userRegistration.html',
                                      context={'request': request, 'host': host}, headers=headers)


# ****************************************
# API for PrivateUser
# ****************************************
@app.post('/user/')
@auth
def create_new_user(user: User, authorization: str | None = Header(convert_underscores=True)):
    """
    Create new user
    :param user:
    :param authorization:
    :return:
    """
    db_user, db_account = db.create_user(user)
    assert db_user is not None
    assert db_account is not None

    web_init = WebAppInitData.form_auth_header(authorization)
    r = send_answer_web_app_query(web_init.query_id, web_init.user.id)
    assert 200 == r.status_code
    return {'account_id': db_account.id }


@app.get('/user/{user_id}')
@auth
def get_user(user_id: int, authorization: str | None = Header(convert_underscores=True)):
    """
    get user info
    :param user_id:
    :param authorization:
    :return:
    """
    user: User = db.get_api_user(user_id)
    if user is not None:
        user_json = jsonable_encoder(user)
        return JSONResponse(content=user_json, status_code=200)
    return Response(status_code=HTTP_204_NO_CONTENT)


@app.get('/user/account/{user_id}/')
@auth
def get_user_account(user_id: int, authorization: str | None = Header(convert_underscores=True)):
    """
    Get user's account
    :param user_id:
    :param authorization:
    :return:
    """
    account: Account = db.get_api_user_account(user_id)
    if account is not None:
        account_json = jsonable_encoder(account)
        return JSONResponse(content=account_json, status_code=200)
    return Response(status_code=HTTP_204_NO_CONTENT)


@app.get('/user/card/{user_id}/')
@auth
def get_user_card_info(user_id: int, authorization: str | None = Header(convert_underscores=True)):
    """
    Get statistic info about all his fundraisings
    :return:
    """


@app.post('/user/fundraising/{user_id}/')
@auth
def create_private_event(user_id: int, fund: Fundraising, authorization: str | None = Header(convert_underscores=True)):
    """
    Create new user's fundraising (event)
    """
    event: Fundraising = db.create_private_fundraising(user_id, fund)
    assert event is not None
    return{'event_id': event.id}

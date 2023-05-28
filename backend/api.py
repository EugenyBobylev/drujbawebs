import json
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
from backend import send_answer_web_app_query, send_message
from backend.models import User, Fundraising, WebAppInitData, PaymentResult
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
@app.get("/test/")
async def get_test(request: Request):
    headers = {
        'ngrok-skip-browser-warning': '100',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0'
    }
    host = BotConfig.instance().base_url
    courses = ['C', 'C++', 'Python', 'Java']
    context = {
        'request': request,
        'courses': courses,
    }
    return templates.TemplateResponse('test.html', context=context, headers=headers)


@app.get("/api/")
async def root():
    return {"message": "Hello World"}


@app.get('/api/query/{query_id}')
async def get_query_id(query_id: str):
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
@app.get('/payment/{account_id}/{cnt}')
async def get_payment_html(request: Request, account_id: int, cnt: int):
    headers = {
        'ngrok-skip-browser-warning': '100',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0'
    }
    host = BotConfig.instance().base_url
    context = {
        'request': request,
        'host': host,
        'account_id': account_id,
        'cnt': cnt,
    }
    return templates.TemplateResponse('payment.html', context=context, headers=headers)


@app.get('/UserRegistration')
async def get_user_registration_html(request: Request):
    headers = {
        'ngrok-skip-browser-warning': '100',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0'
    }
    host = BotConfig.instance().base_url
    return templates.TemplateResponse('userRegistration.html',
                                      context={'request': request, 'host': host}, headers=headers)


@app.get('/FeeCreation')
async def get_private_fundraising_html(request: Request):
    headers = {
        'ngrok-skip-browser-warning': '100',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0'
    }
    host = BotConfig.instance().base_url
    return templates.TemplateResponse('feeCreation.html',
                                      context={'request': request, 'host': host}, headers=headers)


@app.get('/EventSettings/{fund_id}')
async def get_fund_info(fund_id: int, request: Request):
    # Здесь какая-то херня (писал во время обострения отита)
    host = BotConfig.instance().base_url
    fund_info = db.get_fund(fund_id)
    headers = {
        'ngrok-skip-browser-warning': '100',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0'
    }
    context = {
        'request': request,
        'host': host,
        'reason': fund_info.reason,
        'target': fund_info.target,
        'event_date': fund_info.event_date,
        'transfer_info': fund_info.transfer_info,
        'gift_info': fund_info.gift_info,
        'congratulation_date': fund_info.congratulation_date,
        'congratulation_time': fund_info.congratulation_time,
        'event_place': fund_info.event_place,
        'event_dresscode': fund_info.event_dresscode
    }
    return templates.TemplateResponse('editFund.html', context=context, headers=headers)


@app.get('/fundraising/{fund_id}')
async def get_fund(fund_id: int, request: Request):
    host = BotConfig.instance().base_url
    headers = {
        'ngrok-skip-browser-warning': '100',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0'
    }
    fund: Fundraising = db.get_fund(fund_id)
    context = {
        'request': request,
        'host': host,
        'fund_id': fund_id,
        'reason': fund.reason,
        'target': fund.target,
        'event_date': fund.event_date,
        'transfer_info': fund.transfer_info,
        'gift_info': fund.gift_info,
        'congratulation_date': fund.congratulation_date,
        'congratulation_time': fund.congratulation_time,
        'event_place': fund.event_place,
        'event_dresscode': fund.event_dresscode
    }
    return templates.TemplateResponse('editFund.html', context=context, headers=headers)


@app.get('/donors/{fund_id}')
async def get_donors(fund_id: int, request: Request):
    host = BotConfig.instance().base_url
    headers = {
        'ngrok-skip-browser-warning': '100',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0'
    }
    data = db.get_fund_donors(fund_id)
    donors = []
    for d in data:
        item = {
            'user_id': d.user_id,
            'name': d.name,
            'payed': d.payed,
            'payed_date': d.payed_date if d.payed_date is not None else '',
        }
        donors.append(item)

    context = {
        'request': request,
        'host': host,
        'fund_id': fund_id,
        'donors_info': donors
    }
    return templates.TemplateResponse('donors.html', context=context, headers=headers)


@app.get('/donors/edit/{fund_id}')
async def get_donors(fund_id: int, request: Request):
    host = BotConfig.instance().base_url
    headers = {
        'ngrok-skip-browser-warning': '100',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0'
    }
    data = db.get_fund_donors(fund_id)
    donors = []
    for d in data:
        item = {
            'user_id': d.user_id,
            'info': f'{d.name}, {d.payed} руб.',
        }
        donors.append(item)

    context = {
        'request': request,
        'host': host,
        'fund_id': fund_id,
        'donors_info': donors
    }
    return templates.TemplateResponse('participantList.html', context=context, headers=headers)


# ****************************************
# API for PrivateUser
# ****************************************
@app.post('/api/user/')
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
    data = {
        'user_id': db_user.id,
        'account_id': db_account.id
    }
    data_json = json.dumps(data)
    r = send_answer_web_app_query(web_init.query_id, data_json)
    assert 200 == r.status_code
    return {'account_id': db_account.id}


@app.get('/api/user/{user_id}')
@auth
def get_user(user_id: int, authorization: str | None = Header(convert_underscores=True)):
    """
    get user info
    :param user_id:
    :param authorization:
    :return:
    """
    user: User = db.get_user(user_id)
    if user is not None:
        user_json = jsonable_encoder(user)
        return JSONResponse(content=user_json, status_code=200)
    return Response(status_code=HTTP_204_NO_CONTENT)


@app.get('/api/user/account/{user_id}/')
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


@app.get('/api/user/card/{user_id}/')
@auth
def get_user_card_info(user_id: int, authorization: str | None = Header(convert_underscores=True)):
    """
    Get statistic info about all his fundraisings
    :return:
    """
    pass


@app.post('/api/user/fundraising/{user_id}/')
@auth
def create_private_event(user_id: int, fund: Fundraising, authorization: str | None = Header(convert_underscores=True)):
    """
    Create new user's fundraising (event)
    """
    fund: Fundraising = db.create_private_fundraising(user_id, fund)
    assert fund is not None

    web_init = WebAppInitData.form_auth_header(authorization)
    data = {
        'fund_id': fund.id,
        'target': fund.target,  # кому собираем
        'invite_url': fund.invite_url,
    }
    data_json = json.dumps(data)
    r = send_answer_web_app_query(web_init.query_id, data_json)
    assert 200 == r.status_code
    return {
        'event_id': fund.id,
        'invite_url': fund.invite_url
    }


@app.get('/api/fundraising/{fund_id}/')
@auth
def get_api_fund(fund_id):
    """
    Get fundraising (event)
    """
    fund: Fundraising = db.get_fund(fund_id)
    fund_json = jsonable_encoder(fund)
    return JSONResponse(content=fund_json, status_code=200)


@app.put('/api/fundraising/{fund_id}/')
@auth
def edit_api_fund(fund_id: int, fund: Fundraising):
    """
    Edit fundraising (event)
    """
    ok: bool = db.update_fund(fund_id, fund)
    return {
        'operation': 'edit fundraising',
        'fund_id': fund_id,
        'result': ok,
    }


@app.delete('/api/fundraising/{fund_id}/donor/{user_id}/')
@auth
def delete_donor(fund_id: int, user_id: int):
    """
    Delete donor form donors of the fundraising
    :return:
    """
    ok: bool = db.delete_donor(fund_id=fund_id, user_id=user_id)
    return {
        'operation': 'delete donor',
        'fund_id': fund_id,
        'user_id': user_id,
        'result': ok,
    }


@app.get('/api/fundraising/{fund_id}/admin/{user_id}/')
@auth
def set_fund_admin(fund_id: int, user_id: int):
    """
    Change fundraising admin
    :param fund_id:
    :param user_id:
    :return:
    """
    ok: bool = db.set_fund_admin(fund_id=fund_id, user_id=user_id)
    return {
        'operation': 'change admin',
        'fund_id': fund_id,
        'user_id': user_id,
        'result': ok,
    }


@app.post('/api/payment/')
async def get_payment_html(result: PaymentResult):
    user_id = db.get_user_id_by_account(result.account_id)
    if result.success:
        db.add_account_payment(result)
    data_json = jsonable_encoder(result)
    send_message(user_id, data_json)

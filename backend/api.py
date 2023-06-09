import json
import urllib
import urllib.parse
from functools import wraps

from fastapi import FastAPI, Header, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.status import HTTP_204_NO_CONTENT
from starlette.templating import Jinja2Templates

import db
from backend import send_answer_web_app_query
from backend.models import User, Fundraising, WebAppInitData, PaymentResult, CompanyUser
from backend.telegram_api import send_payment_message
from config import Config
from db import Account
from utils import check_webapp_signature, decode_base64_str

config = Config()
app = FastAPI()

templates = Jinja2Templates(directory=config.templates_dir)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
static_dir = config.app_dir + '/backend/static'
app.mount('/static', StaticFiles(directory=static_dir), name='static')

# funds = [
#     {
#         'reason': 'Юбилей Татьяны Осиповой',  # основание для сбора (ДР, юбилей, свадьба, 8-е марта)
#         'target': 'Татьяне Алексеевне',  # кому собираем
#         'event_date': '2023-08-12',  # дата события
#         'transfer_info': 'На карту ее мужа, Михаила (5555-5555-4444-3333)',  # реквизиты перевода
#         'gift_info': 'Что-нибудь из ювелирки'
#     },
#     {
#         'reason': 'Проводы жены (едет к маме не месяц)',  # основание для сбора (ДР, юбилей, свадьба, 8-е марта)
#         'target': 'Кольке',  # кому собираем
#         'event_date': '2023-07-12',  # дата события
#         'transfer_info': 'На карту Палыча (5555-5544-4455-4444)',  # реквизиты перевода
#         'gift_info': ''
#     },
#     {
#         'reason': 'День рождения',  # основание для сбора (ДР, юбилей, свадьба, 8-е марта)
#         'target': 'Семенычу',  # кому собираем
#         'event_date': '2023-07-16',  # дата события
#         'transfer_info': 'На карту Вадима Игоревича (3333-1144-3345-4444)',  # реквизиты перевода
#         'gift_info': 'Какую-нибудь фигню для его авто, потом решим'
#     }
# ]


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
# Вызовы WebApps
# ****************************************
@app.get('/UserRegistration')
async def get_user_registration_html(request: Request):
    headers = {
        'ngrok-skip-browser-warning': '100',
    }
    host = Config().base_url
    return templates.TemplateResponse('userRegistration.html',
                                      context={'request': request, 'host': host}, headers=headers)


@app.get('/CompanyRegistration')
async def get_company_registration_html(request: Request):
    headers = {
        'ngrok-skip-browser-warning': '100',
    }
    host = Config().base_url
    return templates.TemplateResponse('companyRegistration.html',
                                      context={'request': request, 'host': host}, headers=headers)


@app.get('/payment/{account_id}/{cnt}')
async def get_payment_html(request: Request, account_id: int, cnt: int):
    headers = {
        'ngrok-skip-browser-warning': '100',
    }
    host = Config().base_url
    context = {
        'request': request,
        'host': host,
        'account_id': account_id,
        'cnt': cnt,
    }
    return templates.TemplateResponse('payment.html', context=context, headers=headers)


@app.get('/CreateFund/')
async def get_fundraising_html(request: Request, account_id: int, payed_events: int):
    headers = {
        'ngrok-skip-browser-warning': '100',
    }
    host = Config().base_url
    # fund = funds[random.randint(0, 2)]
    context = {
        'request': request,
        'host': host,
        'account_id': account_id,
        'payed_events': payed_events,
        # 'reason': fund['reason'],
        # 'target': fund['target'],  # кому собираем
        # 'event_date': fund['event_date'],  # дата события
        # 'transfer_info': fund['transfer_info'],  # реквизиты перевода
        # 'gift_info': fund['gift_info']
    }
    return templates.TemplateResponse('feeCreation.html', context=context, headers=headers)


@app.get('/fundraising/{fund_id}')
async def get_fund(fund_id: int, request: Request):
    host = Config().base_url
    headers = {
        'ngrok-skip-browser-warning': '100',
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
        'congratulation_date': fund.congratulation_date if fund.congratulation_date is not None else '',
        'congratulation_time': fund.congratulation_time if fund.congratulation_time is not None else '',
        'event_place': fund.event_place if fund.event_place is not None else '',
        'event_dresscode': fund.event_dresscode if fund.event_dresscode is not None else ''
    }
    return templates.TemplateResponse('editFund.html', context=context, headers=headers)


@app.get('/user/{user_id}')
async def get_user(user_id: int, request: Request):
    host = Config().base_url
    headers = {
        'ngrok-skip-browser-warning': '100',
    }
    user: User = db.get_user(user_id)
    context = {
        'request': request,
        'host': host,
        'user_id': user_id,
        'name': user.name,
        'birthdate': user.birthdate,
        'timezone': user.timezone,
    }
    return templates.TemplateResponse('formEdit.html', context=context, headers=headers)


@app.get('/account/{account_id}/funds/')
async def get_user_funds(account_id: int, request: Request):
    host = Config().base_url
    headers = {
        'ngrok-skip-browser-warning': '100',
    }

    data = db.get_account_funds_info(account_id)

    open_funds = len([fi for fi in data if fi.is_open])
    closed_funds = len([fi for fi in data if not fi.is_open])
    successful_funds = len([fi for fi in data if fi.is_success])
    unsuccessful_funds = len([fi for fi in data if not fi.is_success])

    amounts = {
        'open': open_funds,
        'closed': closed_funds,
        'success': successful_funds,
        'unsuccessful': unsuccessful_funds
    }

    context = {
        'request': request,
        'host': host,
        'account_id': account_id,
        'funds_info': data,
        'funds_amounts': amounts
    }
    return templates.TemplateResponse('feeHistory3.html', context=context, headers=headers)


@app.get('/donors/{fund_id}')
async def get_donors(fund_id: int, request: Request):
    """
    Детали сбора
    """
    host = Config().base_url
    headers = {
        'ngrok-skip-browser-warning': '100',
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
    """
    Редактировать список участников
    """
    host = Config().base_url
    headers = {
        'ngrok-skip-browser-warning': '100',
    }
    data = db.get_fund_donors(fund_id)
    donors = []
    for d in data:
        item = {
            'user_id': d.user_id,
            'info': f'{d.name}, {d.payed} руб.',
        }
        donors.append(item)

    fund: Fundraising = db.get_fund(fund_id)
    context = {
        'request': request,
        'host': host,
        'fund_id': fund_id,
        'invite_url': fund.invite_url,
        'donors_info': donors
    }
    return templates.TemplateResponse('participantList.html', context=context, headers=headers)


# ****************************************
# API
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
    db_user, db_accounts = db.create_user(user)
    assert db_user is not None
    assert db_accounts is not None

    web_init = WebAppInitData.form_auth_header(authorization)
    data = {
        'command': 'create_user',
        'user_id': db_user.id,
        'account_id': db_accounts[0].id
    }
    data_json = json.dumps(data)
    r = send_answer_web_app_query(web_init.query_id, data_json)
    assert 200 == r.status_code
    return {'account_id': db_accounts[0].id}


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


@app.post('/api/user/fundraising/{account_id}/')
@auth
def create_fundraising(account_id: int, fund: Fundraising,
                       authorization: str | None = Header(convert_underscores=True)):
    """
    Create new user's fundraising (event)
    """
    fund: Fundraising = db.create_fundraising(account_id, fund)
    assert fund is not None

    web_init = WebAppInitData.form_auth_header(authorization)
    data = {
        'operation': 'create_fund',
        'account_id': account_id,
        'fund_id': fund.id,
        'reason': fund.reason,  # основание для сбора (ДР, юбилей, свадьба, 8-е марта)
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


@app.post('/api/company/')
@auth
def create_company(company_user: CompanyUser, authorization: str | None = Header(convert_underscores=True)):
    ok = db.check_company_exists(company_user.company_name)
    if ok:
        return {'result': 'company exists'}
    company, company_account, user, member_account = db.create_company_user(company_user)
    if not company:
        return {'result': 'company not created'}
    if not company_account:     # не бы создан аккаунт компании
        return {'result': 'company account not created'}
    if not user:  # не бы создан пользователь
        return {'result': 'user not created'}
    if not member_account:  # не бы создан аккаунт участника компании
        return {'result': 'member account not created'}

    # компания/аккаунт/пользователь/участник компании созданы
    web_init = WebAppInitData.form_auth_header(authorization)
    data = {
        'command': 'create_company',
        'company_id': company.id,
        'company_account_id': company_account.id,
        'user_id': user.id,
        'member_account_id': member_account.id
    }
    data_json = json.dumps(data)
    r = send_answer_web_app_query(web_init.query_id, data_json)
    assert 200 == r.status_code

    return {'result': 'ok'}


@app.get('/api/fundraising/{fund_id}/open/')
@auth
def get_api_fund_open(fund_id: int, authorization: str | None = Header(convert_underscores=True)):
    """
    Open fundraising (event)
    """
    web_init = WebAppInitData.form_auth_header(authorization)
    fund: Fundraising = db.get_fund(fund_id)
    data = {
        'operation': 'open_fund',
        'account_id': fund.account_id,
        'fund_id': fund_id,
    }
    data_json = json.dumps(data)
    r = send_answer_web_app_query(web_init.query_id, data_json)
    assert 200 == r.status_code
    return {'ok': True}


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


@app.put('/api/user/{user_id}/')
@auth
def edit_api_user(user_id: int, user: User):
    """
    Edit user
    """
    ok: bool = db.update_user(user_id, user)
    return {
        'operation': 'edit fundraising',
        'fund_id': user_id,
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
def get_payment_html(result: PaymentResult):
    user_id = db.get_user_id_by_account(result.account_id)
    if result.success:
        db.add_account_payment(result)
    # data_json = jsonable_encoder(result)
    send_payment_message(user_id, result)

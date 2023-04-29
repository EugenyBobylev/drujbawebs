from flask import Flask, send_from_directory, jsonify, request, render_template
from dotenv import load_dotenv
from telebot import types, TeleBot
import psycopg

from functools import wraps
import json
import base64
import urllib.parse
import hashlib
import hmac
import os
import datetime

app = Flask(__name__, static_folder='reactapp/build')
app.secret_key = 'P@ssw0rdsecr3t_key'
load_dotenv('../.env')

PG_USERNAME = os.getenv("PG_USERNAME")
PG_PASSWORD = os.getenv("PG_PASSWORD")
PG_HOST = os.getenv("PG_HOST")
PG_DB = os.getenv("PG_DB")
connstr = f'postgresql://{PG_USERNAME}:{PG_PASSWORD}@{PG_HOST}/{PG_DB}'

TG_TOKEN = os.getenv("TG_TOKEN")
BASE_WEBAPP_DOMAIN = os.getenv('BASE_WEBAPP_DOMAIN')

bot = TeleBot(TG_TOKEN)

def getText(textid: str):
    with psycopg.connect(connstr, row_factory=psycopg.rows.dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT text_value FROM public.texts WHERE text_name = %s", (textid, ))
            text = cur.fetchone()['text_value']

    return text

def processAuth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if auth_header is None:
            return '', 400
        
        data_check_string = base64.b64decode(auth_header)
        data_check_string = urllib.parse.unquote(data_check_string)
        dcat = dict(urllib.parse.parse_qsl(data_check_string))
        telegram_hash = dcat['hash']
        del dcat['hash']
        dca = ['='.join([k, v]) for k, v in dcat.items()]
        dca.sort()
        data_check_string = '\n'.join(dca)

        sk = hmac.new(b'WebAppData', os.getenv('TG_TOKEN').encode('utf-8'), hashlib.sha256).digest()
        check_hash = hmac.new(sk, data_check_string.encode('utf-8'), hashlib.sha256).hexdigest()

        if telegram_hash != check_hash:
            return 'something wrong', 401
        
        uid = json.loads(dcat['user'])['id']

        return f(uid=uid, *args, **kwargs)
    return decorated_function

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists("reactapp/build/" + path):
        return send_from_directory('reactapp/build', path)
    else:
        return send_from_directory('reactapp/build', 'index.html')
    
@app.route('/api/userRegister', methods=['POST'])
@processAuth
def webappUserRegistration(uid):
    payload = request.get_json()

    if payload is None:
        return '', 400
    
    name = payload['name']
    dob = payload['dob']
    timezone = payload['timezone']
    personaldata = payload['pdata']

    fdob = datetime.datetime.strptime(dob[:10], '%Y-%m-%d') + datetime.timedelta(days=1)

    if not personaldata:
        return 'Требуется соглашение с обработкой персональных данных', 400
    
    with psycopg.connect(connstr, row_factory=psycopg.rows.dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO users (tgid, name, dob, timezone) VALUES (%s, %s, %s, %s)", (uid, name, fdob, timezone))
            if 'cid' in payload:
                cur.execute("UPDATE users SET companies = %s WHERE tgid = %s", ([payload['cid']], uid))
            # if 'eid' in payload:
            #     cur.execute("SELECT participants FROM events WHERE id = %s", (payload['eid'], ))
            #     participants = cur.fetchone()['participants']
            #     participants.append(uid)
            #     cur.execute("UPDATE events SET participants = %s WHERE id = %s", (participants, payload['eid']))
            conn.commit()


    # await bot.send_message(uid, ) TODO: send main menu
    if 'eid' not in payload:
        markup = types.InlineKeyboardMarkup()
        eventPath = '/webapp/eventCreateForm'
        markup.add(
            types.InlineKeyboardButton("Создать бесплатный сбор", web_app=types.WebAppInfo(url=BASE_WEBAPP_DOMAIN + eventPath)),
        )
        markup.add(types.InlineKeyboardButton("Чаты", callback_data='ch'))
        markup.add(types.InlineKeyboardButton("Оплатить тариф и создать новый сбор", callback_data='qweqwe'))

        bot.send_message(uid, getText('trial_menu').replace('\\n', '\n').format(
            name=name,
        ), reply_markup=markup)
    else:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Принять приглашение", callback_data='event_accept:' + payload['eid']))
        markup.add(types.InlineKeyboardButton("Отклонить приглашение", callback_data='event_decline:' + payload['eid']))

        with psycopg.connect(connstr, row_factory=psycopg.rows.dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT owner, target, campaign_start, type FROM events WHERE id = %s', (payload['eid'], ))
                event = cur.fetchone()

                if event['owner'] > 0:
                    cur.execute('SELECT name FROM users WHERE tgid = %s', (event['owner'], ))
                    owner = cur.fetchone()['name']
                else:
                    cur.execute('SELECT name FROM companies WHERE id = %s', (event['owner'] * -1))
                    owner = cur.fetchone()['name']

        bot.send_message(uid, getText('event_invite_1').replace('\\n', '\n').format(
                event_owner=owner,
                event_target=event['target'],
                campaing_start=event['campaign_start'],
                event_type=event['type']
            ), parse_mode='HTML', reply_markup=markup)

    return '', 200

@app.route('/api/userData', methods=['GET'])
@processAuth
def webappUserData(uid):
    with psycopg.connect(connstr, row_factory=psycopg.rows.dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE tgid = %s", (uid,))
            user = cur.fetchone()
            if user is None:
                return '', 404
            return jsonify(user)
        
@app.route('/api/eventCreation', methods=['POST'])
@processAuth
def webappEventCreation(uid):
    payload = request.get_json()

    if payload is None:
        return '', 400
    
    etype = payload['type']
    target = payload['target']
    date = payload['date']
    reciever = payload['reciever']
    gifts = payload['gifts']

    fdate = datetime.datetime.strptime(date[:10], '%Y-%m-%d') + datetime.timedelta(days=1)
    edate = fdate + datetime.timedelta(days=7)

    with psycopg.connect(connstr, row_factory=psycopg.rows.dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT payed_events, name, role, cid_admin FROM users WHERE tgid = %s', (uid, ))
            data = cur.fetchone()
            if 'eid' not in payload:
                if data['payed_events'] > 0:
                    payed = True
                else:
                    payed = False

                # participants = [uid]

                # participants_info = [{
                #     'id': uid,
                #     'name': data['name'],
                #     'payed': 0
                # }]

                owner = data['cid_admin'] * -1 if data['role'] == 2 else uid

                cur.execute('INSERT INTO events (type, target, owner, campaign_start, campaign_end, recieve_link, gifts_example, payed, closed, participants, participants_info) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id', (etype, target, owner, fdate, edate, reciever, gifts, payed, not payed, [], json.dumps([])))
                eid = cur.fetchone()['id']

                if payed:
                    cur.execute('UPDATE users SET payed_events = payed_events - 1 WHERE tgid = %s', (uid, ))

                if owner > 0:
                    cur.execute('SELECT name, premium FROM users WHERE tgid = %s', (uid, ))
                    user = cur.fetchone()
                    isPrem = user['premium']
                    if not isPrem:
                        markup = types.InlineKeyboardMarkup()
                        markup.add(types.InlineKeyboardButton("Перейти к сбору", web_app=types.WebAppInfo(url=BASE_WEBAPP_DOMAIN + '/webapp/eventAdmin/?eid=' + str(eid))))
                        markup.add(types.InlineKeyboardButton("Чаты", callback_data='ch'))
                        markup.add(types.InlineKeyboardButton("Оплатить тариф и создать новый сбор", callback_data='qweqwe'))

                        bot.send_message(uid, getText('trial_menu').replace('\\n', '\n').format(
                            name=user['name'],
                        ), reply_markup=markup)
            else:
                eid = payload['eid']
                cur.execute('SELECT * FROM events WHERE id = %s', (eid, ))
                event = cur.fetchone()
                if event is None:
                    return '', 404
                if event['owner'] != uid and event['owner'] != data['cid_admin'] * -1:
                    return '', 403
                if event['closed']:
                    return '', 403

                cur.execute('UPDATE events SET type = %s, target = %s, campaign_start = %s, campaign_end = %s, recieve_link = %s, gifts_example = %s WHERE id = %s', (etype, target, fdate, edate, reciever, gifts, eid))

            conn.commit()

    # TODO: if not payed create payment link and redirect
    # TODO: also send message about it in chat, with buttons to remove it or paygit 



    return jsonify({'event_id': eid}), 200

@app.route('/api/getText/<textid>')
# @processAuth
def webappGetText(textid):
    with psycopg.connect(connstr, row_factory=psycopg.rows.dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM texts WHERE text_name = %s", (textid,))
            text = cur.fetchone()
            if text is None:
                return '', 404
            return text['text_value']
        
@app.route('/api/getEvent/<eid>', methods=['GET'])
@processAuth
def webappGetEvent(uid, eid):
    with psycopg.connect(connstr, row_factory=psycopg.rows.dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM events WHERE id = %s", (eid,))
            event = cur.fetchone()
            cur.execute("SELECT * FROM users WHERE tgid = %s", (uid,))
            user = cur.fetchone()

    if event is None:
        return '', 404
    if event['owner'] != uid and event['owner'] != user['cid_admin'] * -1:
        return '', 403
    
    event['campaign_start'] = event['campaign_start'].strftime('%Y-%m-%d')
    event['campaign_end'] = event['campaign_end'].strftime('%Y-%m-%d')

    payed_summ = 0
    avg_price = 0

    if not event['participants']:
        event['participants'] = []

    if not event['participants_info']:
        event['participants_info'] = []

    if event['participants_info']:
        for payment in event['participants_info']:
            payed_summ += payment['payed']
        avg_price = payed_summ // len(event['participants_info'])
    
    event_stats = {'payed_summ': payed_summ, 'avg_price': avg_price}
    event = event | event_stats

    return jsonify(event)

@app.route('/api/getEventParticipants/<eid>', methods=['GET'])
@processAuth
def webappGetEventParticipants(uid, eid):
    with psycopg.connect(connstr, row_factory=psycopg.rows.dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM events WHERE id = %s", (eid,))
            event = cur.fetchone()
            cur.execute("SELECT cid_admin FROM users WHERE tgid = %s", (uid, ))
            user = cur.fetchone()
            if event is None:
                return '', 404
            if event['owner'] != uid and event['owner'] != user['cid_admin'] * -1:
                return '', 403

            return jsonify(event['participants_info'])

@app.route('/api/removeParticipant/<eid>', methods=['POST'])
@processAuth
def webappRemoveParticipant(uid, eid):
    payload = request.get_json()

    if payload is None:
        return '', 400
    
    participant = payload['participant']

    with psycopg.connect(connstr, row_factory=psycopg.rows.dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM events WHERE id = %s", (eid,))
            event = cur.fetchone()
            if event is None:
                return '', 404
            if event['owner'] != uid:
                return '', 403

            event['participants'].remove(participant)
            event['participants_info'] = [x for x in event['participants_info'] if x['id'] != participant]

            cur.execute("UPDATE events SET participants = %s, participants_info = %s WHERE id = %s", (event['participants'], json.dumps(event['participants_info']), eid))
            conn.commit()

    return jsonify(event['participants_info']), 200

@app.route('/api/changeEventOwner/<eid>', methods=['POST'])
@processAuth
def webappChangeEventOwner(uid, eid):
    payload = request.get_json()

    if payload is None:
        return '', 400
    
    newowner = payload['newowner']

    with psycopg.connect(connstr, row_factory=psycopg.rows.dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM events WHERE id = %s", (eid,))
            event = cur.fetchone()
            if event is None:
                return '', 404
            if event['owner'] != uid:
                return '', 403

            cur.execute("UPDATE events SET owner = %s WHERE id = %s", (newowner, eid))
            conn.commit()

    return '', 200

@app.route('/api/company/register', methods=['POST'])
@processAuth
def webappCompanyRegistration(uid):
    payload = request.get_json()

    if payload is None:
        return '', 400
    
    name = payload['name']
    branch = payload['branch']
    personName = payload['personName']
    position = payload['position']
    phone = payload['phone']
    email = payload['email']

    with psycopg.connect(connstr, row_factory=psycopg.rows.dict_row) as conn:
        with conn.cursor() as cur:
            if 'cid' in payload:
                cur.execute("SELECT * FROM companies WHERE id = %s", (payload['cid'],))
                company = cur.fetchone()
                if company is None:
                    return '', 404
                if company['owner'] != uid:
                    return '', 403

                cur.execute("UPDATE companies SET name = %s, branch = %s, owner = %s, owner_position = %s, owner_phone = %s, owner_email = %s WHERE id = %s", (name, branch, uid, position, phone, email, payload['cid']))
                return '', 200

            cur.execute("INSERT INTO companies (name, branch, owner, owner_position, owner_phone, owner_email) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id", (name, branch, uid, position, phone, email))

            cid = cur.fetchone()['id']

            cur.execute("SELECT tgid FROM users WHERE tgid = %s", (uid,))

            if cur.fetchone() is None:
                cur.execute("INSERT INTO users (tgid, name, role, cid_admin, companies) VALUES (%s, %s, 2, %s, %s)", (uid, personName, cid, [cid]))
            else:
                cur.execute("UPDATE users SET cid_admin = %s, companies = companies || %s, role = 2 WHERE tgid = %s", (cid, [cid], uid, ))
            
            cur.execute("SELECT name FROM users WHERE tgid = %s", (uid, ))
            pname = cur.fetchone()['name']

            conn.commit()

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Перейти в личный кабинет компании", web_app=types.WebAppInfo(url=BASE_WEBAPP_DOMAIN + '/webapp/company/admin/?cid=' + str(cid))))
    markup.add(types.InlineKeyboardButton("Проверить ваш тариф или перейти к оплате", callback_data='buy_tariff')) # TODO: tariff magic
    markup.add(types.InlineKeyboardButton("Создать новый сбор", web_app=types.WebAppInfo(url=BASE_WEBAPP_DOMAIN + '/webapp/eventCreateForm')))

    link = f'https://t.me/bot_druzhba_bot?start=c_{str(cid)}'

    bot.send_message(uid, getText('company_menu').replace('\\n', '\n').format(
        name=pname,
        cname=name,
        link=link,
        payed_events=0,
        created_events_len=0,
        employees_len=1,
        participants_len=0,
        events_sum=0,
        open_events=0,
        avg_price=0,
        succeded_events=0,
        event_transfers=0
    ), disable_web_page_preview=True, reply_markup=markup, parse_mode='HTML')

    return '', 200

@app.route('/api/company/get/<cid>', methods=['GET'])
@processAuth
def webappCompanyGet(cid, uid):
    with psycopg.connect(connstr, row_factory=psycopg.rows.dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM companies WHERE id = %s", (cid,))
            company = cur.fetchone()
            if company is None:
                return '', 404
            if company['owner'] != uid:
                return '', 403
            
            cur.execute("SELECT * FROM users WHERE tgid = %s", (uid,))
            user = cur.fetchone()
            company['owner_name'] = user['name']
            
            cur.execute("SELECT COUNT(*) as employees_len FROM users WHERE %s = ANY(companies)", (user['cid_admin'], ))
            employees_len = cur.fetchone()['employees_len']
            cur.execute("SELECT COUNT(*) as created_events FROM events WHERE owner = %s", (user['cid_admin'] * -1, ))
            created_events_len = cur.fetchone()['created_events']
            cur.execute("SELECT COUNT(DISTINCT c) as participants_len FROM (SELECT UNNEST(participants) from events where owner = %s) AS dt(c)", (user['cid_admin'] * -1, ))
            participants_len = cur.fetchone()['participants_len']
            cur.execute("SELECT SUM(event_bank) as events_sum FROM events WHERE owner = %s", (user['cid_admin'] * -1, ))
            events_sum = 0
            t = cur.fetchone()
            if t['events_sum']: events_sum = t['events_sum']
            cur.execute("SELECT COUNT(*) as open_events FROM events WHERE owner = %s AND closed = false AND payed = true", (user['cid_admin'] * -1, ))
            open_events = cur.fetchone()['open_events']
            cur.execute("SELECT participants_info FROM events WHERE owner = %s", (user['cid_admin'] * -1, ))
            succeded_events = 0
            transfers = 0
            for event in cur.fetchall():
                if len(event['participants_info']) > 0:
                    succeded_events += 1
                transfers += len(event['participants_info'])
            avg_price = 0
            if transfers != 0: avg_price = events_sum // transfers

            company_stats = {'employees_len': employees_len, 'created_events_len': created_events_len, 'participants_len': participants_len, 'events_sum': events_sum, 'open_events': open_events, 'succeded_events': succeded_events, 'transfers': transfers, 'avg_price': avg_price}

            company = company | company_stats

            return jsonify(company)
        
@app.route('/api/company/getEvents/<cid>', methods=['GET'])
@processAuth
def webappCompanyGetEvents(cid, uid):
    showOpened = request.args.get('showOpened', 'true') == 'true'
    showClosed = request.args.get('showClosed', 'true') == 'true'
    showSucceded = request.args.get('showSucceded', 'true') == 'true'
    showUnsucceded = request.args.get('showUnsucceded', 'true') == 'true'

    with psycopg.connect(connstr, row_factory=psycopg.rows.dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM companies WHERE id = %s", (cid,))
            company = cur.fetchone()
            if company is None:
                return '', 404
            if company['owner'] != uid:
                return '', 403

            cur.execute("SELECT * FROM events WHERE owner = %s", (int(cid) * -1, ))
            events = cur.fetchall()

            nevents = []
            for event in events:
                if not showOpened and not event['closed']:
                    continue
                if not showClosed and event['closed']:
                    continue
                if not showSucceded and len(event['participants_info']) > 0:
                    continue
                if not showUnsucceded and len(event['participants_info']) == 0:
                    continue
                nevents.append(event)

            print(len(nevents))
            return jsonify(nevents)

@app.route('/api/company/getParticipants/<cid>', methods=['GET'])
@processAuth
def webappCompanyGetParticipants(cid, uid):
    with psycopg.connect(connstr, row_factory=psycopg.rows.dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM companies WHERE id = %s", (cid,))
            company = cur.fetchone()
            if company is None:
                return '', 404
            if company['owner'] != uid:
                return '', 403

            cur.execute("SELECT * FROM users WHERE %s = ANY(companies)", (cid,))
            users = cur.fetchall()

            return jsonify(users)
        
@app.route('/api/company/removeParticipant/<cid>', methods=['POST'])
@processAuth
def webappCompanyRemoveParticipant(cid, uid):
    payload = request.get_json()
    print(payload)
    if 'uid' not in payload:
        return '', 400
    
    with psycopg.connect(connstr, row_factory=psycopg.rows.dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM companies WHERE id = %s", (cid,))
            company = cur.fetchone()
            if company is None:
                return 'no company', 404
            if company['owner'] != uid:
                return '', 403

            cur.execute("SELECT * FROM users WHERE tgid = %s", (payload['uid'],))
            user = cur.fetchone()
            if user is None:
                return 'no user', 404

            if int(cid) not in user['companies']:
                return 'no user in company', 404

            user['companies'].remove(int(cid))

            cur.execute("UPDATE users SET companies = %s WHERE tgid = %s", (user['companies'], payload['uid'], ))

            conn.commit()

            cur.execute("SELECT * FROM users WHERE %s = ANY(companies)", (cid,))
            users = cur.fetchall()

            return jsonify(users)
        
# @app.route('/webapp/userRegisterN', methods=['GET'])
# def userRegisterPage():
#     return render_template('userRegistration.html')

# @app.route('/webapp/shareCompany', methods=['GET'])
# def companySharePage():
#     cid = request.args.get('cid')
#     link = 'https://t.me/bot_druzhba_bot?start=c_' + cid

#     return render_template('company_successfulreg.html', link=link)

# @app.route('/webapp/shareEvent', methods=['GET'])
# def eventSharePage():
#     eid = request.args.get('eid')
#     link = 'https://t.me/bot_druzhba_bot?start=e_' + eid

#     return render_template('event_successfulreg.html', link=link)

# @app.route('/webapp/eventParticipantsList', methods=['GET'])
# def eventParticipantList():
#     eid = request.args.get('eid')
#     link = 'https://t.me/bot_druzhba_bot?start=e_' + eid

#     return render_template('event_participantsList.html', link=link)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000, debug=True)
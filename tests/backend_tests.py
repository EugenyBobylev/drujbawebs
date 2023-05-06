

# *************************************
# Required working backend
# *************************************
def test_create_user_without_auth():
    url = 'http://127.0.0.1:8000/user/'
    user = User(name='test_user', timezone=1)
    r = requests.post(url, json=user.__dict__)
    assert r.status_code == 422


def test_create_user_with_auth():
    url = 'http://127.0.0.1:8000/user/'
    headers = {
        'Authorization': auth
    }
    user = User(name='test_user', timezone=1)
    r = requests.post(url, headers=headers, json=user.__dict__)
    assert r.status_code == 200


def test_create_user_with_wrong_auth():
    url = 'http://127.0.0.1:8000/user/'
    headers = {
        'Authorization': 'all nonsense'
    }
    user = User(name='test_user', timezone=1)
    r = requests.post(url, headers=headers, json=user.__dict__)
    assert r.status_code == 401


def test_api_bot_send_me():
    headers = {
        'Content-Type: application/json'
    }
    token = BotConfig.instance().token
    url = f'https://api.telegram.org/bot{token}/getMe'
    r = requests.get(url)
    assert 200 == r.status_code
    answer = r.json()
    assert answer['ok']
    assert 'conceptui' == answer['result']['first_name']
    assert 'conceptuibot' == answer['result']['username']


def test_answer_web_app_query():
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        'web_app_query_id': 'AAHHSWsHAAAAAMdJawcBvcwJ',
        'result': {
            'type': 'article',
            'id': '123',
            'title': 'test article',
            'message_text': 'Я пришел к тебе с приветом',
            'obj': {
                'name': 'Пушкин',
                'timezone': 1,
            }
        }
    }
    body = json.dumps(data)
    token = BotConfig.instance().token
    url = f'https://api.telegram.org/bot{token}/answerWebAppQuery'

    r = requests.post(url, headers=headers, data=body)
    assert 200 == r.status_code

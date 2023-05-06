import base64
import hashlib
import hmac
import re
from operator import itemgetter
from urllib.parse import parse_qsl


def check_webapp_signature(token: str, init_data: str) -> bool:
    """
    Check incoming WebApp init data signature
    Source: https://core.telegram.org/bots/webapps#validating-data-received-via-the-web-app
    :param token:
    :param init_data:
    :return:
    """
    try:
        parsed_data = dict(parse_qsl(init_data))
    except ValueError:
        # Init data is not a valid query string
        return False
    if "hash" not in parsed_data:
        # Hash is not present in init data
        return False

    hash_ = parsed_data.pop('hash')
    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(parsed_data.items(), key=itemgetter(0))
    )
    secret_key = hmac.new(
        key=b"WebAppData", msg=token.encode(), digestmod=hashlib.sha256
    )
    calculated_hash = hmac.new(
        key=secret_key.digest(), msg=data_check_string.encode(), digestmod=hashlib.sha256
    ).hexdigest()
    return calculated_hash == hash_


def decode_base64_str(base64_encoded: str):
    try:
        base64_bytes = base64_encoded.encode('ascii')
        message_bytes = base64.b64decode(base64_bytes)
        decoded = message_bytes.decode('ascii')
    except Exception:
        decoded = ''
    return decoded


def re_search(pattern: str, txt: str) -> str | None:
    _match = re.search(pattern, txt)
    if _match:
        return _match[1]
    return None

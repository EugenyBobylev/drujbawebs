import asyncio
import json
import os
from dataclasses import dataclass
from pathlib import Path

from telethon import TelegramClient, password
from telethon.errors import UserRestrictedError, UserDeactivatedBanError, ChannelPrivateError, SrpIdInvalidError
from telethon.tl.functions.account import GetPasswordRequest
from telethon.tl.functions.channels import CreateChannelRequest, GetParticipantsRequest, EditCreatorRequest
from telethon.tl.functions.messages import ExportChatInviteRequest
from telethon.tl.types import ChannelParticipantsSearch

script_path = os.path.abspath(__file__)
work_dir = str(Path(script_path).parent)
files = os.listdir(work_dir)
json_files = [work_dir + '/' + f for f in files if os.path.isfile(work_dir + '/' + f) if f.endswith('.json')]


@dataclass
class ChatConfig:
    app_id: int
    app_hash: str
    pwd: str
    session_path: str
    proxy_host: str
    proxy_port: int
    proxy_login: str
    proxy_pwd: str

    def __repr__(self):
        return f'app_id={self.app_id}; app_hash="{self.app_hash}"; pwd="{self.pwd}"; session_path="{self.session_path}"'

    def get_telegram_client(self) -> TelegramClient:
        proxy = None
        if self.proxy_host and self.proxy_port:
            proxy = {
                'proxy_type': 'socks5',
                'addr': self.proxy_host,
                'port': self.proxy_port,
                'rdns': True
            }
            if self.proxy_login and self.proxy_pwd:
                proxy['login'] = self.proxy_login
                proxy['password'] = self.proxy_pwd
        client = TelegramClient(self.session_path, self.app_id, self.app_hash, proxy=proxy)
        return client

    @classmethod
    def from_json(cls, path) -> 'ChatConfig':
        with open(path, mode='r', encoding='utf-8') as f:
            json_str = f.read()
            data = json.loads(json_str)
            instance = cls(app_id=data.get('app_id', None),
                           app_hash=data.get('app_hash', None),
                           pwd=data.get('twoFA', None),
                           session_path=path[0:-4]+'session',
                           proxy_port=data.get('proxy_port', None),
                           proxy_host=data.get('proxy_host', None),
                           proxy_login=data.get('proxy_login', None),
                           proxy_pwd=data.get('proxy_pwd', None),)
            return instance


async def _send_message(client: TelegramClient):
    await client.send_message("@BobylevEA", 'Privet')


async def get_channel_link(channel_id: int, client: TelegramClient) -> str:
    invite = await client(ExportChatInviteRequest(peer=channel_id))
    channel_link = invite.link
    return channel_link


async def _create_channel(chat_name, chat_about, client: TelegramClient) -> str:
    await client.connect()
    try:
        channel = await client(CreateChannelRequest(title=chat_name, about=chat_about, megagroup=True,))
        channel_id = channel.updates[1].channel_id
        channel_link = await get_channel_link(channel_id, client)
    except (UserRestrictedError, UserDeactivatedBanError):
        channel_link = 'user account is blocked'
    finally:
        await client.disconnect()
    return channel_link


async def _get_all_channels(client: TelegramClient) -> list:
    channels = []
    try:
        await client.connect()
        async for dialog in client.iter_dialogs():
            if dialog.is_channel:
                link = await get_channel_link(dialog.id, client)
                data = (dialog.id, dialog.title, link)
                channels.append(data)
    finally:
        await client.disconnect()
    return channels


async def _change_channel_owner(channel_id: int, owner_password: str, client: TelegramClient) -> bool:
    try:
        users = await client(GetParticipantsRequest(channel_id,
                                                    ChannelParticipantsSearch(''), limit=2, offset=0, hash=0))
        users = users.participants
        if len(users) > 1:
            user_id = users[0].user_id
            pwd = await client(GetPasswordRequest())
            pwd_2 = password.compute_check(pwd, owner_password)

            await client(EditCreatorRequest(channel_id, user_id, pwd_2))
            await client.delete_dialog(channel_id)
            return True
        else:
            return False
    except(UserRestrictedError, UserDeactivatedBanError, ChannelPrivateError, SrpIdInvalidError):
        return False


# ******************************************************
# Logic for works with user chats
# ******************************************************
def get_json_file() -> str:
    json_file = json_files.pop(0)
    json_files.append(json_file)
    return json_file


def get_chat_config(json_file: str) -> ChatConfig:
    """
    Вернуть данные пользователя телеграмм, от имени которого будем производить действия в дальнейшем
    :return:
    """
    chat_config = ChatConfig.from_json(json_file)
    return chat_config


async def async_create_chat2(chat_name: str, about: str = '') -> str:
    """
    Создать чат и удалить из чата создателя, передав права владельца первому пользователю чата
    """
    json_file = get_json_file()
    _config: ChatConfig = get_chat_config(json_file)

    chat_url = await async_create_chat(chat_name, about, _config)
    cnt = await async_change_chats_owners(_config)
    return chat_url


async def async_create_chat(chat_name: str, about: str = '', config: ChatConfig = None) -> str:
    """
    Создать чат
    """
    if about == '':
        about = chat_name

    if config is None:
        json_file = get_json_file()
        config = get_chat_config(json_file)
    _client = config.get_telegram_client()
    # with _client:
    _chat_url = await _create_channel(chat_name, about, _client)
    return _chat_url


async def async_change_channel_owner(channel_id: int, chat_config: ChatConfig) -> bool:
    owner_password = chat_config.pwd
    client = chat_config.get_telegram_client()
    await client.connect()

    try:
        users = await client(GetParticipantsRequest(channel_id,
                                                    ChannelParticipantsSearch(''), limit=2, offset=0, hash=0))
        users = users.participants
        if len(users) > 1:
            user_id = users[0].user_id
            pwd = await client(GetPasswordRequest())
            pwd_2 = password.compute_check(pwd, owner_password)

            await client(EditCreatorRequest(channel_id, user_id, pwd_2))
            await client.delete_dialog(channel_id)
            return True
        else:
            return False
    except(UserRestrictedError, UserDeactivatedBanError, ChannelPrivateError, SrpIdInvalidError):
        return False
    finally:
        await client.disconnect()


async def async_change_chats_owners(chat_config: ChatConfig) -> int:
    """
    Выполнить передачу прав на чат пользователям чата
    :return: кол. чатов, права на которые были переданы пользователям этих чатов
    """
    _cnt = 0
    all_chats = await async_get_chats(chat_config)
    pwd = chat_config.pwd

    _client = chat_config.get_telegram_client()
    all_tasks = []
    await _client.connect()
    try:
        for chat_id, _, _ in all_chats:
            t = asyncio.create_task(_change_channel_owner(chat_id, pwd, _client))
            all_tasks.append(t)
        await asyncio.sleep(0.2)
        done, pending = await asyncio.wait(all_tasks, timeout=5, return_when=asyncio.ALL_COMPLETED)
        for t in done:
            ok = await t
            if ok:
                _cnt += 1
        for t in pending:
            t.cancel()
    finally:
        await _client.disconnect()
    return _cnt


async def async_get_chats(chat_config: ChatConfig) -> list[str]:
    """
    Вернуть список всех чатов созданных пользователем из chat_config
    :return: (chat_id, chat_name, chat_url)
    """
    _client = chat_config.get_telegram_client()
    all_chats = await _get_all_channels(_client)
    return all_chats

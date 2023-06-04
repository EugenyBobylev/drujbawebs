import json
from dataclasses import dataclass

from telethon import TelegramClient, password
from telethon.errors import UserRestrictedError, UserDeactivatedBanError, ChannelPrivateError
from telethon.tl.functions.account import GetPasswordRequest
from telethon.tl.functions.channels import CreateChannelRequest, GetParticipantsRequest, EditCreatorRequest
from telethon.tl.functions.messages import ExportChatInviteRequest
from telethon.tl.types import ChannelParticipantsSearch


@dataclass
class ChatConfig:
    app_id: int
    app_hash: str
    pwd: str
    session_path: str

    def __repr__(self):
        return f'app_id={self.app_id}; app_hash="{self.app_hash}"; pwd="{self.pwd}"; session_path="{self.session_path}"'

    def get_telegram_client(self) -> TelegramClient:
        client = TelegramClient(self.session_path, self.app_id, self.app_hash,)
        return client

    @classmethod
    def from_json(cls, path) -> 'ChatConfig':
        with open(path, mode='r', encoding='utf-8') as f:
            json_str = f.read()
            data = json.loads(json_str)
            instance = cls(app_id=data.get('app_id', None),
                           app_hash=data.get('app_hash', None),
                           pwd=data.get('twoFA', None),
                           session_path=path[0:-4]+'session')
            return instance


async def _send_message(client: TelegramClient):
    await client.send_message("@BobylevEA", 'Privet')


async def get_channel_link(channel_id: int, client: TelegramClient)-> str:
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
    await client.connect()
    try:
        users = await client(GetParticipantsRequest(channel_id, ChannelParticipantsSearch(''), limit=2, offset=0, hash=0))
        users = users.participants
        if len(users) > 1:
            user_id = users[0].user_id
            pwd = await client(GetPasswordRequest())
            pwd_2 = password.compute_check(pwd, owner_password)

            update = await client(EditCreatorRequest(channel_id, user_id, pwd_2))
            await client.delete_dialog(channel_id)
            return True
    except(UserRestrictedError, UserDeactivatedBanError, ChannelPrivateError):
        return False
    finally:
        await client.disconnect()


# ******************************************************
# Logic for works with user chats
# ******************************************************
def create_chat(chat_name: str, about: str = '') -> str:
    """
    Создать чат
    :param chat_name: наименование чата
    :param about: описани чата
    :return:
    """
    if about == '':
        about = chat_name
    _config = ChatConfig.from_json('12016637512.json')
    _client = _config.get_telegram_client()
    with _client:
        _chat_url = _client.loop.run_until_complete(
            _create_channel(chat_name, about, _client)
        )
    return _chat_url


def get_all_chats() -> list[str]:
    """
    Вернуть список всех чатов пользователя
    :return: (chat_id, chat_name, chat_url)
    """
    _config = ChatConfig.from_json('12016637512.json')
    _client = _config.get_telegram_client()
    with _client:
        all_chats = _client.loop.run_until_complete(_get_all_channels(_client))
    return all_chats


def change_chat_owner(chat_id: int) -> bool:
    """
    Удалить себя из чата, пеередав права на чат другому пользователю (тому кто первый вошел в чат)
    :param chat_id:
    :return: True or False
    """
    _config = ChatConfig.from_json('12016637512.json')
    _client = _config.get_telegram_client()
    with _client:
        ok = _client.loop.run_until_complete(_change_channel_owner(chat_id, _config.pwd, _client))
    return ok


if __name__ == '__main__':
    # chat_url = create_chat('8 Друзей Оушена', 'Обсуждаем друзей Оушена')
    # print(chat_url)

    all_channels = get_all_chats()
    print(all_channels)

    # ok = change_chat_owner(-1001861785717)
    # print(ok)

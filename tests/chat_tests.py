import asyncio
import random
from asyncio import Task

import pytest

from chat.user_chat import ChatConfig, json_files, get_json_file, async_get_chats, async_change_chats_owners, \
    async_change_channel_owner


def test_json_files():
    assert len(json_files) == 2


def test_get_json_file():
    json_file = get_json_file()
    assert json_file == '/home/bobylev/PycharmProjects/drujbawebs/chat/12016637512.json'


def test_get_chat_config():
    json_file = get_json_file()
    chat_config = ChatConfig.from_json(json_file)
    assert chat_config is not None


def test_get_chats():
    json_file = get_json_file()
    chat_config = ChatConfig.from_json(json_file)
    chats = asyncio.run(async_get_chats(chat_config))

    for chat_id, name, url in chats:
        print(chat_id, url)
    assert len(chats) == 4


@pytest.mark.asyncio
async def test_async_changes_chat_owner():
    chat_ids = [-1001320996404, -1001735138619, -1001941148261, -1001919363789, ]
    json_file = '/home/bobylev/PycharmProjects/drujbawebs/chat/12016637512.json'
    chat_config = ChatConfig.from_json(json_file)
    pwd = chat_config.pwd
    client = chat_config.get_telegram_client()
    ok = await async_change_channel_owner(chat_ids[0], pwd, client)
    assert ok


@pytest.mark.asyncio
async def test_async_changes_chats_owner():
    json_file = '/home/bobylev/PycharmProjects/drujbawebs/chat/12016637512.json'
    chat_config = ChatConfig.from_json(json_file)
    cnt = await async_change_chats_owners(chat_config)
    assert cnt == 0


async def long_time_function(name: str) -> str:
    seconds = random.random() * 8
    await asyncio.sleep(seconds)
    return f'{name} finished in {round(seconds, 3)} seconds'


@pytest.mark.asyncio
async def test_long_time():
    all_tasks = []
    for i in range(1, 11):
        t = asyncio.create_task(long_time_function(f'task_{i}'))
        all_tasks.append(t)
    await asyncio.sleep(0.2)
    done, pending = await asyncio.wait(all_tasks, timeout=5, return_when=asyncio.ALL_COMPLETED)
    print('\n')
    for t in done:
        res = await t
        print(res)
    for t in pending:
        res = t.cancel()
        print(res)
    print(f'len_pending={len(pending)}')
    print('all done')

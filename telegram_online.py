import os
import pickle
import time
import asyncio
import logging
from telethon import TelegramClient, sync, events
from telethon.sessions import StringSession

# Введите свои данные приложения из https://my.telegram.org/apps
api_id = 26741039
api_hash = 'fe897b39141cb85d129800ce709bf9f1'
session_file = 'session.pickle'
contacts_file = 'tp1/account.txt'
phone_number = '+380664167171'
import json

# Создаем логгер и устанавливаем уровень логирования (может быть logging.DEBUG, logging.INFO, logging.WARNING и т. д.)
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def get_telegram_client():
    if os.path.exists(session_file):
        with open(session_file, 'r') as f:
            session_data = json.load(f)
            client = TelegramClient(StringSession(session_data['session_string']), api_id, api_hash)
    else:
        client = TelegramClient(phone_number, api_id, api_hash)
        client.connect()
        if not client.is_user_authorized():
            client.send_code_request(phone_number)
            code = input("Введите код, который пришел вам в Telegram: ")
            client.sign_in(phone_number, code)

        session_data = {
            'session_string': client.session.save(),
        }
        with open(session_file, 'w') as f:
            json.dump(session_data, f)

    return client

async def get_online_status_async(client, username):
    try:
        user_entity = await client.get_entity(username)
        if user_entity.status:
            if hasattr(user_entity.status, 'was_online'):
                return user_entity.status.was_online
            else:
                print(f"Пользователь {username} онлайн")
                # Получаем текущее время в секундах с начала эпохи (01.01.1970, 00:00:00 UTC)
                current_timestamp = time.time()

                # Преобразуем текущее время в структуру времени
                current_time_struct = time.localtime(current_timestamp)

                # Форматируем структуру времени и получаем текущую дату и время в строковом виде
                current_date_time = time.strftime("%Y-%m-%d %H:%M:%S", current_time_struct)
                return current_date_time
    except Exception as e:
        logger.error(f"Ошибка при получении статуса пользователя {username}: {e}")
    return None

def save_last_online(username, last_online):
    filename = f"{username}.txt"
    with open(filename, 'a') as f:
        f.write(str(last_online) + '\n')

def main():
    # Удаление старого файла session.pickle, если он существует
    if os.path.exists(session_file):
        os.remove(session_file)

    client = get_telegram_client()

    with open(contacts_file, 'r') as f:
        contacts = f.read().splitlines()

    online_status_list = []

    while True:
        for username in contacts:
            try:
                last_online = client.loop.run_until_complete(get_online_status_async(client, username))
                if last_online:
                    save_last_online(username, last_online)
                    print(f"Пользователь {username} был онлайн в {last_online}")
                if last_online == 'UserStatusOnline':
                    print('Пользователь онлайн')
                else:
                    print(f"Пользователь {username} оффлайн")

                # Добавляем информацию в список
                online_status_list.append({"username": username, "status": last_online})
            except KeyboardInterrupt:
                # Остановка цикла, если пользователь прерывает скрипт
                break
            except Exception as e:
                print(f"Ошибка при получении статуса пользователя {username}: {e}")

        # Проверяем каждую минуту
        time.sleep(60)

    # Дополнительный код, который может использовать список online_status_list
    # для последующей работы с данными, сохраненными в процессе мониторинга.

if __name__ == "__main__":
    main()

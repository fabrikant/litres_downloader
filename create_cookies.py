import requests
import logging
import argparse
from pathlib import Path
import json

from tg_sender import send_to_telegram

LITRES_DOMAIN_NAME = "litres.ru"
logger = logging.getLogger(__name__)


def create_cookies(user, password, cookies_file, tg_api_key, tg_chat_id):
    url = f"https://api.{LITRES_DOMAIN_NAME}/foundation/api/auth/countries/allowed"
    res = requests.get(url)
    if not res.ok:
        msg = f"Oшибка {res.status_code} при обращении к URL: {url}"
        logger.error(msg)
        send_to_telegram(msg, tg_api_key, tg_chat_id)
        exit(0)

    SID = res.headers["request-session-id"]

    url = f"https://api.{LITRES_DOMAIN_NAME}/foundation/api/auth/login"
    headers = {"Session-Id": SID, "app-id": "115"}
    json_data = {"login": user, "password": password}
    res = requests.post(url, headers=headers, json=json_data)
    if not res.ok:
        msg = (
            f"Ошибка {res.status_code} при попытке авторизации {res.content.decode()} "
            f"url {url}"
        )
        logger.error(msg)
        send_to_telegram(msg, tg_api_key, tg_chat_id)
        exit(0)
        pass

    Path(args.cookies_file).write_text(json.dumps({"SID": SID}))
    msg = f"Записан файл {args.cookies_file}"
    logger.info(msg)
    send_to_telegram(msg, tg_api_key, tg_chat_id)


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    parser = argparse.ArgumentParser(
        description=f"Создает файл cookies по имени пользователя и паролю от сайта {LITRES_DOMAIN_NAME} для \
            дальнейшего использования со скриптом закачки книг"
    )
    parser.add_argument(
        "--telegram-api",
        help="Необязательный ключ API телеграм бота, который будет сообщать о процессе загрузки",
        default="",
    )
    parser.add_argument(
        "--telegram-chatid",
        help="Необязательный ключ идентификатор чата в который будет писать телеграм бот",
        default="",
    )
    parser.add_argument("-u", "--user", help="Имя пользователя", default="")
    parser.add_argument("-p", "--password", help="Пароль", default="")
    parser.add_argument(
        "--cookies-file",
        help="Cookies сохранятся в этот файл. По умолчанию: cookies.json",
        default="cookies.json",
    )
    args = parser.parse_args()

    logger.info(args)
    create_cookies(
        args.user,
        args.password,
        args.cookies_file,
        args.telegram_api,
        args.telegram_chatid,
    )

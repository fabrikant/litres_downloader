import requests
import logging
import argparse
from pathlib import Path
import json
from tg_sender import send_to_telegram
from common import LITRES_DOMAIN_NAME, cookies_is_valid

try:
    import cookielib
except ImportError:
    import http.cookiejar as cookielib

logger = logging.getLogger(__name__)


def to_cookielib_cookie(name, value, domain):
    return cookielib.Cookie(
        version=0,
        name=name,
        value=value,
        port="80",
        port_specified=False,
        domain=domain,
        domain_specified=True,
        domain_initial_dot=False,
        path="/",
        path_specified=True,
        secure=True,
        expires=None,
        discard=False,
        comment=None,
        comment_url=None,
        rest=None,
    )


def create_cookies(user, password, cookies_file, tg_api_key, tg_chat_id):
    url = f"https://api.{LITRES_DOMAIN_NAME}/foundation/api/auth/login-available"
    json_data = {"login": user}
    res = requests.post(url, json=json_data)
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

    cookie_jar = cookielib.CookieJar()
    cookie_jar.set_cookie(to_cookielib_cookie("SID", SID, f"www.{LITRES_DOMAIN_NAME}"))
    err_msg = cookies_is_valid(cookie_jar, tg_api_key, tg_chat_id)
    if err_msg == "":
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
    parser.add_argument(
        "-b",
        "--browser",
        help=f"Не используется оставлен для совместимости",
        default="firefox",
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

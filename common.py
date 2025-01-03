import requests
import logging
from requests.utils import cookiejar_from_dict
from pathlib import Path

try:
    import cookielib
except ImportError:
    import http.cookiejar as cookielib
import json

LITRES_DOMAIN_NAME = "litres.ru"
logger = logging.getLogger(__name__)


def send_to_telegram(msg, tg_api_key, tg_chat_id):
    if len(tg_api_key) > 0 and len(tg_chat_id) > 0:
        url = f"https://api.telegram.org/bot{tg_api_key}/sendMessage"
        data = {"chat_id": tg_chat_id, "text": msg}
        res = requests.post(url, data=data)
        if res.ok:
            logger.info("Отправлено сообщение в телеграм")
        else:
            err_msg = (
                f"Ошибка: {res.status_code} ({res.json()['description']}) POST: {url}"
            )
            logger.warning(err_msg)


def cookies_is_valid(cookies, tg_api_key, tg_chat_id):

    err_msg = ""
    url_string = f"https://{LITRES_DOMAIN_NAME}"
    res = requests.get(url_string, cookies=cookies)
    if res.ok:
        ref_string = "/me/profile/"
        content_list = res.text.split(ref_string)
        if len(content_list) == 1:
            err_msg = f"Ошибка: {res.status_code} GET {url_string} \
                В полученных данных не удалось найти ссылку {ref_string}, \
                что означает ошибку авторизации по файлу cookies"
            logger.error(err_msg)
            send_to_telegram(err_msg, tg_api_key, tg_chat_id)
    else:
        err_msg = f"Ошибка: {res.status_code} ({str(res.json())}) GET {url_string} \
                Ошибка авторизации по файлу cookies"
        logger.error(err_msg)
        send_to_telegram(err_msg, tg_api_key, tg_chat_id)
    return err_msg

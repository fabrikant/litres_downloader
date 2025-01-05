import requests
import logging
from requests.utils import cookiejar_from_dict
from pathlib import Path

try:
    import cookielib
except ImportError:
    import http.cookiejar as cookielib
import json
from tg_sender import send_to_telegram

LITRES_DOMAIN_NAME = "litres.ru"
logger = logging.getLogger(__name__)


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

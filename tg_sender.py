import requests
import logging
logger = logging.getLogger(__name__)

def send_to_telegram(msg, tg_api_key, tg_chat_id):
    logger.debug(f"Вызвана процедура: send_to_telegram(msg={msg}, tg_api_key={tg_api_key}, tg_chat_id={tg_chat_id})")
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
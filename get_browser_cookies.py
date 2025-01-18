import requests
import browsercookie
import argparse
import logging
from pathlib import Path
import json
from requests.utils import dict_from_cookiejar

logger = logging.getLogger(__name__)


def get_cookies(browser):
    cookies = ""
    if browser == "chrome":
        cookies = browsercookie.chrome()
    elif browser == "chromium":
        cookies = browsercookie.chromium()
    elif browser == "vivaldi":
        cookies = browsercookie.vivaldi()
    elif browser == "edge":
        cookies = browsercookie.edge()
    elif browser == "firefox":
        cookies = browsercookie.firefox()
    elif browser == "safari":
        cookies = browsercookie.safari()
    return cookies


def cookies_is_valid(cookies):
    result = False
    res = requests.get(f"https://{LITRES_DOMAIN_NAME}", cookies=cookies)
    if res.ok:
        content_list = res.text.split("/me/profile/")
        if len(content_list) > 1:
            result = True

    return result


def convert_etc_to_requests(cookie_list):
    """Конвертирует формат EditThisCookie в формат, совместимый с requests"""
    cookies_dict = {}
    for cookie in cookie_list:
        # Включаем только необходимые поля, которые нужны для requests
        cookies_dict[cookie["name"]] = cookie["value"]
    return cookies_dict


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    parser = argparse.ArgumentParser(description=f"Извлечение cookies из браузера")
    parser.add_argument(
        "-b",
        "--browser",
        help=f"Браузер в котором вы авторизованы на сайте litres.ru. По умолчанию: chrome",
        default="chrome",
        choices=["chrome", "edge", "firefox", "safari"],
    )
    parser.add_argument(
        "--cookies-file",
        help="Имя файла в которой будут сохранены cookies из браузера",
        default="cookies.json",
    )

    args = parser.parse_args()
    logger.info(args)

    cookies = get_cookies(args.browser)
    if len(args.cookies_file) > 0:
        Path(args.cookies_file).write_text(json.dumps(dict_from_cookiejar(cookies)))

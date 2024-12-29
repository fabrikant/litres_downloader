import requests
from pathvalidate import sanitize_filename
import argparse
import logging
from pathlib import Path
from fake_useragent import UserAgent
from tqdm import tqdm

try:
    import cookielib
except ImportError:
    import http.cookiejar as cookielib
import json
from requests.utils import cookiejar_from_dict

logger = logging.getLogger(__name__)
LITRES_DOMAIN_NAME = "litres.ru"
api_url = f"https://api.{LITRES_DOMAIN_NAME}/foundation/api/arts/"


def get_headers(browser):
    ua = UserAgent()
    agent = ua.chrome
    if browser == "firefox":
        agent = ua.firefox
    elif browser == "edge":
        agent = ua.edge
    elif browser == "safari":
        agent = ua.safari
    return {
        "User-Agent": agent,
    }


def download_mp3(url, path, filename, cookies, headers):
    logger.info(f"Загрузка файла: {url}")
    full_filename = Path(path) / sanitize_filename(filename)

    res = requests.get(url, stream=True, cookies=cookies, headers=headers)
    if res.status_code == 200:
        total_size = int(res.headers.get("content-length", 0))
        block_size = 1024
        with tqdm(
            total=total_size, unit="B", unit_scale=True, desc=filename
        ) as progress_bar:
            with open(full_filename, "wb") as file:
                for data in res.iter_content(block_size):
                    progress_bar.update(len(data))
                    file.write(data)

            if total_size != 0 and progress_bar.n != total_size:
                logger.error(f"Не удалось загрузить файл: {url}")
    else:
        logger.error(f"code: {res.status_code} При загрузке с адреса: {url}")


def get_book_info(json_data):
    book_info = {
        "title": "",
        "author": "",
        "reader": "",
        "series": "",
        "series_count": 0,
        "series_num": 0,
    }
    book_info["title"] = json_data["title"]

    for person_info in json_data["persons"]:
        if person_info["role"] == "author" and book_info["author"] == "":
            book_info["author"] = person_info["full_name"]
            author_split = book_info["author"].split()
            # Переворачиваем фамилию имя
            if len(author_split) == 2:
                book_info["author"] = f"{author_split[1]} {author_split[0]}"

        if person_info["role"] == "reader" and book_info["reader"] == "":
            book_info["reader"] = person_info["full_name"]

    for series_info in json_data["series"]:
        if "name" in series_info and series_info["name"] != None:
            book_info["series"] = series_info["name"]
        if "arts_count" in series_info and series_info["arts_count"] != None:
            book_info["series_count"] = series_info["arts_count"]
        if "art_order" in series_info and series_info["art_order"] != None:
            book_info["series_num"] = series_info["art_order"]
        break

    return book_info


def get_book_folder(output, book_info):
    book_folder = Path(output)
    if book_info["author"] != "":
        book_folder = Path(book_folder) / sanitize_filename(book_info["author"])

    if book_info["series"] != "":
        book_folder = Path(book_folder) / sanitize_filename(book_info["series"])

    if book_info["series_num"] > 0:
        book_folder = Path(book_folder) / sanitize_filename(
            f'{book_info["series_num"]:02d} {book_info["title"]}'
        )
    else:
        book_folder = Path(book_folder) / sanitize_filename(book_info["title"])
    Path(book_folder).mkdir(exist_ok=True, parents=True)
    return book_folder


def download_book(url, output, browser, cookies):
    headers = get_headers(browser)
    book_id = url.split("-")[-1].split("/")[0]

    url_string = api_url + book_id
    res = requests.get(url_string, cookies=cookies, headers=headers)
    if res.status_code != 200:
        logger.error(f"Ошибка запроса GET: {url_string}. Статус: {res.status_code}")
        exit(1)

    book_info = get_book_info(res.json()["payload"]["data"])
    logger.debug(f"Получена информация о книге: {book_info['title']}")
    book_folder = get_book_folder(output, book_info)
    logger.info(f"Загрузка файлов в каталог: {book_folder}")

    # Список файлов для загрузки
    url_string = url_string + "/files/grouped"
    res = requests.get(url_string, cookies=cookies, headers=headers)
    if res.status_code != 200:
        logger.error(f"Ошибка запроса GET: {url_string}. Статус: {res.status_code}")
        exit(1)

    groups_info = res.json()["payload"]["data"]
    for group_info in groups_info:
        if "standard_quality_mp3" in group_info["file_type"]:
            files_info = group_info["files"]
            for file_info in files_info:
                file_id = file_info["id"]
                filename = file_info["filename"]
                file_url = f"https://www.{LITRES_DOMAIN_NAME}/download_book_subscr/{book_id}/{file_id}/{filename}"
                download_mp3(file_url, book_folder, filename, cookies, headers)
            break


def cookies_is_valid(cookies):
    result = False
    res = requests.get(f"https://{LITRES_DOMAIN_NAME}", cookies=cookies)
    if res.ok:
        content_list = res.text.split("/me/profile/")
        if len(content_list) > 1:
            result = True

    return result


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    parser = argparse.ArgumentParser(
        description=f"Загрузчик аудиокниг с сайта {LITRES_DOMAIN_NAME} ДОСТУПНЫХ ПОЛЬЗОВАТЕЛЮ ПО ПОДПИСКЕ "
    )
    parser.add_argument(
        "-b",
        "--browser",
        help=f"Будет эмулироваться User agent этого браузера. По умолчанию: chrome",
        default="chrome",
        choices=["chrome", "edge", "firefox", "safari"],
    )
    parser.add_argument(
        "--cookies-file",
        help="Файл содержащий cookies. Нужно предварительно сформировать скриптом create-cookies.py \
            По умолчанию: cookies.json",
        default="cookies.json",
    )
    parser.add_argument("-o", "--output", help="Путь к папке загрузки", default=".")
    parser.add_argument("--url", help="Адрес (url) страницы с книгой", default="")

    args = parser.parse_args()
    logger.info(args)

    if len(args.cookies_file) > 0:
        if Path(args.cookies_file).is_file():
            logger.info(f"Try to get cookies from file {args.cookies_file}")
            cookies_dict = json.loads(Path(args.cookies_file).read_text())
            cookies = cookiejar_from_dict(cookies_dict)

            # Проверим, что куки из файла валидные, иначе сбросим их
            if not cookies_is_valid(cookies):
                logger.error(f"The cookies in the file {args.cookies_file} is invalid")
                exit(0)

    if len(args.url) > 0:
        download_book(args.url, args.output, args.browser, cookies=cookies)

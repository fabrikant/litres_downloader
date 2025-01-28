import requests
from pathvalidate import sanitize_filename
import argparse
import logging
from pathlib import Path
from fake_useragent import UserAgent
from tqdm import tqdm
import shutil
import re
import sys
import subprocess
import json
from requests.utils import cookiejar_from_dict

from opf import book_info_to_xml, if_to_fi
from common import LITRES_DOMAIN_NAME, cookies_is_valid
from tg_sender import send_to_telegram, send_file_to_telegram
from common_arguments import create_common_args, parse_args


logger = logging.getLogger(__name__)
CLEANR = re.compile("<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});")
api_url = f"https://api.{LITRES_DOMAIN_NAME}/foundation/api/arts/"


def close_programm(msg, tg_api_key, tg_chat_id):
    send_to_telegram(msg, tg_api_key, tg_chat_id)
    exit(0)


def get_headers():
    ua = UserAgent()
    agent = ua.firefox
    return {
        "User-Agent": agent,
    }


def download_content_file(url, path, filename, cookies, headers, progress_bar):
    err_msg = ""
    logger.info(f"Загрузка файла: {url}")
    full_filename = Path(path) / sanitize_filename(filename)

    res = requests.get(url, stream=True, cookies=cookies, headers=headers)
    if res.ok:
        if progress_bar:
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
                    err_msg = f"Не удалось загрузить файл: {url}"
                    logger.error(err_msg)
                    return err_msg
        else:
            with open(full_filename, "wb") as f:
                shutil.copyfileobj(res.raw, f)
    else:
        err_descr = ""
        try:
            err_descr = f"({str(res.json())})"
        except:
            pass
        err_msg = f"Ошибка: {res.status_code} {err_descr} файл: {url}"
        logger.error(err_msg)
        return err_msg
    return err_msg


def get_book_info(json_data):
    book_info = {
        "url": f'https://{LITRES_DOMAIN_NAME}{json_data["url"]}',
        "id": json_data["id"],
        "title": json_data["title"],
        "author": "",
        "authors": [],
        "narrator": "",
        "narrators": [],
        "series": "",
        "series_count": 0,
        "series_num": 0,
        "genres": [],
        "cover": json_data["cover_url"],
        "tags": [],
        "description": re.sub(CLEANR, "", json_data["html_annotation"]),
        "isbn": json_data["isbn"],
        "publishedYear": json_data["publication_date"].split("-")[0],
        "publishedDate": json_data["publication_date"],
        "uuid": json_data["uuid"],
    }

    for person_info in json_data["persons"]:

        person_name = if_to_fi(person_info["full_name"])
        if person_info["role"] == "author":
            book_info["authors"].append(person_name)
            if book_info["author"] == "":
                book_info["author"] = person_name

        if person_info["role"] == "reader":
            book_info["narrators"].append(person_name)
            if book_info["narrator"] == "":
                book_info["narrator"] = person_name

    for genre in json_data["genres"]:
        book_info["genres"].append(genre["name"].lower())

    for series_info in json_data["series"]:
        if "name" in series_info and series_info["name"] != None:
            book_info["series"] = series_info["name"]
        if "arts_count" in series_info and series_info["arts_count"] != None:
            book_info["series_count"] = series_info["arts_count"]
        if "art_order" in series_info and series_info["art_order"] != None:
            book_info["series_num"] = series_info["art_order"]
        break

    for tag in json_data["tags"]:
        book_info["tags"].append(tag["name"].lower())

    return book_info


def get_book_folder(output, book_info):
    book_folder = Path(output)
    if book_info["author"] != "":
        book_folder = Path(book_folder) / sanitize_filename(book_info["author"])

    if book_info["series"] != "":
        book_folder = Path(book_folder) / sanitize_filename(book_info["series"])

    if book_info["series_num"] > 0:
        book_folder = Path(book_folder) / sanitize_filename(
            f'{book_info["series_num"]:02d} - {book_info["title"]} - читает {book_info["narrator"]}'
        )
    else:
        book_folder = Path(book_folder) / sanitize_filename(book_info["title"])
    Path(book_folder).mkdir(exist_ok=True, parents=True)
    return book_folder


def download_cover(book_folder, book_info):
    filename = Path(book_folder) / "cover.jpg"
    url_string = f'https://{LITRES_DOMAIN_NAME}{book_info["cover"]}'
    res = requests.get(url_string, stream=True)
    if res.ok:
        res.raw.decode_content = True
        with open(filename, "wb") as f:
            shutil.copyfileobj(res.raw, f)
    else:
        err_msg = f"Ошибка: {res.status_code} ({str(res.json())}) GET {url_string}"
        logger.warning(err_msg)


def create_metadata_file(book_folder, book_info):
    filename = Path(book_folder) / "metadata.opf"
    xml = book_info_to_xml(book_info)
    Path(filename).write_text(xml)


def download_book(
    url,
    output,
    cookies,
    tg_api_key,
    tg_chat_id,
    progress_bar,
    load_cover,
    create_metadata,
    send_fb2_via_telegram,
):
    headers = get_headers()
    book_id = url.split("-")[-1].split("/")[0]

    url_string = api_url + book_id
    res = requests.get(url_string, cookies=cookies, headers=headers)
    if not res.ok:
        err_msg = f"Ошибка: {res.status_code} ({str(res.json())}) GET {url_string}"
        logger.error(err_msg)
        close_programm(err_msg, tg_api_key, tg_chat_id)

    book_info = get_book_info(res.json()["payload"]["data"])
    release_file_id = res.json()["payload"]["data"]["linked_arts"][0]["release_file_id"]
    msg = f"Начало загрузки книги:\n{book_info['title']}\nавтор: {book_info['author']}"
    logger.debug(msg)
    send_to_telegram(msg, tg_api_key, tg_chat_id)

    book_folder = get_book_folder(output, book_info)
    logger.info(f"Загрузка файлов в каталог: {book_folder}")

    # Загрузка обложки
    if load_cover:
        download_cover(book_folder, book_info)
    # Формирование файла метаданных
    if create_metadata:
        create_metadata_file(book_folder, book_info)

    # Список файлов для загрузки
    url_string = url_string + "/files/grouped"
    res = requests.get(url_string, cookies=cookies, headers=headers)
    if not res.ok:
        err_msg = f"Ошибка: {res.status_code} ({str(res.json())}) GET {url_string}"
        logger.error(err_msg)
        close_programm(err_msg, tg_api_key, tg_chat_id)

    groups_info = res.json()["payload"]["data"]
    for group_info in groups_info:
        # Загрузка mp3
        if "standard_quality_mp3" in group_info["file_type"]:
            files_info = group_info["files"]
            for file_info in files_info:
                file_id = file_info["id"]
                filename = file_info["filename"]
                file_url = f"https://www.{LITRES_DOMAIN_NAME}/download_book_subscr/{book_id}/{file_id}/{filename}"
                err_msg = download_content_file(
                    file_url, book_folder, filename, cookies, headers, progress_bar
                )
                if err_msg != "":
                    close_programm(err_msg, tg_api_key, tg_chat_id)
        elif "unknown" in group_info["file_type"] and type(group_info["files"]) == type(
            []
        ):
            for file_spec in group_info["files"]:
                if file_spec["extension"] == "fb2.zip":
                    file_id = file_spec["id"]
                    filename = file_spec["filename"]
                    # file_url = f"https://www.{LITRES_DOMAIN_NAME}/download_book_subscr/{book_id}/{file_id}/json"
                    file_url = f"https://www.{LITRES_DOMAIN_NAME}/download_book_subscr/{book_id}/{file_id}/fb2/zip"
                    err_msg = download_content_file(
                        file_url, book_folder, filename, cookies, headers, progress_bar
                    )
                    if err_msg != "":
                        close_programm(err_msg, tg_api_key, tg_chat_id)
                    # Файл загружен без ошибки, попробуем отправить его в телеграм
                    if send_fb2_via_telegram and tg_api_key != "" and tg_chat_id != "":
                        full_filename = Path(book_folder) / filename
                        send_file_to_telegram(full_filename, tg_api_key, tg_chat_id)
                        # Если отправили файл в телеграм, нет смысла дополнительно
                        # сообщать об успешной загрузке. Выходим из программы.
                        exit(0)
    msg = (
        f"Окончание загрузки книги:\n{book_info['title']}\nавтор: {book_info['author']}"
    )
    logger.debug(msg)
    send_to_telegram(msg, tg_api_key, tg_chat_id)
    if sys.platform != "win32":
        subprocess.Popen(f"chmod -R ugo+wrX '{str(book_folder)}'", shell=True)


if __name__ == "__main__":

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.ERROR,
    )
    # Создаем общие аргументы для всех качалок
    parser = create_common_args(
        f"Загрузчик аудиокниг с сайта {LITRES_DOMAIN_NAME} ДОСТУПНЫХ ПОЛЬЗОВАТЕЛЮ ПО ПОДПИСКЕ"
    )
    # Добавляем специфические аргументы для данной качалки
    parser.add_argument(
        "--send-fb2-via-telegram",
        help="Отправлять fb2 файлы книг через телеграм бота (требуется задать --telegram-api и --telegram-chatid)",
        action=argparse.BooleanOptionalAction,
        default=False,
    )
    parser.add_argument(
        "--progressbar",
        help="Показывать прогресс для каждого файла",
        action=argparse.BooleanOptionalAction,
        default=False,
    )
    parser.add_argument(
        "--cookies-file",
        help=(
            "Файл содержащий cookies. Нужно предварительно сформировать скриптом create-cookies.py "
            "или извлечь из браузера скриптом get_browser_cookies.py"
            "По умолчанию: cookies.json в каталоге скрипта"
        ),
        default="cookies.json",
    )

    args = parse_args(parser, logger)
    logger.info(args)

    if Path(args.cookies_file).is_file():
        logger.info(f"Попытка извлечь cookies из файла {args.cookies_file}")
        cookies_dict = json.loads(Path(args.cookies_file).read_text())
        cookies = cookiejar_from_dict(cookies_dict)

        # Проверим, что куки из файла валидные, иначе прервем выполнение
        err_msg = cookies_is_valid(cookies, args.telegram_api, args.telegram_chatid)
        if not err_msg == "":
            close_programm(err_msg, args.telegram_api, args.telegram_chatid)
    else:
        err_msg = f"Не найден файл с cookies: {args.cookies_file}"
        logger.error(err_msg)
        close_programm(err_msg, args.telegram_api, args.telegram_chatid)

    download_book(
        args.url,
        args.output,
        cookies,
        args.telegram_api,
        args.telegram_chatid,
        args.progressbar,
        args.cover,
        args.metadata,
        args.send_fb2_via_telegram,
    )

import argparse
import logging
from pathlib import Path
from download_book import download_book, cookies_is_valid
import json
from requests.utils import cookiejar_from_dict

logger = logging.getLogger(__name__)

def download_books(input, output, browser, cookies):
    with open(input, "r") as f:
        for url in f:
            url_trim = url.strip()
            if "litres.ru" in url_trim:
                logger.info(f"Адрес к загрузке: {url_trim}")
                download_book(url_trim, output, browser, cookies)


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    parser = argparse.ArgumentParser(
        description="Загрузчик аудиокниг доступных по подписке с сайта litres.ru. \n Прежде чем использовать скрипт, небходимо в браузере залогиниться на сайте. \n Загрузчик использует cookies из браузера."
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
    parser.add_argument(
        "-i",
        "--input",
        help="Путь к файлу со списком url книг к загрузке. Каждый адрес с новой строки",
        default="queue.txt",
    )
    parser.add_argument("-o", "--output", help="Путь к папке загрузки", default=".")

    args = parser.parse_args()
    logger.info(args)

    if len(args.cookies_file) > 0:
        if Path(args.cookies_file).is_file():
            logger.info(f"Try to get cookies from file {args.cookies_file}")
            cookies_dict = json.loads(Path(args.cookies_file).read_text())
            cookies = cookiejar_from_dict(cookies_dict)

            # Проверим, что куки из файла валидные, иначе сбросим их
            err_msg = cookies_is_valid(cookies)
            if err_msg != "":
                logger.error(f"The cookies in the file {args.cookies_file} is invalid")
                exit(0)

    download_books(args.input, args.output, args.browser, cookies)

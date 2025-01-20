import argparse
import logging
from pathlib import Path
from download_book import (
    download_book,
    cookies_is_valid,
    close_programm,
    LITRES_DOMAIN_NAME,
)
import json
from requests.utils import cookiejar_from_dict
from common_arguments import create_common_args_without_url, parse_args

logger = logging.getLogger(__name__)


def download_books(
    input,
    output,
    cookies,
    tg_api_key,
    tg_chat_id,
    progressbar,
    load_cover,
    create_metadata,
):
    with open(input, "r") as f:
        for url in f:
            url_trim = url.strip()
            if "litres.ru" in url_trim:
                logger.info(f"Адрес к загрузке: {url_trim}")
                download_book(
                    url_trim,
                    output,
                    cookies,
                    tg_api_key,
                    tg_chat_id,
                    progressbar,
                    load_cover,
                    create_metadata,
                )


if __name__ == "__main__":

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.ERROR,
    )
    # Создаем общие аргументы для всех качалок
    parser = create_common_args_without_url(
        f"Загрузчик аудиокниг с сайта {LITRES_DOMAIN_NAME} ДОСТУПНЫХ ПОЛЬЗОВАТЕЛЮ ПО ПОДПИСКЕ. Позволяет скачать несколько книг."
    )
    # Добавляем специфические аргументы для данной качалки
    parser.add_argument(
        "--progressbar",
        help="Показывать прогресс для каждого файла",
        action=argparse.BooleanOptionalAction,
        default=False,
    )
    parser.add_argument(
        "--cookies-file",
        help="Файл содержащий cookies. Нужно предварительно сформировать скриптом create-cookies.py \
            По умолчанию: cookies.json в каталоге скрипта",
        default="cookies.json",
    )
    parser.add_argument(
        "-i",
        "--input",
        help="Путь к файлу со списком url книг к загрузке. Каждый адрес с новой строки",
        default="queue.txt",
    )

    args = parse_args(parser, logger, check_url=False)
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

    download_books(
        args.input,
        args.output,
        cookies,
        args.telegram_api,
        args.telegram_chatid,
        args.progressbar,
        args.cover,
        args.metadata,
    )

import argparse
import logging


def create_common_args_without_url(app_description):
    parser = argparse.ArgumentParser(description=app_description)
    parser.add_argument(
        "--verbose",
        "-v",
        help="Уровень логирования по умолчанию (если ключ не задан) - error. warning -v, info -vv, debug -vvv",
        action="count",
        default=0,
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
    parser.add_argument(
        "--cover",
        help="Загружать|Не загружать обложку (файл cover.jpg)",
        action=argparse.BooleanOptionalAction,
        default=False,
    )
    parser.add_argument(
        "--metadata",
        help="Создавать|Не создавать файл метаданных",
        action=argparse.BooleanOptionalAction,
        default=False,
    )
    parser.add_argument("-o", "--output", help="Путь к папке загрузки", default=".")
    return parser


def create_common_args(app_description):
    parser = create_common_args_without_url(app_description)
    parser.add_argument("--url", help="Адрес (url) страницы с книгой", default="")
    return parser


def parse_args(parser, logger, check_url=True):
    try:
        args = parser.parse_args()
    except:
        exit(0)

    log_level = logging.ERROR
    if args.verbose == 1:
        log_level = logging.WARNING
    elif args.verbose == 2:
        log_level = logging.INFO
    elif args.verbose > 2:
        log_level = logging.DEBUG

    logger.setLevel(log_level)

    if check_url:
        if len(args.url) == 0:
            logger.error("Не задан ключ --url")
            exit(0)

    return args

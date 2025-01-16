import argparse
import logging

def create_common_args(app_description):
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
    parser.add_argument("-o", "--output", help="Путь к папке загрузки", default=".")
    parser.add_argument("--url", help="Адрес (url) страницы с книгой", default="")
    
    return parser

def check_common_args(parser, logger):
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
    
    if len(args.url) == 0:
        logger.error("Не задан ключ --url")
        exit(0)
        
    return  args  
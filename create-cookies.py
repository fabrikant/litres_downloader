import random
import logging
import time
from pathlib import Path
import json
from requests.utils import dict_from_cookiejar

try:
    import cookielib
except ImportError:
    import http.cookiejar as cookielib
import argparse

from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.firefox.service import Service as firefox_service
from webdriver_manager.firefox import GeckoDriverManager

from selenium.webdriver.chrome.service import Service as chrome_service
from webdriver_manager.chrome import ChromeDriverManager

LITRES_DOMAIN_NAME = "litres.ru"


logger = logging.getLogger(__name__)


def get_firefox_driver():
    executable_path = GeckoDriverManager().install()
    options = webdriver.FirefoxOptions()
    # options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--single-process")
    options.add_argument("--disable-dev-shm-usage")
    service = firefox_service(executable_path=executable_path)
    return webdriver.Firefox(service=service, options=options)


def get_chrome_driver():
    executable_path = ChromeDriverManager().install()
    options = webdriver.ChromeOptions()
    # options.add_argument("headless")
    service = chrome_service(executable_path=executable_path)
    return webdriver.Chrome(service=service, options=options)


def to_cookielib_cookie(selenium_cookie):
    return cookielib.Cookie(
        version=0,
        name=selenium_cookie["name"],
        value=selenium_cookie["value"],
        port="80",
        port_specified=False,
        domain=selenium_cookie["domain"],
        domain_specified=True,
        domain_initial_dot=False,
        path=selenium_cookie["path"],
        path_specified=True,
        secure=selenium_cookie["secure"],
        expires=(
            selenium_cookie["expiry"] if ("expiry" in selenium_cookie.keys()) else None
        ),
        discard=False,
        comment=None,
        comment_url=None,
        rest=None,
        rfc2109=False,
    )


def put_cookies_in_jar(selenium_cookies):
    cookie_jar = cookielib.CookieJar()
    for cookie in selenium_cookies:
        cookie_jar.set_cookie(to_cookielib_cookie(cookie))
    return cookie_jar


def create_cookies(user, password, browser, cookies_file):

    if "chrome" in browser:
        driver = get_chrome_driver()
    else:
        driver = get_firefox_driver()

    driver.implicitly_wait(10)

    # driver.get("https://www.litres.ru/")
    # enter_button = driver.find_element(By.LINK_TEXT, '/auth/login')
    # enter_button.click()

    driver.get(f"https://www.{LITRES_DOMAIN_NAME}/auth/login")

    id = "auth__input--enterEmailOrLogin"
    field = driver.find_element(By.ID, "auth__input--enterEmailOrLogin")
    field.send_keys(user)
    time.sleep(random.randint(2, 5))
    ActionChains(driver).key_down(Keys.SHIFT).send_keys(Keys.ENTER).perform()
    time.sleep(random.randint(3, 6))
    field = driver.find_element(By.NAME, "pwd")
    field.send_keys(password)
    time.sleep(random.randint(3, 5))
    ActionChains(driver).key_down(Keys.SHIFT).send_keys(Keys.ENTER).perform()
    time.sleep(random.randint(5, 9))

    cookies = driver.get_cookies()
    logger.info(cookies)
    driver.quit()
    
    Path(args.cookies_file).write_text(
            json.dumps(dict_from_cookiejar(put_cookies_in_jar(cookies))))
    
    

if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    parser = argparse.ArgumentParser(
        description=f"Создает файл cookies по имени пользователя и паролю от сайта {LITRES_DOMAIN_NAME} для \
            дальнейшего использования со скриптом закачки книг"
    )
    parser.add_argument(
        "-b",
        "--browser",
        help=f"Браузер в котором будут формироваться cookies. По умолчанию: chrome",
        default="chrome",
        choices=["chrome", "firefox"],
    )
    parser.add_argument("-u", "--user", help="Имя пользователя", default="")
    parser.add_argument("-p", "--password", help="Пароль", default="")
    parser.add_argument(
        "--cookies-file",
        help="Cookies сохранятся в этот файл. По умолчанию: cookies.json",
        default="cookies.json",
    )
    args = parser.parse_args()
    logger.info(args)
    create_cookies(args.user, args.password, args.browser, args.cookies_file)
    # litres202412@n-drive.cf', 'fiix9Ai7Aev3Iej6koo5'
# litres_downloader
Загружает файлы книг и аудиокниг доступные по подписке с сайта [Литрес](https://litres.ru).
Данный скрипт не позволяет скачать книги, которые вам недоступны. Другими словами, если у вас оформлена подписка, но вам не нравится приложение литрес, есть возможность скачать файлы и слушать (читать) в альтернативных плеерах (читалках).
>**ХОЗЯЙКЕ НА ЗАМЕТКУ**
>
> - Для регистрации на [Литрес](https://litres.ru) достаточно адреса электронной почты
> - Первый месяц подписки - бесплатный

Скрипт может использоваться самостоятельно, но предназначен для работы с телеграм ботом [tg-combine](https://github.com/fabrikant/tg-combine)

# Требования
1. Операционная система **Linux** тестировалось на ubuntu 24.04. На **Windows** должно работать, но не тестировалось.
1. Установленный [python3](https://www.python.org/) и venv. Чем новее, тем лучше. Тестировалось на 3.12.

1. Установленный браузер (тестировалось на **firefox**), в котором разрешены куки. Браузер нужен для формирования/извлечения файла cookies. 
    
    - Сформирвать файл cookies по имени пользователя и паролю можно в браузере **firefox** и **chrome**

    - Извлечь cookies потенциально возможно из браузеров: **chrome, chromium, vivaldi, edge, firefox, safari**. Проверялось на firefox.

>**ВАЖНО!!!** 
>
>1. **firefox** snap установленный в ubuntu по умолчанию не работает. Нужно его удалить и установить из deb пакета или tarball с [официального сайта](https://www.mozilla.org/en-US/firefox/)
>
>1. Из-за ошибки компонента [browsercookie](https://pypi.org/project/browsercookie/) попытка извлечь cookies из браузера chrome завершается с ошибкой. Возможно в будущем разработчики её исправят


# Установка
Скачиваем любым способом исходный код. Например:  
```bash
git clone https://github.com/fabrikant/litres_audiobooks_downloader.git
```
Переходим в каталог с исходным кодом и выполняем команду  
**Linux:**
```bash
./install.sh
```
**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
deactivate
```

# Использование на Linux и Windows
**Linux**

Если установка произведена с помощью скрипта ./install.sh, то для запуска можно воспользоваться скриптами: ***create-cookies.sh, get-browser-cookies.sh, download-book.sh, multiloader.sh***
При их использовании будет автоматически активировано виртуальное окружение, вызван скрипт python, а по окончанию работы деактивировано виртуальное окружение.

>**ВАЖНО!!!**
>
>**Для получения справки по доступным ключам, любой скрипт можно вызвать с параметром -h или --help.**

**Windows**

Если при установке создавалось виртуальное окружение, то перед запуском скриптов необходимо активировать его командой:
```
venv\Scripts\activate
```
Далее скрипты вызываются командами аналогичными Linux. Вместо *sh* файла linux запускается соответствующий python файл. Например:
```
python3 download_book.py --help
```

# Использование

1. Перед загрузкой книг необходимо сформировать файл cookies. Путь к этому файлу будет передаваться всякий раз в качестве параметра при загрузке книг. Сформировать файл cookies можно двумя способами:
 - **Извлечь файл cookies из браузера**. Для этого предварительно нужно открыть браузер и войти в свой аккаунт на сайте [Литрес](litres.ru), после чего закрыть браузер и воспользоваться командой:
 
    ```bash
    ./get-browser-cookies.sh -b {firefox} --cookies-file {/tmp/cookies-file.json}
    ```
    >*Значения в фигурных скобках нужно заменить на свои.*
- Сформировать файл cookies с помщью имени/пароля и браузера **firefox** или **chrome**
    ```bash
    ./create-cookies.sh -b {firefox} -u {your_user_name} -p {password} --cookies-file {/tmp/cookies-file.json}
    ```
    >*Значения в фигурных скобках нужно заменить на свои.*

2. Загрузка одной книги:

    ```bash
    ./download-book.sh --cookies-file {/tmp/cookies-file.json} --output {/tmp/audiobooks} --url {https://www.litres.ru/audiobook/sebastyan-fitcek/pacient-osoboy-kliniki-54990486/}
    ``` 
    >*Значения в фигурных скобках нужно заменить на свои.*

3. Загрузка списка книг:
    - Предварительно создать файл (например /tmp/queue.txt) со списком адресов. Одна строка - один адрес. Комментарии не допускаются. Пустые строки допускаются.
    - Выполнить команду:
    ```bash
    ./multiloader.sh --cookies-file {/tmp/cookies-file.json} --output {/tmp/audiobooks} --input {/tmp/queue.txt}
    ``` 
    >*Значения в фигурных скобках нужно заменить на свои.*

# Примечания
 - Ссылку нужно брать именно со страницы книги/аудиокниги. Если вам нужна текстовая версия, нажмите кнопку "Текст", для аудиокниги - "Аудио". Идентификаторы текстового варианта и аудио варианта одной и той же книги отличаются. Текстовый вариант в строке адреса содержит подстроку "/book/", а аудиокнига "/audiobook/".
- Текстовый вариант книги можно отправить себе в телеграм через бота.
- Аудиовариант нельзя отправить в телеграм, так как существуют жесткие ограничения по размеру файлов, которые могут отправлять боты.
 - Если используете телеграм бота, напишите ему что-нибудь. Боты не могут отправлять сообщения пользователям, которые к ним (к ботам) не обращались.

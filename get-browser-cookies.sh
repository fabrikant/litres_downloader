#! /bin/bash
DIR=$(dirname $0)
cd $DIR
source .venv/bin/activate
python3 get_browser_cookies.py $@
deactivate
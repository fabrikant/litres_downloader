#! /bin/bash
DIR=$(dirname $0)
cd $DIR
source .venv/bin/activate
python3 create_cookies.py $@
deactivate
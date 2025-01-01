#! /bin/bash
DIR=$(dirname $0)
cd $DIR
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
pip insatll -r requirements.txt
deactivate
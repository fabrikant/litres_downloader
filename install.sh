#! /bin/bash
DIR=$(dirname $0)
cd $DIR
python3 -m venv .venv
source .venv/bin/activate
pip insatll -r requirement.txt
deactivate
#!/bin/bash
# do necessary inital tasks

git pull
git submodule update --recursive --remote --init

pip3 install -r requirements.txt

cd ./viewer-framework
python3 manage.py createcachetable
# python3 manage.py makemigrations viewer example_app
python3 manage.py migrate
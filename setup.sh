#!/bin/bash
# do necessary inital tasks

pip install -r requirements.txt

cd ./viewer-framework
python3 manage.py createcachetable
python3 manage.py makemigrations viewer
python3 manage.py migrate
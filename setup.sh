#!/bin/bash
# do necessary inital tasks

pip install -r requirements.txt

cd ./viewer-framework
python3 manage.py createcachetable
python3 manage.py makemigrations viewer mturk_manager
python3 manage.py migrate
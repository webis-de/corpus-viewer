#!/bin/bash
# do necessary inital tasks

python3 manage.py createcachetable
python3 manage.py makemigrations viewer example_app
python3 manage.py migrate
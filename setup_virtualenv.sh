#!/bin/bash
# do necessary inital tasks

mkdir venv_viewer
virtualenv -p python3 venv_viewer/

venv_viewer/bin/pip install django==1.10.6
venv_viewer/bin/pip install whoosh==2.7.4
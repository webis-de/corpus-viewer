#!/bin/bash
# do necessary inital tasks

mkdir venv_viewer
python3 -m venv venv_viewer/

venv_viewer/bin/pip install django==1.10.6
venv_viewer/bin/pip install whoosh==2.7.4
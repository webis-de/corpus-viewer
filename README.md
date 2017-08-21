# Corpus-Viewer
This repository houses a tool which loads any arbitrary corpus and provides an extensive user interface to explore the data. 

The user has to provide one single property file for each corpus. This file defines the overall structure of the corpus and how to load the corpus into the tool.  
The instructions of how to write that file can be found in the 'Documentation'-page inside of the tool.  

The whole tool is built on top of the [Django-Framework](https://www.djangoproject.com/).  
By default the tool uses the pure-Python search-engine [Whoosh](https://pypi.python.org/pypi/Whoosh/) to make each corpus searchable.

## Requirements
* Python 3.x _(tested with version 3.5)_
* virtualenv

## Installation
1. run `./setup_virtualenv.sh` to setup the virtual environment and to install Django and Whoosh
2. run `./setup_django.sh` to setup the required Django database tables

## Quickstart
1. run 'cd viewer-framework'
1. run `python manage.py runserver` to start the server _([more](https://docs.djangoproject.com/en/1.10/ref/django-admin/#django-admin-runserver) on how to start a django server)_

## Supported Features
* loading of arbitrary corpora
* no need to preprocess the corpus due to custom loading function (scripted in python)
* integrated loading of corpora stored in a in ldjson- or csv-file
* multiple convenient ways to assign tags to your corpus items
* export the whole or parts of the corpus into a ldjson- or csv-file

## Upcomming Features
* (better) support for mobile devices 
* configurable item view with web components

## Known Bugs

## Contributors
* Kristof Komlossy
* Martin Potthast
* Matthias Hagen

## Contact
You found a bug or you have questions/requests?  
Write me a mail: kristof.komlossy@uni-weimar.de
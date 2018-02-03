# Corpus-Viewer
This repository houses a tool which loads any arbitrary corpus and provides an extensive user interface to explore the data. 

The user has to provide one single property file for each corpus. This file defines the overall structure of the corpus and how to load the corpus into the tool.  
The instructions of how to write that file can be found in the 'Documentation'-page inside of the tool.  

The whole tool is built on top of the [Django-Framework](https://www.djangoproject.com/).  
By default the tool uses the pure-Python search engine [Whoosh](https://pypi.python.org/pypi/Whoosh/) to make each corpus searchable.

## Requirements
* Python 3.5+

## Installation
**Note:** If you want to use a virtual environment like `virtualenv` switch to the virtual environment before executing the following step(s)!

1. Run `./setup.sh`

## Quickstart
1. Run `cd viewer-framework`
1. Run `python manage.py runserver` to start the server _([more](https://docs.djangoproject.com/en/1.10/ref/django-admin/#django-admin-runserver) on how to start a django server)_
3. Visit [localhost:8000](http://localhost:8000)

## Supported Features
* Loading of arbitrary corpora
* No need to preprocess the corpus due to custom loading function (scripted in python)
* Integrated loading of corpora stored in a in ldjson- or csv-file
* Load corpora stored in PostgreSQL, MySQL, SQLite or Oracle databases
* Different, convenient ways to assign tags to your corpus items
* Export the whole or parts of the corpus into a ldjson- or csv-file
* Configurable item view via html or external source
* Create interface plugins to serve your needs
* Switch from the Whoosh search engine to any other search engine

## Contributors
* Kristof Komlossy
* Martin Potthast
* Matthias Hagen

## Contact
Did you find a bug or do you have questions/requests?
Write me a mail: kristof.komlossy@uni-weimar.de
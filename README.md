# Corpus-Viewer
This repository houses a tool which loads any arbitrary corpus and provides an extensive user interface to explore the data. 

The user has to provide one single property file for each corpus. This file defines the overall structure of the corpus and how to load the corpus into the tool.
The instructions of how to write that file can be found in the 'Documentation'-page inside of the tool.  

The whole tool is built on top of the [Django-Framework](https://www.djangoproject.com/).
By default the tool uses the pure-Python search-engine [Whoosh](https://pypi.python.org/pypi/Whoosh/) to make each corpus searchable.

## Requirements
* Python 3.x _(tested with version 3.5)_
* Pip _(tested with version 9.0.1)_

## Installation
1. run `sudo ./install.sh` to install Django and Whoosh
2. run `./setup_django.sh` to setup the required Django database tables
3. run `python3 manage.py runserver` to start the server

## Contributors
* Kristof Komlossy
* Martin Potthast
* Matthias Hagen

## Contact
You found a bug or you have questions/requests?
Write me a mail: kristof.komlossy@uni-weimar.de
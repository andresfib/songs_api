# Song Challenge #

A small Flask API that queries a locally hosted MongoDB collection of songs

## Installing ##

`pipenv install`

## Running ##

`export FLASK_APP=__init__.py; export FLASK_DEBUG=1; pipenv run flask run`

You can specify the database name where your song collection resides. E.g.:

`export SONGS_DB=yousician-andres; export FLASK_APP=__init__.py; export FLASK_DEBUG=1; pipenv run flask run`

## Testing ##

`pipenv run python -m unittest discover -s tests`
'

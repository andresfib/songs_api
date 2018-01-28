# Song Challenge #

A small Flask API that queries a MongoDB collection of songs.

You can specify where your song collection resides. E.g.:

`export SONGS_DB_URI=mongodb://localhost/app_songs`

## Installing ##

`pipenv install`

## Running ##

`export FLASK_APP=__init__.py; export FLASK_DEBUG=1; pipenv run flask run`

## Testing ##

`pipenv run python -m unittest discover -s tests`
'

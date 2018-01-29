# Song Challenge #

A small Flask API that queries a MongoDB collection of songs.

It uses [pipenv](https://docs.pipenv.org) to install the packages and run the app.

You can specify the database where your song collection resides with its [URI](https://docs.mongodb.com/manual/reference/connection-string/):

`export SONGS_DB_URI=mongodb://localhost/app_songs`

## Installing ##

`pipenv install`

## Debugging ##

`export FLASK_APP=songs_app.py; export FLASK_DEBUG=1; pipenv run flask run`

## Running ##

`export FLASK_APP=songs_app.py;export FLASK_DEBUG=0; pipenv run flask run`

## Testing ##

`pipenv run python -m unittest discover -s tests`
'

from flask import Flask

import pymongo

from .songs_api import songs_api
from .models import mongo


def create_app(database):
    app = Flask(__name__)

    app.config['MONGO_DBNAME'] = database
    app.config["JSONIFY_PRETTYPRINT_REGULAR"] = False
    mongo.init_app(app)
    with app.app_context():
        mongo.db.songs.create_index([('title', pymongo.TEXT), ('artist', pymongo.TEXT)])

    app.register_blueprint(songs_api)
    return app

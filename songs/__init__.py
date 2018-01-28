import pymongo

from .songs_api import songs_api
from .models import mongo
from .api_utils import FlaskApi


def create_app(database):
    app = FlaskApi(__name__)

    app.config['MONGO_URI'] = database
    mongo.init_app(app)
    with app.app_context():
        mongo.db.songs.create_index([('title', pymongo.TEXT), ('artist', pymongo.TEXT)])

    app.register_blueprint(songs_api)
    return app

from flask import Flask, jsonify, make_response
from flask_pymongo import PyMongo
import pymongo

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'yousician-andres'
mongo = PyMongo(app)
with app.app_context():
    mongo.db.songs.create_index([('title', pymongo.TEXT), ('artist', pymongo.TEXT)])

@app.route('/songs')
def get_songs():
    songs = mongo.db.songs.find({}, {'_id': 0})
    result = []
    for song in songs:
        result.append(song)
    return jsonify(result)

@app.route('/songs/avg/difficulty', defaults={'level': None})
@app.route('/songs/avg/difficulty/<int:level>')
def get_avg_difficulty(level):
    pipeline = []
    if level is not None:
        pipeline.append({'$match': {'level': int(level)}})

    pipeline.append(
        {'$group': {
            '_id': 'null',
            'avg_difficulty': {'$avg': '$difficulty'}
            }
        })

    avg = mongo.db.songs.aggregate(pipeline)

    #There should only be one document returned
    try:
        result = avg.next()
    except StopIteration:
        #The given level does not exist
        return make_response("", 404)

    result['avg_difficulty'] = round(result['avg_difficulty'], 2)

    return jsonify(result)

if __name__ == '__main__':
    app.run()

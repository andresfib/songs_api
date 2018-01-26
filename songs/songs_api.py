from flask import jsonify, Response, Blueprint, request
from bson.json_util import dumps
from bson.objectid import ObjectId
from .models import mongo

songs_api = Blueprint('songs_api', __name__)


@songs_api.route('/songs')
def get_songs():
    # TODO: Paginate
    cursor = mongo.db.songs.find({})
    return cursor_to_response(cursor)


@songs_api.route('/songs/avg/difficulty')
def get_avg_difficulty():
    pipeline = []
    level = request.args.get('level', None)
    if level is not None:
        try:
            level = int(level)
        except ValueError:
            return invalid_usage('Level should be an int')
        pipeline.append({'$match': {'level': level}})

    pipeline.append({
        '$group': {
            '_id': 'null',
            'avg': {'$avg': '$difficulty'}
        }
    })

    avg = mongo.db.songs.aggregate(pipeline)

    # There should only be one document returned
    try:
        result = avg.next()
    except StopIteration:
        return invalid_usage('Level does not exist in the database')

    result = {
        'avg': round(result['avg'], 2),
        'level': level}
    return jsonify(result)


@songs_api.route('/songs/search')
def search_songs():
    message = request.args.get('message', None)
    if message is None:
        return jsonify({})

    query = make_and_text_query(message)
    cursor = mongo.db.songs.find({'$text': {'$search': query}})
    return cursor_to_response(cursor)


@songs_api.route('/songs/rating', methods=['POST'])
def rate_song():
    # TODO: Validation vouluptous
    song_id = request.args.get('song_id', None)
    rating = request.args.get('rating', None)

    mongo.db.songs.update_one({'_id': ObjectId(song_id)},
                              {'$push': {'ratings': int(rating)}})
    song = mongo.db.songs.find_one({'_id': ObjectId(song_id)})
    return Response(dumps(song),
                    status=200,
                    mimetype='application/json')

@songs_api.route('/songs/avg/rating')
def get_song_ratings_stats():
    song_id = request.args.get('song_id', None)
    song = mongo.db.songs.find_one({'_id': ObjectId(song_id)}, {'ratings': 1})
    ratings = song['ratings']
    result = {
        'avg': sum(ratings)/float(len(ratings)),
        'max': max(ratings),
        'min': min(ratings)
    }
    return jsonify(result)


def invalid_usage(message, status_code=400):
    response = jsonify({'message': message})
    response.status_code = status_code
    return response


def cursor_to_response(cursor):
    result = []
    for item in cursor:
        result.append(item)
    return Response(dumps(result),
                    status=200,
                    mimetype='application/json')


def make_and_text_query(message):
    return '"' + '" "'.join(message.split()) + '"'

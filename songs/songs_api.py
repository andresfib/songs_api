from bson.objectid import ObjectId
from flask import Blueprint, request
from voluptuous import Schema, Coerce, Optional, Required, All, Length, Match, Range
from .models import mongo
from .api_utils import make_and_text_query, parameter_schema
from .api_utils import ApiResult, ApiException

songs_api = Blueprint('songs_api', __name__)

SONGS_PER_PAGE = 5

@songs_api.route('/songs')
@parameter_schema(Schema({
    Optional('page', default=None): All(Coerce(int), Range(min=1))}))
def get_songs():
    page = request.args['page']
    cursor = {}
    if page is not None:
        skip = (page - 1) * SONGS_PER_PAGE
        cursor = mongo.db.songs.find({}, limit=SONGS_PER_PAGE, skip=skip)
    else:
        cursor = mongo.db.songs.find({})

    result = ApiResult(list(cursor))
    return result.to_response()


@songs_api.route('/songs/avg/difficulty')
@parameter_schema(Schema({Optional('level', default=None): Coerce(int)}))
def get_avg_difficulty():
    pipeline = []
    level = request.args['level']
    if level is not None:
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
        raise ApiException('Level does not exist in the database')

    result = ApiResult({
        'avg': round(result['avg'], 2),
        'level': level})
    return result.to_response()


@songs_api.route('/songs/search')
@parameter_schema(Schema({Required('message'): All(str, Length(min=3))}))
def search_songs():
    message = request.args.get('message', None)
    query = make_and_text_query(message)
    cursor = mongo.db.songs.find({'$text': {'$search': query}})

    result = ApiResult(list(cursor))
    return result.to_response()


@songs_api.route('/songs/rating', methods=['POST'])
@parameter_schema(Schema({
    Required('song_id'): All(str, Match(r'^[a-fA-F0-9]{24}$',
                                        msg='Invalid song_id format')),
    Required('rating'): All(Coerce(int), Range(min=1, max=5))
}))
def rate_song():

    song_id = request.args['song_id']
    rating = request.args['rating']
    mongo.db.songs.update_one({'_id': ObjectId(song_id)},
                              {'$push': {'ratings': int(rating)}})
    song = mongo.db.songs.find_one({'_id': ObjectId(song_id)})

    result = ApiResult(song)
    return result.to_response()


@songs_api.route('/songs/avg/rating')
@parameter_schema(Schema({
    Required('song_id'): All(str, Match(r'^[a-fA-F0-9]{24}$',
                                        msg='Invalid song_id format')),
}))
def get_song_ratings_stats():
    song_id = request.args.get('song_id', None)
    song = mongo.db.songs.find_one({'_id': ObjectId(song_id)}, {'ratings': 1})
    ratings = song['ratings']
    result = ApiResult({
        'avg': sum(ratings)/float(len(ratings)),
        'max': max(ratings),
        'min': min(ratings)
    })
    return result.to_response()


@songs_api.errorhandler(ApiException)
def handle_api_exception(e):
    return e.to_response()


@songs_api.app_errorhandler(Exception)
def handle_unexpected_error(error):
    # Not a real ApiResult but will make a nice response
    result = ApiResult({'message': 'Server error. Contact admin'}, status=500)
    return result.to_response()

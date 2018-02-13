from bson.objectid import ObjectId
from flask import Blueprint
from voluptuous import Schema, Coerce, Optional, Required
from voluptuos import All, Length, Match, Range
import pymongo

from .models import mongo, SONGS_PER_PAGE
from .api_utils import make_and_text_query, parameter_schema
from .api_utils import ApiResult, ApiException

songs_api = Blueprint('songs_api', __name__)
song_id_schema = All(str, Match(r'^[a-fA-F0-9]{24}$',
                                msg='Invalid song_id format'))


@songs_api.route('/songs')
@parameter_schema(
    Schema({
        Optional('page', default=None): All(Coerce(int), Range(min=1)),
        Optional('last_id', default=None): song_id_schema}))
def get_songs(page, last_id):
    '''
    We return songs ordered in descending order by its _id
    If last_id is passed then we used index on _id to get a page faster,
    and ignore page argument.
    If page is passed then we use limit and skip to retrieve page
    The endpoint only returns a list of songs with all their fields, but it
    could be modified to return a dictionary that also includes information
    about the list, like count of returned songs, of _id of last returned song.
    '''
    cursor = {}
    if last_id is not None:
        # If we get last_id then we can produce faster pagination
        cursor = mongo.db.songs.find({'_id': {'$lt': ObjectId(last_id)}},
                                     limit=SONGS_PER_PAGE)
    elif page is not None:
        skip = (page - 1) * SONGS_PER_PAGE
        cursor = mongo.db.songs.find({}, limit=SONGS_PER_PAGE, skip=skip)
    else:
        # No pagination
        cursor = mongo.db.songs.find({})

    result = list(cursor.sort('_id', pymongo.DESCENDING))
    return ApiResult(result)


@songs_api.route('/songs/avg/difficulty')
@parameter_schema(Schema({Optional('level', default=None): Coerce(int)}))
def get_avg_difficulty(level):
    pipeline = []
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
    return result


@songs_api.route('/songs/search')
@parameter_schema(Schema({Required('message'): All(str, Length(min=3))}))
def search_songs(message):
    query = make_and_text_query(message)
    cursor = mongo.db.songs.find({'$text': {'$search': query}})

    return ApiResult(list(cursor))


@songs_api.route('/songs/rating', methods=['POST'])
@parameter_schema(Schema({
    Required('song_id'): song_id_schema,
    Required('rating'): All(Coerce(int), Range(min=1, max=5))
}))
def rate_song(song_id, rating):
    result = mongo.db.songs.update_one({'_id': ObjectId(song_id)},
                                       {'$push': {'ratings': int(rating)}})
    if result.modified_count is 0:
        raise ApiException('Song not found')
    else:
        song = mongo.db.songs.find_one({'_id': ObjectId(song_id)})
        return ApiResult(song)


@songs_api.route('/songs/avg/rating')
@parameter_schema(Schema({Required('song_id'): song_id_schema}))
def get_song_ratings_stats(song_id):
    song = mongo.db.songs.find_one({'_id': ObjectId(song_id)}, {'ratings': 1})
    if song is None:
        raise ApiException('Song not found')

    ratings = song.get('ratings', None)
    if ratings is None:
        raise ApiException('Song has no ratings')

    result = ApiResult({
        'avg': sum(ratings)/float(len(ratings)),
        'max': max(ratings),
        'min': min(ratings)
    })
    return result


@songs_api.errorhandler(ApiException)
def handle_api_exception(e):
    return e.to_result()


@songs_api.app_errorhandler(Exception)
def handle_unexpected_error(error):
    # Not a real ApiResult but will make a nice response
    result = ApiResult({'message': 'Server error. Contact admin'}, status=500)
    # Do some server logging
    print(error)
    return result

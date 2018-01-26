from flask import Flask, jsonify, make_response, Response, Blueprint, request
from bson.json_util import dumps
from flask_pymongo import PyMongo
import pymongo

songs_api = Blueprint('songs_api', __name__)
from .models import mongo

@songs_api.route('/songs')
def get_songs():
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
        return invalid_usage('Level does not exist in the database')

    result = {
        'avg_difficulty': round(result['avg_difficulty'], 2),
        'level': level}
    return jsonify(result)

@songs_api.route('/songs/search')
def search_songs():
    message = request.args.get('message', None)
    if message is None:
        return jsonify({})
    cursor = mongo.db.songs.find({'$text': {'$search': message}})
    return cursor_to_response(cursor)

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

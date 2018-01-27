from flask import Response, jsonify, Flask
from bson.json_util import dumps

'''
Class Api result creates Response object for BSON/JSON
Useful for mongo collections that include ObjectId() objects
Taken from https://speakerdeck.com/mitsuhiko/flask-for-fun-and-profit
'''


class ApiResult(object):

    def __init__(self, value, status=200):
        self.value = value
        self.status = status

    def to_response(self):
        return Response(dumps(self.value),
                        status=self.status,
                        mimetype='application/json')


class ApiError(object):

    def __init__(self, message, status=400):
        self.message = message
        self.status = status

    def to_response(self):
        return ApiResult({'message': self.message},
                         status=self.status).to_response()


def invalid_usage(message, status_code=400):
    response = jsonify({'message': message})
    response.status_code = status_code
    return response


def make_and_text_query(message):
    return '"' + '" "'.join(message.split()) + '"'

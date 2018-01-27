from functools import update_wrapper
from bson.json_util import dumps
from flask import Response, request
from voluptuous import Invalid


class ApiResult(object):
    '''
    Class ApiResult creates Response object for BSON/JSON
    Useful for mongo collections that include ObjectId() objects
    Taken from https://speakerdeck.com/mitsuhiko/flask-for-fun-and-profit
    '''

    def __init__(self, value, status=200):
        self.value = value
        self.status = status

    def to_response(self):
        return Response(dumps(self.value),
                        status=self.status,
                        mimetype='application/json')


class ApiException(Exception):

    def __init__(self, message, status=400):
        self.message = message
        self.status = status
        super().__init__()

    def to_response(self):
        return ApiResult({'message': self.message},
                         status=self.status).to_response()


def make_and_text_query(message):
    '''Compose logical 'and' query from user message string for search'''
    return '"' + '" "'.join(message.split()) + '"'


def parameter_schema(schema):
    def decorator(f):
        def new_func(*args, **kwargs):
            try:
                parameters = request.args.copy()
                request.args = schema(parameters)
            except Invalid as e:
                raise ApiException('Invalid parameter: %s %s' %
                                   (e.msg, e.path))
            return f(*args, **kwargs)
        return update_wrapper(new_func, f)
    return decorator

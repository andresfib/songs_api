from functools import update_wrapper
from bson.json_util import dumps
from flask import Response, request, Flask
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

    def to_result(self):
        return ApiResult({'message': self.message},
                         status=self.status)


class FlaskApi(Flask):
    '''
    We overload the make_response method to automatically get response from
    ApiResult objects
    '''
    def make_response(self, rv):
        if isinstance(rv, ApiResult):
            return rv.to_response()
        return Flask.make_response(self, rv)


def make_and_text_query(message):
    '''Compose logical 'and' query from user message string for search'''
    return '"' + '" "'.join(message.split()) + '"'


def parameter_schema(schema):
    def decorator(f):
        def new_func(*args, **kwargs):
            try:
                parameters = request.args.copy()
                # We assume parameters only have one value
                parameters = schema(parameters).to_dict()
            except Invalid as e:
                raise ApiException('Invalid parameter: %s %s' %
                                   (e.msg, e.path))
            return f(*args, **kwargs, **parameters)
        return update_wrapper(new_func, f)
    return decorator

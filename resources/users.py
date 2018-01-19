import json
from flask import Blueprint, abort, jsonify, make_response
from flask_restful import (
    Resource, Api, reqparse, inputs, fields, marshal, marshal_with, url_for
)

import models

user_fields = {
    'username': fields.String
}

def user_or_404(username):
    """Check to see if the usrname exists or to abort.
    """
    try:
        user = models.User.get(models.User.username == username)
    except models.User.DoesNotExist:
        abort(404)
    else:
        return user


class UserList(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'username',
            required = True,
            help = 'No course username provided',
            location = ['form', 'json']
        )
        self.reqparse.add_argument(
            'email',
            required = True,
            help = 'No valid email provided',
            location = ['form', 'json'],
        )
        self.reqparse.add_argument(
            'password',
            required = True,
            help = 'No password provided',
            location = ['form', 'json'],
        )
        self.reqparse.add_argument(
            'verify_password',
            required = True,
            help = 'No verification password provided',
            location = ['form', 'json'],
        )
        super().__init__()

    def post(self):
        args = self.reqparse.parse_args()
        if args['password'] == args['verify_password']:
            user = models.User.create_user(**args)
            return marshal(user, user_fields), 201
        return make_response(
            json.dumps(
                {'error': 'Password and verification password do not match.'}
            ), 400
        )

    # @marshal_with(user_fields)
    # def get(self, username = None):
    #     if username:
    #         return user_or_404(username)
    #     else:
    #         users = [
    #         marshal(add_reviews(user), user_fields)
    #             for user in models.User.select()
    #         ]
    #         return {'users': users}


users_api = Blueprint('resources.users', __name__)
api = Api(users_api)
api.add_resource(
    UserList,
    '/users',
    endpoint = 'users'
)

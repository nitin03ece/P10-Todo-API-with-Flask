from flask import Blueprint, make_response
from flask_restful import Resource, reqparse, fields , Api, marshal_with, marshal
# from peewee import IntegrityError

from auth import auth

import json
import models


user_fields = {
    'username': fields.String,
    'email' : fields.String
}

class UserList(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'username',
            required = True,
            help = "No username Provided",
            location = ['form', 'json']
        )
        self.reqparse.add_argument(
            'email',
            required = True,
            help = "No Email provided",
            location = ['form', 'json']
        )
        self.reqparse.add_argument(
            'password',
            required = True,
            help = "No Password provided",
            location = ['form', 'json']
        )
        self.reqparse.add_argument(
            'verify_password',
            required = True,
            help = "No Password verification provided",
            location = ['form', 'json']
        )
        super().__init__()

    @marshal_with(user_fields)
    @auth.login_required
    def post(self):
        args = self.reqparse.parse_args()
        if args['password'] == args['verify_password']:
            user = models.User.create_user(**args)
            return (
                user,
                201
            )
        else:
            return make_response(
                json.dumps(
                    {"error" : "Password and verify password does not match!"}
                ),
                400
            )

    # @auth.login_required
    def get(self):
        users = [ marshal(user, user_fields) for user in models.User.select() ]
        return {'users': users}, 200


# class User(Resource):
#     def __init__(self):
#         self.reqparse = reqparse.RequestParser()
#         self.reqparse.add_argument(
#             'username',
#             required = True,
#             help = "No username Provided",
#             location = ['form', 'json']
#         )
#         self.reqparse.add_argument(
#             'email',
#             required = True,
#             help = "No Email provided",
#             location = ['form', 'json']
#         )
#         super().__init__()
#
#     @marshal_with(user_fields)
#     def get(self, username):
#         user = models.User.get(models.User.username==username)
#         return user, 203
#
#     @marshal_with(user_fields)
#     @auth.login_required
#     def delete(self, username):
#         user = models.User.delete().where(models.User.username==username)
#         user.execute()
#         return ("", 204)


users_api = Blueprint('resources/user', __name__)
api = Api(users_api)
api.add_resource(
    UserList,
    '/users',
    endpoint = 'users'
)
# api.add_resource(
#     User,
#     '/users/<username>',
#     endpoint='user'
# )

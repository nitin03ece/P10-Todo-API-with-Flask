from flask_restful import Resource, Api, reqparse, marshal, fields, marshal_with
from flask import Blueprint, g, make_response

from auth import auth

import models
import json


task_fields = {
    'id': fields.Integer,
    'name' : fields.String,
    'user' : fields.String
}

class TaskList(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'name',
            required = True,
            help = 'Name of the task',
            location=['form', 'json']
        )
        super().__init__()

    def get(self):
        tasks = [ marshal(task, task_fields) for task in models.Todo.select()]
        return (
            {'tasks':tasks},
            200
        )

    @marshal_with(task_fields)
    @auth.login_required
    def post(self):
        args = self.reqparse.parse_args()
        user = g.user
        task = models.Todo.create(user=user, **args)
        return task, 201


class Task(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'name',
            required = True,
            help = 'Name of the task',
            location = ['form', 'json']
        )
        super().__init__()


    @marshal_with(task_fields)
    @auth.login_required
    def get(self, id):
        task = models.Todo.get(models.Todo.id == id)
        return (task, 200)


    @marshal_with(task_fields)
    @auth.login_required
    def put(self, id):
        try:
            args = self.reqparse.parse_args()
            task = models.Todo.select().where(
                (models.Todo.user == g.user) |
                (models.Todo.id == id)
            ).get()
        except models.Todo.DoesNotExist:
            raise ValueError("Task does not exist!")
        query = task.update(**args)
        query.execute()
        return (
            task,
            201
        )


    @auth.login_required
    def delete(self, id):
        query = models.Todo.get(models.Todo.id==id)
        if query.user == g.user:
            task = models.Todo.delete().where(models.Todo.id == id)
            task.execute()
            return (
                '',
                202
            )
        else:
            return make_response(json.dumps(
                {"error" : "{} not allowed to delete record of {}".format(g.user.username, query.user)}
            ), 401)


tasks_api = Blueprint('resources/todo', __name__)
api = Api(tasks_api)


api.add_resource(
    TaskList,
    '/todos',
    endpoint='todos'
)
api.add_resource(
    Task,
    '/todos/<int:id>',
    endpoint='todo'
)

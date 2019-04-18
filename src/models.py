import datetime

from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer,
                          BadSignature, SignatureExpired)
from peewee import *
from argon2 import PasswordHasher

import config

HASHER = PasswordHasher()

DATABASE = SqliteDatabase('todo.db')

class User(Model):
    username = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField()

    class Meta:
        database = DATABASE

    @classmethod
    def create_user(cls, username, email, password, **kwargs):
        email = email.lower()
        try:
            cls.select().where(
                cls.email==email |
                cls.username==username
            ).get()
        except cls.DoesNotExist:
            user = cls(username=username, email=email)
            user.password = user.set_password(password)
            user.save()
            return user
        else:
            Exception("username or email already exists please try something else!")

    @staticmethod
    def verify_token(token):
        serialize = Serializer(config.SECRET_KEY)
        try:
            data = serialize.loads(token)
        except (BadSignature, SignatureExpired):
            return None
        else:
            user = User.get(User.id == data['id'])
            return user

    @staticmethod
    def set_password(password):
        return HASHER.hash(password)

    def verify_password(self, password):
        return HASHER.verify(self.password, password)

    def generate_token(self):
        serialize = Serializer(config.SECRET_KEY, expires_in=3600)
        return serialize.dumps({'id':self.id})

    def __str__(self):
        return self.username


class Todo(Model):
    name = CharField(unique=True)
    user = ForeignKeyField(User, backref='users')

    class Meta:
        database = DATABASE

    def __str__(self):
        return self.name


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, Todo], safe=True)
    DATABASE.close()

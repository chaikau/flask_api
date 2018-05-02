#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import bcrypt
from flask import request, g
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired, BadSignature
from sqlalchemy.sql import and_, or_, func
from .errors import ApiRuntimeError
from .meta import data_db
from functools import wraps
import config

serializer = Serializer(config.SECRET_KEY, expires_in=config.TOKEN_EXPIRATION)


class User(object):
    """
    CREATE TABLE users
    (
    id INTEGER PRIMARY KEY NOT NULL,
    username varchar(127) UNIQUE,
    password varchar(127),
    description text
    );
    """

    def __init__(self, username=None, id=None):
        self.username = username
        self.id = id
        self.is_anymous = True
        self.session = getattr(g, "user_session", None)

    @classmethod
    def get_by_username(cls, username):
        sql = "SELECT username, id FROM users WHERE username=:username LIMIT 1"
        params = {"username": username}
        query = g.user_session.execute(sql, params)
        user = query.fetchone()
        if user is None:
            raise ApiRuntimeError(400, "user not exists")
        u = User()
        u.id = user.id
        u.username = user.username
        u.is_anymous = False
        return u

    @classmethod
    def get_by_id(cls, uid):
        sql = "SELECT username, id FROM users WHERE id=:uid LIMIT 1"
        params = {"uid": uid}
        query = g.user_session.execute(sql, params)
        user = query.fetchone()
        if user is None:
            raise ApiRuntimeError(404, "user not exists")
        u = User()
        u.id = user.id
        u.username = user.username
        u.is_anymous = False
        return u

    def save(self):
        if not self.is_anymous:
            self.update()
        else:
            sql = "INSERT INTO users (username) VALUES (:username)"
            params = {"username": self.username}
            self.session.execute(sql, params)
            self.session.commit()
            self.is_anymous = False
        return self

    def set_password(self, password):
        password_hash = self.hash_password(password)
        sql = "UPDATE users SET password=:password WHERE id=:uid"
        params = {"uid": self.id, "password": password_hash}
        self.session.execute(sql, params)
        self.session.commit()

    @staticmethod
    def hash_password(password):
        password = password.encode('utf-8')
        return bcrypt.hashpw(password, bcrypt.gensalt(12))

    def validate_password(self, password):
        password = password.encode('utf-8')
        sql = "SELECT * from users WHERE id=:id LIMIT 1"
        params = {"id": self.id}
        query = self.session.execute(sql, params)
        user = query.fetchone()
        password_hash = user.password
        if bcrypt.hashpw(password, password_hash) != password_hash:
            raise ApiRuntimeError(401, "incorrect password")
        return True

    def delete(self):
        pass

    def token(self):
        return serializer.dumps({'id': self.id, 'username': self.username})

    @staticmethod
    def validate_token(token):
        try:
            data = serializer.loads(token.encode('utf-8'))
        except SignatureExpired:
            raise ApiRuntimeError(401, "token expired")
        except BadSignature:
            raise ApiRuntimeError(401, "token invalid")
        return data

    def update(self):
        sql = "UPDATE users SET description=:description WHERE id=:uid"
        self.session.execute(sql, {"uid": self.id, "description": "description"})
        self.session.commit()


class Detail(object):
    """
    CREATE TABLE details
    (
    id INTEGER PRIMARY KEY NOT NULL,
    id_no varchar(64) UNIQUE,
    name varchar(64),
    description text
    );
    INSERT INTO details (id_no, name, description) VALUES (1, 'test', 'test get resource');
    """

    @classmethod
    def list(self, args):
        size = int(args["size"])
        page = int(args["page"]) - 1
        Resource = data_db.classes.details
        conditions = or_(*[Resource.name == args["name"], Resource.id_no == args["id_no"]])
        query = g.user_session.query(Resource).filter(conditions)
        count = query.count()
        content = [dict(data.__dict__) for data in query.limit(size).offset(size * (page - 1))]
        for item in content:
            item.pop("_sa_instance_state", None)
        return content, count

    @classmethod
    def get_one(self, id_no):
        sql = "SELECT * FROM `details` WHERE id_no=:id_no"
        query = g.user_session.execute(sql, {"id_no": id_no})
        data = query.fetchone()
        return dict(data)


def token_required(location="json", key="token"):
    """
    token auth helper
    :param key: key to get token
    :param location: token location, valid: json, headers, form, args
    :return:
    """

    def validate_token(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            req_args = getattr(request, location)
            token = req_args.get(key)
            assert bool(token), "token is required"
            user_info = User.validate_token(token)
            g.u = User.get_by_id(user_info["id"])
            return f(*args, **kwargs)

        return wrapper

    return validate_token

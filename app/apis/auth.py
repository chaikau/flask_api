#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    @version:  python 3.6
    @FileName: auth.py
    @Author:   chaikau
    @Time：    2018-03-24 19:39
    @Description: auth api with flask simple style
"""
from lib.Logging import Logging
from flask import request, Blueprint
from app.models import User
from ..utils import json_wrapper

logger = Logging('log/auth.log', "auth").get_logging()

auth = Blueprint('auth', __name__)


@auth.route('/token', methods=['POST'])
@json_wrapper
def login():
    args = request.json

    user_name = args.get("user_name")
    password = args.get("password")

    assert user_name, "must user_name"
    assert password, "must password"
    assert len(user_name) <= 32, "user_name len too long"
    assert len(password) <= 64, "password len too long"

    user = User.get_by_username(user_name)

    if user.validate_password(password):
        token = user.token()
        ret = {"status": "success", "token": str(token, encoding="utf8")}
    else:
        ret = {"status": "failure"}

    return ret


@auth.route('/users/<uid>', methods=['PATCH'])
@json_wrapper
def users(uid):
    """Reset password"""
    args = request.json

    old_password = args.get("old_password")
    password = args.get("password")
    password2 = args.get("password2")

    assert bool(old_password), "must old_password"
    assert bool(password), "must new password"
    assert bool(password2), "must repeating new password"
    assert password == password2, "the repeated new password is not the same as new password"

    user = User.get_by_id(int(uid))
    assert user.validate_password(old_password), "old password is incorrect"
    user.set_password(password)
    return {"result": "success"}

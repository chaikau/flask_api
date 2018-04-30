#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    @version:  python 3.6
    @FileName: models.py
    @Author:   chaikau
    @Time：    2018-03-24 19:39
    @Description: flask helper
"""

from flask import request, jsonify, g, Response
from .meta import user_db, data_db
from functools import wraps
from lib.Logging import Logging

logger = Logging('log/exeception.log', "exeception").get_logging()
request_logger = Logging('log/request.log', "request").get_logging()


def log_request():
    values = request.values
    json = request.json
    ip = request.remote_addr
    method = request.method
    path = request.path
    request_logger.info("{ip} {method}: {path}, {values}, {json}".format(
        ip=ip, method=method, path=path, values=values, json=json))


def make_db_session():
    g.user_session = user_db.make_session()
    g.data_session = data_db.make_session()


def teardown_db_session(e):
    if e:
        g.user_session.rollback()
        g.data_session.rollback()
    g.user_session.close()
    g.data_session.close()


def handle_assertion_error(err):
    ret = {
        "message": str(err),
        "status": 400,
    }
    return jsonify(ret)


def handle_api_error(err):
    result = {
        "message": str(err.message),
        "status": err.code,
    }
    return jsonify(result)


def handle_error(err):
    logger.exception(request.path)
    result = {
        "message": getattr(err, "message", None) or str(err),
        "status": getattr(err, "code", None) or 500,
    }
    return jsonify(result)


def json_wrapper(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        result = f(*args, **kwargs)
        if isinstance(result, (dict, list)):
            return jsonify({
                "status": 200,
                "data": result
            })
        return result
    return wrapper


def json_util(result):
    if isinstance(result, (dict, list)):
        return jsonify({
            "status": 200,
            "data": result
        })
    return result

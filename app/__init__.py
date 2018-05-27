#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, redirect, url_for
from .utils import make_db_session, log_request, teardown_db_session
from werkzeug.utils import import_string


def init_app(app):
    extensions = {
        "app.meta.user_db": {"config_prefix": 'USER'},
        "app.meta.data_db": {"config_prefix": 'DATA'},
    }
    blueprints = {
        "app.apis.auth.auth": {"url_prefix": "/api/v1/auth"},
        "app.apis.resources.resources": {"url_prefix": "/api/v1/resources"},
        "app.apis.resources_v2.resources": {"url_prefix": "/api/v2"},
    }
    errorhandlers = {
        "app.utils.handle_assertion_error": AssertionError,
        "app.utils.handle_api_error": "app.errors.ApiRuntimeError",
        "app.utils.handle_error": Exception,
    }

    for ext_name, kwargs in extensions.items():
        ext = import_string(ext_name)
        ext.init_app(app, **kwargs)

    for bp_name, kwargs in blueprints.items():
        bp = import_string(bp_name)

        bp.before_request(make_db_session)
        bp.before_request(log_request)
        # bp.after_request(json_envelope)
        bp.teardown_request(teardown_db_session)

        app.register_blueprint(bp, **kwargs)

    for handle, error in errorhandlers.items():
        if isinstance(error, str):
            error = import_string(error)
        handle = import_string(handle)
        app.errorhandler(error)(handle)

        # app.after_request(json_envelope)


def favicon(app):
    @app.route("/favicon.ico", methods=["GET"])
    def get_favicon():
        return redirect(url_for("static", filename="favicon.ico"))


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    init_app(app)
    favicon(app)
    return app

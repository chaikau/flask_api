#!/usr/bin/env python3
# encoding: utf-8
"""
    @version:  python 3.6
    @FileName: flask_mysql.py
    @Author:   Piwenwu
    @Description: flask mysql extension, support multi database connections by config_prefix
"""

from flask import current_app
from sqlalchemy import create_engine, exc, event, select
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker

__all__ = ('FlaskMySQL',)
__version__ = '0.1.1'


class FlaskMySQL(object):
    def __init__(self, app=None, config={}, config_prefix='MYSQL'):
        self.config = config
        self.make_session = None
        self.connect_name = self.config_prefix = config_prefix
        self.class_bucket = "%s_CLASS" % config_prefix
        if app is not None:
            self.init_app(app, config, config_prefix)

    def init_app(self, app, config={}, config_prefix=None):
        if config_prefix:
            self.connect_name = self.config_prefix = config_prefix
            self.class_bucket = "%s_CLASS" % config_prefix
        self.config.update(app.config)
        self.config.update(config)
        uri = self.config[self.key('SQLALCHEMY_DATABASE_URI')]
        # engine = create_engine(uri, pool_recycle=14400, pool_size=100)
        engine = create_engine(uri, pool_recycle=14400)
        self.make_session = sessionmaker(engine)

        # fix broken pipe exception
        @event.listens_for(engine, "engine_connect")
        def ping_connection(connection, branch):
            if branch:
                return
            save_should_close_with_result = connection.should_close_with_result
            connection.should_close_with_result = False
            try:
                connection.scalar(select([1]))
            except exc.DBAPIError as err:
                if err.connection_invalidated:
                    connection.scalar(select([1]))
                else:
                    raise
            finally:
                connection.should_close_with_result = save_should_close_with_result

        base = automap_base()
        base.prepare(engine, reflect=True)

        ext = app.extensions.setdefault('mysql', {})
        ext[self.connect_name] = engine
        ext[self.class_bucket] = base.classes

    def key(self, suffix):
        return '%s_%s' % (self.config_prefix, suffix)

    @property
    def connection(self):
        return current_app.extensions["mysql"][self.connect_name]

    @property
    def classes(self):
        return current_app.extensions["mysql"][self.class_bucket]

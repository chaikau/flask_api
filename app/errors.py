#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class ApiRuntimeError(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message


class ApiRequestError(ApiRuntimeError):
    def __init__(self, message):
        super().__init__(400, message)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    @version:  python 3.6
    @FileName: auth.py
    @Author:   chaikau
    @Time：    2018-03-24 19:39
    @Description: resource api with flask simple style
"""

from lib.Logging import Logging
from flask import Blueprint, request, g
from ..utils import json_wrapper
from ..models import Detail, token_required


logger = Logging('log/resources.log', "resources").get_logging()
resources = Blueprint('resources', __name__)


@resources.route('/resources', methods=['GET'])
@token_required(location="headers", key="token")
@json_wrapper
def info():
    args = request.args
    assert args.get("name") or args.get("id_no"), "must name or id_no"
    assert args.get("size"), "must size"
    assert args.get("page"), "must page"

    user = g.u
    content, count = Detail.list(args)
    logger.info({"user": user.username, "resource_name": "resources", "count": len(content)})
    return {"content": content, "total": count}

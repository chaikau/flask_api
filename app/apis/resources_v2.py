#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    @version:  python 3.6
    @FileName: auth.py
    @Author:   chaikau
    @Time：    2018-03-24 19:39
    @Description: resource api with swagger
"""
from lib.Logging import Logging
from flask import Blueprint, g, request
from flask_restplus import Resource, fields, reqparse, Api
from ..utils import json_wrapper
from ..errors import ApiRuntimeError
from ..models import Detail, token_required
from ..utils import handle_api_error, handle_assertion_error, handle_error


logger = Logging('log/resources_v2.log', "resources_v2").get_logging()
resources = Blueprint('resources_v2', __name__)

api = Api(resources, version='2.0', title='Api With Swagger', description='rest api')

api.errorhandler(AssertionError)(handle_assertion_error)
api.errorhandler(ApiRuntimeError)(handle_api_error)
api.errorhandler(handle_error)
nm = api.namespace('resources', description='get resources')

token_parser = reqparse.RequestParser()
token_parser.add_argument('token', required=True, type=str, help="token", location='headers')

ResourceModel = api.model('ResourceModel', {
    'id_no': fields.Integer(description='the id number of resource', required=True),
    'name': fields.String(description='name', required=True),
    'description': fields.String(description='content', required=False),
})


@nm.route('/<int:id_no>', methods=['GET'])
@nm.doc("get a resource by id")
@nm.param('id_no', 'resource id')
@nm.expect(token_parser)
class ApiResource(Resource):
    @json_wrapper
    @token_required(location="headers", key="token")
    @nm.marshal_with(ResourceModel)
    # @nm.param('id_no', 'resource id')
    def get(self, id_no):
        """(GET)某资源"""
        user = g.u
        data = Detail.get_one(id_no)
        logger.info({"user": user.username, "resource_name": "resources", "id_no": id_no})
        return data


@nm.route('', methods=['POST'])
@nm.doc("get resources by id or name")
@nm.expect(token_parser)
class ApiResources(Resource):
    JsonParam = api.model('JsonParam', {
        'id_no': fields.Integer(description='查询参数', required=False),
        'name': fields.String(description='查询参数', required=True, default="test"),
        'size': fields.Integer(description='大小', required=True, default=10),
        'page': fields.Integer(description='页数', required=True, default=1),
    })

    ResourceList = api.model("ResourceList", {
        "content": fields.Nested(ResourceModel, description='资源', as_list=True),
        "total": fields.Integer(description='总数'),
    })

    @json_wrapper
    @token_required(location="headers", key="token")
    @nm.expect(JsonParam)
    # @nm.marshal_list_with(ApiModel, envelope="content", mask="description")
    @nm.marshal_list_with(ResourceList)
    # @nm.marshal_list_with(ApiModel)
    @nm.doc("get resources by id or name")
    def post(self):
        """(POST)获取资源列表"""
        args = request.json
        user = g.u
        data, count = Detail.list(args)
        args.pop("token", None)
        logger.info({"user": user.username, "resource_name": "resources", "args": args, "count": len(data)})
        return {"content": data, "total": count}

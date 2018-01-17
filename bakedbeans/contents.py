import json
import logging

import jsonschema
from flask import request

from .exceptions import (
    BeanValidationError,
    ContentNotFoundError,
    InvalidContent,
)


log = logging.getLogger(__name__)


class ContentResolver(object):

    BEAN_SCHEMA = {
        "type": "object",
        "properties": {
            "_bean": {"type": "boolean"},
            "responses": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "properties": {
                        "contents": {"type": "object"},
                        "params": {"type": "object"},
                        "status": {"type": "number"}
                    },
                    "required": ["contents"]
                }
            },
        },
        "required": [
            '_bean',
            'responses'
        ]
    }

    RESPONSE_CODES = {
        'get': 200,
        'post': 201,
        'delete': 204,
        'put': 200,
        'patch': 200
    }

    def __init__(self, base, url, method):
        self.base = base
        self.url = url.replace('//', '/')
        self.method = method

    def build_path(self):
        if self.url.endswith('/') or self.url == '':
            self.path = f'{self.url}index.{self.method}.json'
        else:
            self.path = f'{self.url}.{self.method}.json'
        return self.path

    def resolve_path(self):
        self.full_path = self.base / self.path
        if not self.full_path.exists():
            log.warn(f'Cannot locate content for {self.url}, {self.full_path} not found')
            raise ContentNotFoundError()
        return self.full_path

    def is_bean(self, content):
        return isinstance(content, dict) and content.get('_bean') is True

    def load_content(self):
        with self.full_path.open() as f:
            try:
                return json.load(f)
            except ValueError as e:
                log.error(f'Unable to parse {self.full_path}: {e}')
                raise InvalidContent()

    def validate_bean(self, bean):
        try:
            jsonschema.validate(bean, self.BEAN_SCHEMA)
        except jsonschema.ValidationError as e:
            log.error(f"{self.full_path} contains an invalid bean: {e}")
            raise BeanValidationError()

    def matches_params(self, params):
        for param, value in params.items():
            if request.args.get(param) != str(value):
                return False
        return True

    def resolve_bean(self, bean):
        responses = bean['responses']
        response = None
        for r in responses:
            if self.matches_params(r.get('params', {})):
                response = r
                break
        if response is None:
            log.warn(f"No response matched for {self.url}, defaulting to first")
            response = responses[0]
        return (
            response.get('contents', {}),
            response.get('status', self.default_response_code())
        )

    def default_response_code(self):
        return self.RESPONSE_CODES.get(self.method, 200)

    @property
    def response(self):
        self.build_path()
        self.resolve_path()
        content = self.load_content()
        if self.is_bean(content):
            log.info('Content is a bean, resolving')
            self.validate_bean(content)
            return self.resolve_bean(content)
        return content, self.default_response_code()

from flask import Blueprint, current_app, jsonify, request

from .contents import ContentResolver
from .exceptions import (
    BeanValidationError,
    ContentNotFoundError,
    InvalidContent,
)


beans = Blueprint('name', __name__)


@beans.route('/', defaults={'path': ''},
             methods=['GET', 'POST', "DELETE", "PUT", "PATCH"])
@beans.route('/<path:path>', methods=['GET', 'POST', "DELETE", "PUT", "PATCH"])
def catch_all(path: str):
    try:
        body, status = ContentResolver(
            base=current_app.config['BEANS'],
            url=path,
            method=request.method.lower()
        ).response
    except ContentNotFoundError:
        return jsonify({'error': f'content not found {path}'}), 404
    except InvalidContent:
        return jsonify({'error': 'content invalid'}), 500
    except BeanValidationError:
        return jsonify({'error': 'This is one mouldy bean'}), 500
    return jsonify(body), status

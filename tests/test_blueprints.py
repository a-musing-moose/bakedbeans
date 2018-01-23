import json
from unittest.mock import Mock, PropertyMock

import pytest
from flask import Flask

from bakedbeans import blueprints, exceptions


@pytest.fixture()
def app(tmpdir):
    app = Flask(__name__)
    app.config['BEANS'] = tmpdir
    app.register_blueprint(blueprints.beans)
    return app.test_client()


def get_shouty_content_resolver(exception):
    def _inner(*args, **kwargs):
        resolver = Mock()
        type(resolver).response = PropertyMock(side_effect=exception())
        return resolver
    return _inner


def get_mock_content_resolver(body, status_code):
    def _inner(*args, **kwargs):
        resolver = Mock()
        type(resolver).response = PropertyMock(return_value=(body, status_code))
        return resolver
    return _inner


def test_catch_all_returns_not_found_for_missing_content(app, monkeypatch):
    monkeypatch.setattr(
        'bakedbeans.blueprints.ContentResolver',
        get_shouty_content_resolver(exceptions.ContentNotFoundError)
    )
    response = app.get('/')
    assert response.status_code == 404
    data = json.loads(response.get_data())
    assert 'error' in data


def test_catch_all_returns_server_error_for_invalid_content(app, monkeypatch):
    monkeypatch.setattr(
        'bakedbeans.blueprints.ContentResolver',
        get_shouty_content_resolver(exceptions.InvalidContent)
    )
    response = app.get('/')
    assert response.status_code == 500
    data = json.loads(response.get_data())
    assert 'error' in data


def test_catch_all_returns_server_error_for_bean_validation_error(app, monkeypatch):
    monkeypatch.setattr(
        'bakedbeans.blueprints.ContentResolver',
        get_shouty_content_resolver(exceptions.BeanValidationError)
    )
    response = app.get('/')
    assert response.status_code == 500
    data = json.loads(response.get_data())
    assert 'error' in data


def test_catch_all_returns_body_and_status_from_resolver(app, monkeypatch):
    monkeypatch.setattr(
        'bakedbeans.blueprints.ContentResolver',
        get_mock_content_resolver({"yes": True}, 200)
    )
    response = app.get('/')
    assert response.status_code == 200
    data = json.loads(response.get_data())
    assert data.get('yes', False)


@pytest.mark.parametrize("method, status_code", (
    ('get', 200),
    ('post', 201),
    ('delete', 204),
    ('put', 200),
    ('patch', 200)
))
def test_app_catch_all_view_support_all_methods(app, tmpdir, method, status_code):
    content_file = tmpdir / ('index.' + method + '.json')
    with content_file.open('w') as r:
        r.write('{"_bean": true, "responses": [{"contents": {"yes": true}}]}')
    response = getattr(app, method)('/')
    assert response.status_code == status_code

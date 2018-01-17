from pathlib import Path
from unittest.mock import Mock

import pytest

from bakedbeans import contents, exceptions


def test_build_path_resolves_folder_urls_to_index_file():
    resolver = contents.ContentResolver(
        base=Path(),
        url='somewhere/',
        method='get'
    )
    path = resolver.build_path()
    assert str(path).endswith('index.get.json')


@pytest.mark.parametrize(
    'method,filename',
    (
        ('get', 'index.get.json'),
        ('post', 'index.post.json')
    )
)
def test_build_path_resolves_empty_url_to_index_file(method, filename):
    resolver = contents.ContentResolver(
        base=Path(),
        url='',
        method=method
    )
    path = resolver.build_path()
    assert str(path) == filename


def test_build_path_mirrors_url_path():
    resolver = contents.ContentResolver(
        base=Path(),
        url='a/path/to/a/thing',
        method='get'
    )
    path = resolver.build_path()
    assert str(path) == 'a/path/to/a/thing.get.json'


def test_is_bean_returns_true_when_data_passed_is_a_bean():
    data = {
        '_bean': True
    }
    resolver = contents.ContentResolver(
        base=Path(),
        url='',
        method='get'
    )
    assert resolver.is_bean(data)


def test_is_bean_returns_false_when_data_passed_is_marked_as_not_a_bean():
    data = {
        '_bean': False
    }
    resolver = contents.ContentResolver(
        base=Path(),
        url='',
        method='get'
    )
    assert not resolver.is_bean(data)


def test_is_bean_returns_false_when_data_passed_is_not_a_dict():
    data = ''
    resolver = contents.ContentResolver(
        base=Path(),
        url='',
        method='get'
    )
    assert not resolver.is_bean(data)


def test_bean_validation_raises_exception_when_response_is_not_present():
    bean = {
        '_bean': True
    }
    resolver = contents.ContentResolver(
        base=Path(),
        url='',
        method='get'
    )

    resolver.full_path = ''

    with pytest.raises(exceptions.BeanValidationError):
        resolver.validate_bean(bean)


def test_bean_validation_raises_exception_when_content_not_in_responses():
    bean = {
        '_bean': True,
        'responses': [
            {'params': {'key': 'value'}}
        ]
    }
    resolver = contents.ContentResolver(
        base=Path(),
        url='',
        method='get'
    )

    resolver.full_path = ''

    with pytest.raises(exceptions.BeanValidationError):
        resolver.validate_bean(bean)


def test_bean_validation_does_not_raise_exception_on_valid_bean():
    bean = {
        '_bean': True,
        'responses': [
            {'contents': {}}
        ]
    }
    resolver = contents.ContentResolver(
        base=Path(),
        url='',
        method='get'
    )

    resolver.full_path = ''
    try:
        resolver.validate_bean(bean)
    except exceptions.BeanValidationError:
        pytest.fail("Valid bean raised unexcepted validation error")


@pytest.mark.parametrize("method,status_code", (
    ('get', 200),
    ('post', 201),
    ('delete', 204),
    ('put', 200),
    ('patch', 200),
    ('foobar', 200)
))
def test_default_response_code_is_based_on_method(method, status_code):
    resolver = contents.ContentResolver(
        base=Path(),
        url='',
        method=method
    )
    assert resolver.default_response_code() == status_code


PARAM_DATA = (
    ({'key': 'value'}, {'key': 'value'}, True),  # One match
    ({'key': 5}, {'key': '5'}, True),  # Type as all get params are strings
    ({'key': 'value'}, {'key': 'not_value'}, False),  # One mismatch
    ({'key': 'value', 'key2': "value2"}, {'key': 'value', 'key2': "value2"}, True),  # All match
    ({'key': 'value', 'key2': "value2"}, {'key': 'value', 'key2': "not_value_2"}, False),  # one mismatch
    ({'key': 'value'}, {'key': 'value', 'key2': "value2"}, True),  # additional GET args not considered
)


@pytest.mark.parametrize('params,request_args,expected', PARAM_DATA)
def test_match_params_returns_true_when_params_match(params, request_args, expected, monkeypatch):
    monkeypatch.setattr('bakedbeans.contents.request', Mock(args=request_args))
    resolver = contents.ContentResolver(
        base=Path(),
        url='',
        method='get'
    )
    assert resolver.matches_params(params) is expected


def test_loading_invalid_json_file_raises_exception(tmpdir):
    path = tmpdir / 'test.json'
    with path.open('w') as f:
        f.write('{')
    resolver = contents.ContentResolver(
        base=tmpdir,
        url='',
        method='get'
    )
    resolver.full_path = path
    with pytest.raises(exceptions.InvalidContent):
        resolver.load_content()


def test_loading_valid_json_file_returns_content(tmpdir):
    path = tmpdir / 'test.json'
    with path.open('w') as f:
        f.write('{"key": "value"}')
    resolver = contents.ContentResolver(
        base=tmpdir,
        url='',
        method='get'
    )
    resolver.full_path = path
    content = resolver.load_content()
    assert content == {'key': 'value'}


def test_resolve_path_raises_exception_if_file_not_found():
    resolver = contents.ContentResolver(
        base=Path(),
        url='',
        method='get'
    )
    resolver.path = 'nope.get.json'
    with pytest.raises(exceptions.ContentNotFoundError):
        resolver.resolve_path()


def test_resolve_path_returns_full_path_when_file_exists(tmpdir):
    path = tmpdir / 'index.get.json'
    with path.open('w') as f:
        f.write('{"key": "value"}')
    resolver = contents.ContentResolver(
        base=tmpdir,
        url='',
        method='get'
    )
    resolver.path = 'index.get.json'
    full_path = resolver.resolve_path()
    assert full_path.exists()


def test_resolve_bean_will_return_first_response_if_no_matches_found(monkeypatch):
    monkeypatch.setattr('bakedbeans.contents.request', Mock(args={'key': 'value3'}))
    bean = {
        '_bean': True,
        'responses': [
            {
                'params': {
                    'key': 'value'
                },
                'contents': {
                    'response': 1
                }
            },
            {
                'params': {
                    'key': 'value2'
                },
                'contents': {
                    'response': 2
                }
            }
        ]
    }
    resolver = contents.ContentResolver(
        base=Path,
        url='',
        method='get'
    )
    response, status_code = resolver.resolve_bean(bean)
    assert status_code == 200
    assert response['response'] == 1


def test_resolve_bean_will_return_first_matching_response(monkeypatch):
    monkeypatch.setattr('bakedbeans.contents.request', Mock(args={'key': 'value2'}))
    bean = {
        '_bean': True,
        'responses': [
            {
                'params': {
                    'key': 'value'
                },
                'contents': {
                    'response': 1
                }
            },
            {
                'params': {
                    'key': 'value2'
                },
                'contents': {
                    'response': 2
                }
            }
        ]
    }
    resolver = contents.ContentResolver(
        base=Path(),
        url='',
        method='get'
    )
    response, status_code = resolver.resolve_bean(bean)
    assert status_code == 200
    assert response['response'] == 2


def test_response_property_loads_and_returns_basic_contents(tmpdir):
    content_file = tmpdir / 'index.get.json'
    with content_file.open('w') as r:
        r.write('{"yes": true}')
    resolver = contents.ContentResolver(
        base=tmpdir,
        url='',
        method='get'
    )
    response, status_code = resolver.response
    assert status_code == 200
    assert response == {
        'yes': True
    }


def test_response_property_loads_and_returns_bean_contents(tmpdir):
    content_file = tmpdir / 'index.get.json'
    with content_file.open('w') as r:
        r.write('{"_bean": true, "responses": [{"contents": {"yes": true}}]}')
    resolver = contents.ContentResolver(
        base=tmpdir,
        url='',
        method='get'
    )
    response, status_code = resolver.response
    assert status_code == 200
    assert response == {
        'yes': True
    }

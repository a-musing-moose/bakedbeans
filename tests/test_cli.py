from unittest.mock import Mock

from click.testing import CliRunner

from bakedbeans.cli import main


def test_contents_path_must_exist():
    runner = CliRunner()
    result = runner.invoke(main, ['/does/not/exist/'])
    assert result.exit_code != 0
    assert 'Invalid value' in result.output


def test_manual_option_values_are_passed_to_flask(monkeypatch):
    mock_app = Mock(config={}, run=Mock(), register_blueprint=Mock)
    monkeypatch.setattr(
        'bakedbeans.cli.Flask',
        lambda n: mock_app
    )
    runner = CliRunner()
    result = runner.invoke(main, ['--debug', '--host=0.0.0.0', '--port=8888', '.'])
    assert result.exit_code == 0
    mock_app.run.assert_called_with(host='0.0.0.0', port=8888, debug=True)


def test_default_option_values_are_passed_to_flask(monkeypatch):
    mock_app = Mock(config={}, run=Mock(), register_blueprint=Mock)
    monkeypatch.setattr(
        'bakedbeans.cli.Flask',
        lambda n: mock_app
    )
    runner = CliRunner()
    result = runner.invoke(main, ['.'])
    assert result.exit_code == 0
    mock_app.run.assert_called_with(host='127.0.0.1', port=3000, debug=False)

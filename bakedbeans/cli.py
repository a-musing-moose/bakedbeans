from pathlib import Path

import click
from flask import Flask

from .blueprints import beans


@click.command()
@click.option('--host', default='127.0.0.1', help='default: 127.0.0.1')
@click.option('--port', default=3000, help='default: 3000')
@click.option('--debug', default=False, is_flag=True, help='Enables debug mode')
@click.argument('contents', type=click.Path(exists=True))
def main(host, port, debug, contents):
    app = Flask(__name__)
    app.config['BEANS'] = Path(contents).absolute()
    app.register_blueprint(beans)
    app.run(host=host, port=port, debug=debug)

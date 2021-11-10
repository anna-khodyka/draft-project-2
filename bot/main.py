# pylint: disable=E0402
"""
Here Flask app is started
"""

import threading
import os
import sys
from flask import Flask
from sqlalchemy import *


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

if __package__ == "" or __package__ is None:
    import login_bp
    import contact_bp
    import note_bp
    import init_bp
    import file_bp
    import news_bp
    from neural_code import predict_class
    from fill_db import insert_users
    import db_postgres
else:
    from . import login_bp
    from . import contact_bp
    from . import note_bp
    from . import init_bp
    from . import file_bp
    from . import news_bp
    from . db_postgres import *
    from .neural_code import predict_class
    from .fill_db import insert_users
    from . SQL_alchemy_classes import *

def init_app(config=None):
    """
    Preparing and launch Flask app, warming up neural network.
    :param config: config list
    :return: app Flask.app instance
    """
    SECRET_KEY = bytes(os.environ.get("SECRET_KEY", "gadklnl/dad/;jdisa;l990q3"), 'utf-8')
    is_empty =database_is_empty(engine)
    if is_empty:
        try:
            create_tables(engine)
            insert_users(pgsession)
        except Exception as error:
            return str(error)
    app = Flask(__name__, instance_relative_config=True)
    if not config:
        predict_warmup = threading.Thread(target=predict_class, args=("warm up",))
        predict_warmup.start()
        app.before_request_funcs[None] = [init_bp.before_request]
        app.config.from_mapping(
            DEBUG=False,
            SECRET_KEY=SECRET_KEY,
        )
    else:
        app.config.from_mapping(config)
    app.register_blueprint(login_bp.login_bp)
    app.register_blueprint(contact_bp.contact_bp)
    app.register_blueprint(note_bp.note_bp)
    app.register_blueprint(init_bp.init_bp)
    app.register_blueprint(file_bp.file_bp)
    app.register_blueprint(news_bp.news_bp)
    app.add_url_rule("/", endpoint="index")


    return app

import os
from flask import Flask
from models import db
from views import main_bp
from commands import init_db_cmd


def create_app():
    app = Flask(__name__)

    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'change-this-before-deployment'),
        SQLALCHEMY_DATABASE_URI='sqlite:///expense_tracker.db',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    db.init_app(app)
    app.register_blueprint(main_bp)
    app.cli.add_command(init_db_cmd)

    return app

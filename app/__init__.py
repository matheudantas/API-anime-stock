from flask import Flask
from .views import bp_animes


def create_app():
    app = Flask(__name__)

    app.register_blueprint(bp_animes)

    return app

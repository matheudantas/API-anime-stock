
from flask.json import jsonify
from app.services import Animes
from flask import Blueprint, request
from psycopg2.errors import UniqueViolation, UndefinedTable
from http import HTTPStatus
from flask_cors import CORS

bp_animes = Blueprint('animes', __name__, url_prefix='/api')
CORS(bp_animes)


@bp_animes.route('/animes', methods=['POST', 'GET'])
def get_create():
    animes = Animes()

    if request.method == 'POST':
        data = request.get_json()
        try:
            return animes.insert_anime(data), HTTPStatus.CREATED

        except KeyError as e:
            return e.args[0], HTTPStatus.UNPROCESSABLE_ENTITY

        except UniqueViolation:
            return {'data': 'anime is already exists'}, HTTPStatus.UNPROCESSABLE_ENTITY

        except UndefinedTable:
            animes.create_table()

    try:
        return jsonify(animes.select_animes()), HTTPStatus.OK

    except UndefinedTable:
        return {"data": []}, HTTPStatus.OK

    except Exception as ex:
        return ex.args[0], HTTPStatus.NOT_FOUND


@bp_animes.route('/animes/<int:anime_id>')
def filter(anime_id):
    animes = Animes()

    try:
        return animes.select_by_id(anime_id), HTTPStatus.OK

    except Exception as e:
        return e.args[0], HTTPStatus.NOT_FOUND


@bp_animes.route('/animes/<int:anime_id>', methods=['PATCH'])
def update(anime_id):
    animes = Animes()
    data = request.get_json()

    try:
        return animes.update_by_id(data, anime_id)

    except KeyError as e:
        return e.args[0], HTTPStatus.UNPROCESSABLE_ENTITY

    except Exception as e:
        return e.args[0], HTTPStatus.NOT_FOUND


@bp_animes.route('/animes/<int:anime_id>', methods=['DELETE'])
def delete(anime_id):
    animes = Animes()

    try:
        return animes.delete_by_id(anime_id), 204

    except Exception as e:
        return e.args[0], 404

from flask_restful import reqparse, abort, Api, Resource
from flask import jsonify
from . import db_session
from .cinemas import Cinema
from .cinemas_parser import parser


def abort_if_job_not_found(cinema_id):
    session = db_session.create_session()
    cinema = session.query(Cinema).get(cinema_id)
    if not cinema:
        abort(404, message=f"Cinema {cinema_id} not found")


class CinemasResource(Resource):
    def get(self, cinema_id):
        abort_if_job_not_found(cinema_id)
        db_ses = db_session.create_session()
        cinema = db_ses.query(Cinema).get(cinema_id)
        return jsonify(
            {
                'cinema': cinema.to_dict(only=(
                    'id', 'title'))
            }
        )

    def delete(self, cinema_id):
        abort_if_job_not_found(cinema_id)
        db_sess = db_session.create_session()
        cinema = db_sess.query(Cinema).get(cinema_id)
        db_sess.delete(cinema)
        db_sess.commit()
        return jsonify({'success': 'OK'})


class CinemasListResource(Resource):
    def get(self):
        db_sess = db_session.create_session()
        cinemas = db_sess.query(Cinema).all()
        return jsonify(
            {
                'cinemas':
                    [item.to_dict(only=(
                        'id', 'title'))
                        for item in cinemas]
            }
        )

    def post(self):
        db_sess = db_session.create_session()
        args = parser.parse_args()
        cinema = Cinema(title=args['title'])
        db_sess.add(cinema)
        db_sess.commit()
        return jsonify({'success': 'OK'})
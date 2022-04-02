from flask_restful import reqparse, abort, Api, Resource
from flask import jsonify
from . import db_session
from .halls import Hall
from .cinemas import Cinema
from .halls_parser import parser


def abort_if_job_not_found(hall_id):
    session = db_session.create_session()
    hall = session.query(Hall).get(hall_id)
    if not hall:
        abort(404, message=f"Hall {hall_id} not found")


class HallsResource(Resource):
    def get(self, hall_id):
        abort_if_job_not_found(hall_id)
        db_ses = db_session.create_session()
        hall = db_ses.query(Hall).get(hall_id)
        return jsonify(
            {
                'hall': hall.to_dict(only=(
                    'id', 'width', 'height', 'cinema_id', 'number'))
            }
        )

    def delete(self, hall_id):
        abort_if_job_not_found(hall_id)
        db_sess = db_session.create_session()
        hall = db_sess.query(Hall).get(hall_id)
        db_sess.delete(hall)
        db_sess.commit()
        return jsonify({'success': 'OK'})


class HallsListResource(Resource):
    def get(self):
        db_sess = db_session.create_session()
        halls = db_sess.query(Hall).all()
        return jsonify(
            {
                'halls':
                    [item.to_dict(only=(
                        'id', 'width', 'height', 'cinema_id', 'number'))
                        for item in halls]
            }
        )

    def post(self):
        db_sess = db_session.create_session()
        args = parser.parse_args()
        if not db_sess.query(Cinema).filter(Cinema.id == args['cinema_id']).first():
            return jsonify({'error': 'Cinema ID not found'})
        elif args['height'] <= 0 or args['width'] <= 0:
            return jsonify({'error': 'Height and width less than zero'})
        hall = Hall(width=args['width'], height=args['height'], cinema_id=args['cinema_id'],
                    number=args['number'])
        db_sess.add(hall)
        db_sess.commit()
        return jsonify({'success': 'OK'})

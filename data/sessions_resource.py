from flask_restful import reqparse, abort, Api, Resource
from flask import jsonify
from . import db_session
from .sessions import Session
from .cinemas import Cinema
from .halls import Hall
from .sessions_parser import parser, parser_put


def abort_if_job_not_found(session_id):
    session = db_session.create_session()
    session = session.query(Session).get(session_id)
    if not session:
        abort(404, message=f"Session {session_id} not found")


class SessionsResource(Resource):
    def get(self, session_id):
        abort_if_job_not_found(session_id)
        db_ses = db_session.create_session()
        session = db_ses.query(Session).get(session_id)
        return jsonify(
            {
                'session': session.to_dict(only=(
                    'id', 'title', 'cinema_id', 'hall_id', 'data', 'seats'))
            }
        )

    def delete(self, session_id):
        abort_if_job_not_found(session_id)
        db_sess = db_session.create_session()
        session = db_sess.query(Session).get(session_id)
        db_sess.delete(session)
        db_sess.commit()
        return jsonify({'success': 'OK'})

    def put(self, session_id):
        abort_if_job_not_found(session_id)
        args = parser_put.parse_args()
        db_sess = db_session.create_session()
        session = db_sess.query(Session).get(session_id)
        session.seats = args['seats']
        db_sess.commit()
        return jsonify({'success': 'OK'})


class SessionsListResource(Resource):
    def get(self):
        db_sess = db_session.create_session()
        sessions = db_sess.query(Session).all()
        return jsonify(
            {
                'sessions':
                    [item.to_dict(only=(
                        'id', 'title', 'cinema_id', 'hall_id', 'data', 'seats'))
                        for item in sessions]
            }
        )

    def post(self):
        db_sess = db_session.create_session()
        args = parser.parse_args()
        if not db_sess.query(Cinema).filter(Cinema.id == args['cinema_id']).first():
            return jsonify({'error': 'Cinema Id not found'})
        elif not db_sess.query(Hall).filter(Hall.id == args['hall_id']).first():
            return jsonify({'error': 'Hall Id not found'})
        session = Session(title=args['title'], cinema_id=args['cinema_id'],
                          hall_id=args['hall_id'], data=args['data'], seats=args['seats'])
        db_sess.add(session)
        db_sess.commit()
        return jsonify({'success': 'OK'})

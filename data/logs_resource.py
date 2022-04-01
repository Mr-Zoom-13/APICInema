from flask_restful import reqparse, abort, Api, Resource
from flask import jsonify
from . import db_session
from .logs import Log
from .users import User
from .logs_parser import parser


def abort_if_job_not_found(log_id):
    session = db_session.create_session()
    log = session.query(Log).get(log_id)
    if not log:
        abort(404, message=f"Log {log_id} not found")


class LogsResource(Resource):
    def get(self, log_id):
        abort_if_job_not_found(log_id)
        db_ses = db_session.create_session()
        log = db_ses.query(Log).get(log_id)
        return jsonify(
            {
                'log': log.to_dict(only=(
                    'id', 'user_id', 'summa', 'checks', 'data'))
            }
        )

    def delete(self, log_id):
        abort_if_job_not_found(log_id)
        db_sess = db_session.create_session()
        log = db_sess.query(Log).get(log_id)
        db_sess.delete(log)
        db_sess.commit()
        return jsonify({'success': 'OK'})


class LogsListResource(Resource):
    def get(self):
        db_sess = db_session.create_session()
        logs = db_sess.query(Log).all()
        return jsonify(
            {
                'logs':
                    [item.to_dict(only=(
                        'id', 'user_id', 'summa', 'checks', 'data'))
                        for item in logs]
            }
        )

    def post(self):
        db_sess = db_session.create_session()
        args = parser.parse_args()
        if not db_sess.query(User).filter(User.id == args['user_id']).first():
            return jsonify({'error': 'User ID not found'})
        elif args['summa'] <= 0:
            return jsonify({'error': 'Summa less than zero'})
        log = Log(user_id=args['user_id'], summa=args['summa'], checks=args['checks'])
        db_sess.add(log)
        db_sess.commit()
        return jsonify({'success': 'OK'})

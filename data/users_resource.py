from flask_restful import reqparse, abort, Api, Resource
from flask import jsonify
from . import db_session
from .users import User
from .users_parser import parser


def abort_if_job_not_found(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f"User {user_id} not found")


class UsersResource(Resource):
    def get(self, user_id):
        abort_if_job_not_found(user_id)
        db_ses = db_session.create_session()
        user = db_ses.query(User).get(user_id)
        return jsonify(
            {
                'user': user.to_dict(only=(
                    'id', 'fio', 'password', 'is_admin', 'number_phone'))
            }
        )

    def delete(self, user_id):
        abort_if_job_not_found(user_id)
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(user_id)
        db_sess.delete(user)
        db_sess.commit()
        return jsonify({'success': 'OK'})


class UsersListResource(Resource):
    def get(self):
        db_sess = db_session.create_session()
        users = db_sess.query(User).all()
        return jsonify(
            {
                'users':
                    [item.to_dict(only=(
                        'id', 'fio', 'password', 'is_admin', 'number_phone'))
                        for item in users]
            }
        )

    def post(self):
        db_sess = db_session.create_session()
        args = parser.parse_args()
        if db_sess.query(User).filter(User.number_phone == args['number_phone']).first():
            return jsonify({'error': 'User number phone is already exists'})
        user = User(fio=args['fio'], password=args['password'], is_admin=args['is_admin'],
                    number_phone=args['number_phone'])
        db_sess.add(user)
        db_sess.commit()
        return jsonify({'success': 'OK'})

from flask_restful import reqparse, abort, Api, Resource
from flask import jsonify
from . import db_session
from .playbills import Playbill
from .playbills_parser import parser


def abort_if_job_not_found(playbill_id):
    session = db_session.create_session()
    playbill = session.query(Playbill).get(playbill_id)
    if not playbill:
        abort(404, message=f"Playbill {playbill_id} not found")


class PlaybillsResource(Resource):
    def get(self, playbill_id):
        abort_if_job_not_found(playbill_id)
        db_ses = db_session.create_session()
        playbill = db_ses.query(Playbill).get(playbill_id)
        return jsonify(
            {
                'playbill': playbill.to_dict(only=(
                    'id', 'image', 'key_word'))
            }
        )

    def delete(self, playbill_id):
        abort_if_job_not_found(playbill_id)
        db_sess = db_session.create_session()
        playbill = db_sess.query(Playbill).get(playbill_id)
        db_sess.delete(playbill)
        db_sess.commit()
        return jsonify({'success': 'OK'})


class PlaybillsListResource(Resource):
    def get(self):
        db_sess = db_session.create_session()
        playbills = db_sess.query(Playbill).all()
        return jsonify(
            {
                'playbills':
                    [item.to_dict(only=(
                        'id', 'image', 'key_word'))
                        for item in playbills]
            }
        )

    def post(self):
        db_sess = db_session.create_session()
        args = parser.parse_args()
        playbill = Playbill(image=args['image'], key_word=args['key_word'])
        db_sess.add(playbill)
        db_sess.commit()
        return jsonify({'success': 'OK'})

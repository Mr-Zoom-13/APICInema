from flask_restful import reqparse, abort, Api, Resource
from flask import jsonify
from . import db_session
from .prices import Price
from .prices_parser import parser


def abort_if_job_not_found(price_id):
    session = db_session.create_session()
    price = session.query(Price).get(price_id)
    if not price:
        abort(404, message=f"Price {price_id} not found")


class PricesResource(Resource):
    def get(self, price_id):
        abort_if_job_not_found(price_id)
        db_ses = db_session.create_session()
        price = db_ses.query(Price).get(price_id)
        return jsonify(
            {
                'price': price.to_dict(only=(
                    'id', 'price', 'data'))
            }
        )

    def delete(self, price_id):
        abort_if_job_not_found(price_id)
        db_sess = db_session.create_session()
        price = db_sess.query(Price).get(price_id)
        db_sess.delete(price)
        db_sess.commit()
        return jsonify({'success': 'OK'})

    def put(self, price_id):
        abort_if_job_not_found(price_id)
        args = parser.parse_args()
        db_sess = db_session.create_session()
        price = db_sess.query(Price).get(price_id)
        price.price = args['price']
        db_sess.commit()
        return jsonify({'success': 'OK'})


class PricesListResource(Resource):
    def get(self):
        db_sess = db_session.create_session()
        prices = db_sess.query(Price).all()
        return jsonify(
            {
                'prices':
                    [item.to_dict(only=(
                        'id', 'price', 'data'))
                        for item in prices]
            }
        )

    def post(self):
        db_sess = db_session.create_session()
        args = parser.parse_args()
        price = Price(price=args['price'])
        db_sess.add(price)
        db_sess.commit()
        return jsonify({'success': 'OK'})

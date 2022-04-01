from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument('fio', required=True)
parser.add_argument('password', required=True)
parser.add_argument('is_admin', required=True, type=bool)
parser.add_argument('number_phone', required=True, type=int)
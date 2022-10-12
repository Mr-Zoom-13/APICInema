from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument('user_id', required=True, type=int)
parser.add_argument('summa', required=True, type=int)
parser.add_argument('checks', required=True, type=int)

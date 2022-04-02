from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument('width', required=True, type=int)
parser.add_argument('height', required=True, type=int)
parser.add_argument('cinema_id', required=True, type=int)
parser.add_argument('number', required=True, type=int)

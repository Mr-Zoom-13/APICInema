from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument('title', required=True)
parser.add_argument('cinema_id', required=True, type=int)
parser.add_argument('hall_id', required=True, type=int)
parser.add_argument('data', required=True)
parser.add_argument('seats', required=True)

parser_put = reqparse.RequestParser()
parser_put.add_argument('seats', required=True)

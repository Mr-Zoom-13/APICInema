from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument('image', required=True)
parser.add_argument('key_word', required=True)

import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Playbill(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'playbill'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    image = sqlalchemy.Column(sqlalchemy.String)
    key_word = sqlalchemy.Column(sqlalchemy.String, unique=True)

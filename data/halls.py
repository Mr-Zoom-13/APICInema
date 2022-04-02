import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin


class Hall(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'hall'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    width = sqlalchemy.Column(sqlalchemy.Integer)
    height = sqlalchemy.Column(sqlalchemy.Integer)
    cinema_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('cinema.id'))
    number = sqlalchemy.Column(sqlalchemy.Integer)
    cinema = orm.relation('Cinema')
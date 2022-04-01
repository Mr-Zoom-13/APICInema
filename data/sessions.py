import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin


class Session(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'session'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String)
    cinema_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('cinema.id'))
    hall_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('hall.id'))
    data = sqlalchemy.Column(sqlalchemy.String)
    seats = sqlalchemy.Column(sqlalchemy.String)
    cinema = orm.relation('Cinema')
    hall = orm.relation('Hall')

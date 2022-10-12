import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm
from datetime import date
from sqlalchemy_serializer import SerializerMixin


class Log(SqlAlchemyBase,  SerializerMixin):
    __tablename__ = 'log'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('user.id'))
    summa = sqlalchemy.Column(sqlalchemy.Integer)
    checks = sqlalchemy.Column(sqlalchemy.Integer, unique=True)
    data = sqlalchemy.Column(sqlalchemy.Date, default=date.today)
    user = orm.relation('User')
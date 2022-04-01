import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm
from datetime import date


class Price(SqlAlchemyBase):
    __tablename__ = 'price'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    price = sqlalchemy.Column(sqlalchemy.Integer)
    data = sqlalchemy.Column(sqlalchemy.Date, default=date.today)

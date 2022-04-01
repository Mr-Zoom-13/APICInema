import sqlalchemy
from .db_session import SqlAlchemyBase


class Cinema(SqlAlchemyBase):
    __tablename__ = 'cinema'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, unique=True)
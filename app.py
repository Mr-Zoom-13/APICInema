from flask import Flask
from flask_admin.contrib.sqla import ModelView
from flask_restful import Api
from data import db_session
from data import users_resource, cinemas_resource, halls_resource, logs_resource, \
    playbills_resource, prices_resource, sessions_resource
import os
from flask_admin import Admin
from data.cinemas import Cinema
from data.halls import Hall
from data.logs import Log
from data.playbills import Playbill
from data.prices import Price
from data.sessions import Session
from data.users import User
from waitress import serve

app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_muuu123grom'
api = Api(app)
admin = Admin(app)


def main():
    db_session.global_init('db/cinema.db')
    db_ses = db_session.create_session()
    admin.add_view(ModelView(Cinema, db_ses))
    admin.add_view(ModelView(Hall, db_ses))
    admin.add_view(ModelView(Log, db_ses))
    admin.add_view(ModelView(Playbill, db_ses))
    admin.add_view(ModelView(Price, db_ses))
    admin.add_view(ModelView(Session, db_ses))
    admin.add_view(ModelView(User, db_ses))
    api.add_resource(users_resource.UsersListResource, '/api/v2/users')
    api.add_resource(users_resource.UsersResource, '/api/v2/users/<int:user_id>')
    api.add_resource(halls_resource.HallsListResource, '/api/v2/halls')
    api.add_resource(halls_resource.HallsResource, '/api/v2/halls/<int:hall_id>')
    api.add_resource(cinemas_resource.CinemasListResource, '/api/v2/cinemas')
    api.add_resource(cinemas_resource.CinemasResource, '/api/v2/cinemas/<int:cinema_id>')
    api.add_resource(logs_resource.LogsListResource, '/api/v2/logs')
    api.add_resource(logs_resource.LogsResource, '/api/v2/logs/<int:log_id>')
    api.add_resource(playbills_resource.PlaybillsListResource, '/api/v2/playbills')
    api.add_resource(playbills_resource.PlaybillsResource,
                     '/api/v2/playbills/<int:playbill_id>')
    api.add_resource(prices_resource.PricesListResource, '/api/v2/prices')
    api.add_resource(prices_resource.PricesResource, '/api/v2/prices/<int:price_id>')
    api.add_resource(sessions_resource.SessionsListResource, '/api/v2/sessions')
    api.add_resource(sessions_resource.SessionsResource, '/api/v2/sessions/<int:session_id>')
    serve(app, host='0.0.0.0', port=5000)
    # app.run(host='0.0.0.0', port=5000)


@app.route('/')
def index():
    return 'HI'


@app.route('/api/v2/m')
def index_2():
    return 'HI2'


if __name__ == '__main__':
    main()

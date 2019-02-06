import sys, os
sys.path.insert(0, os.path.abspath('..'))
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment

mail = Mail()
bootstrap = Bootstrap()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'main.login'
moment = Moment()



def create_app(config_name):         #Application Factory

    app = Flask(__name__)
    
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    
    bootstrap.init_app(app)
    db.init_app(app)
    from .models.users import User, Role
    with app.app_context():
        #db.drop_all()
        db.create_all()
    login_manager.init_app(app)
    mail.init_app(app)
    moment.init_app(app)

    from .main import error, main
    
    app.register_blueprint(error)
    app.register_blueprint(main)

    return app
    

from flask import Flask
from flask_cache import Cache
from flask_pagedown import PageDown
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_login import LoginManager
from flask_mail import Mail

from config import config

db = SQLAlchemy()
bootstrap = Bootstrap()
moment = Moment()
mail = Mail()
pagedown = PageDown()
cache = Cache()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


def create_app(config_name):
    """
    创建应用的方法
    :param config_name:
    :return:
    """
    # 初始化应用及配置
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app()

    # 初始化拓展
    db.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    pagedown.init_app(app)
    cache.init_app(app)
    api = Api(app)

    from app.api.main import PostApi
    api.add_resource(PostApi, '/api_1_0/posts')

    from app.api.main import UserApi
    api.add_resource(UserApi, '/api_1_0/users')

    # 注册蓝本
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app

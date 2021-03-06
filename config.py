import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'easy to guess string ? no,no,no.'

    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_RECORD_TIMEOUT = True

    MAIL_SERVER = 'smtp.189.cn'
    MAIL_PORT = 25
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or '17730804096@189.cn'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or '6827427955'
    MAIL_SUBJECT_PROFIX = '[keke]'
    MAIL_SENDER = 'keke Admin <17730804096@189.cn>'

    FLASKY_ADMIN = 'kevinforlj@163.com'

    # 每页加载多少个内容
    FLASKY_POST_PER_PAGE = 12
    FLASKY_FOLLOWERS_PER_PAGE = 12
    FLASKY_COMMENTS_PER_PAGE = 10

    # Cache configuration
    CACHE_TYPE = 'redis'
    CACHE_REDIS_HOST = '127.0.0.1'
    CACHE_REDIS_PORT = 6379
    CACHE_REDIS_PASSWORD = ''
    CACHE_REDIS_DB = ''

    UPLOAD_FOLDER = basedir+'/app/static/uploads'
    ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    @staticmethod
    def init_app():
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
                              'mysql+pymysql://root:qwer@localhost:3306/pythonist_dev'


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
                              'mysql+pymysql://root:qwer@localhost:3306/pythonist_test'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
                              'mysql+pymysql://root:qwer@localhost:3306/pythonist_pro'


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}

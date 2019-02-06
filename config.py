import os
base_dir=os.path.abspath(os.path.dirname(__file__))

class  Config:

    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SECRET_KEY = 'a2a844344fafd7f218aad2e10269572b'
    SQLALCHEMY_DATABASE_URI = \
                            'sqlite:///' + os.path.join(base_dir, 'data.sqlite')
    MAIL_SERVER = 'smtp.mail.yahoo.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = 'Mankaran Singh'
    MAIL_PASSWORD = 'Devilman32'
    ADMIN = 'mankaran32@gmail..com'
    DEBUG = True

    @staticmethod
    def init_app(app):
        pass
        

class Development(Config):
    pass

class Production(Config):
    pass

class Testing(Config):
    pass


config = {'default' : Config,
          'development' : Development,
          'production' : Production,
          'testing' : Testing}
          

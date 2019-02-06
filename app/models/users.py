from .. import db, login_manager, mail
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, render_template, request
from flask_mail import Message
from datetime import datetime
import hashlib


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Permission:

    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_POST = 0x03
    MODERATE_COMMENTS = 0x08
    ADMINISTRATOR = 0x80 

class Role(db.Model, UserMixin ):

    __tablename__ = 'roles'

    role_name =  db.Column(db.String(50), unique = True)
    id = db.Column(db.Integer, primary_key = True)
    users = db.relationship('User' , backref = 'role', lazy = 'dynamic' )
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)

    @staticmethod
    def insert_roles():

        roles = {'User': (Permission.FOLLOW | Permission.COMMENT | Permission.WRITE_POST, True), 
                 'Moderator': (Permission.FOLLOW | Permission.COMMENT | Permission.WRITE_POST | Permission.MODERATE_COMMENTS, False),
                 'Administrator':( Permission.FOLLOW | Permission.COMMENT | Permission.WRITE_POST | Permission.MODERATE_COMMENTS | Permission.ADMINISTRATOR, False)}

        for r in roles:
            if Role.query.filter_by(role_name = str(r)).first() is None:
                role = Role(role_name = str(r))
                role.permissions = roles[r][0]
                role.default = roles[r][1]
                db.session.add(role)
            else:
                continue
            
        db.session.commit()
               
                

class User(db.Model, UserMixin):

    __tablename__ = 'users'
    
    username = db.Column(db.String(50), unique = True, nullable = False)
    id = db.Column(db.Integer, primary_key = True, nullable = False)
    role_id = db.Column(db.Integer , db.ForeignKey('roles.id'))
    email = db.Column(db.String(120), unique= True, nullable = False)
    password = db.Column(db.String(120), nullable = False)
    confirmed = db.Column(db.Boolean, default = False)
    about_me = db.Column(db.Text())
    location = db.Column(db.String(64))
    member_since = db.Column(db.DateTime(),default = datetime.utcnow)
    last_seen = db.Column(db.DateTime(),default = datetime.utcnow)
    avtar_hash = db.Column(db.String(32))
    posts = db.relationship('Post', backref = 'author', lazy ='dynamic')

    blood_group = db.Column(db.String(50),nullable = False)
    phone_number = db.Column(db.Integer, nullable = False)
    require = db.Column(db.Boolean, default = False)
    donate = db.Column(db.Integer, default = 0)
    age = db.Column(db.Integer, nullable = False, )
        
    def generate_confirmation_token(self, expiration = 3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm':self.id})

    def confirm(self,token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm')!= self.id:
            return False
        self.confirm = True
        db.session.add(self)
        return True

    def send_mail(to, subject, template, **kwargs):
        msg = Message(subject, sender = 'mankaran32@gmail.com',
                      recipients = [str(to)])
        msg.body = render_template(str(template) + '.txt', **kwargs)
        mail.send(msg)

    def can(self, permissions):
        if self.role.permissions >= permissions:
            return True
        return False
    def is_admin(self):
        if self.role.permissions == Permission.ADMINISTRATOR:
            return True
        return False

    def ping(self):
        self.last_seen = datetime.utcnow()

    def generate_avtar_hash(self):
        return hashlib.md5(self.email.encode('utf-8')).hexdigest()
        

    def get_avtar(self, size = 50, default = 'identicon', rating = 'g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'

        else:
            url = 'http://www.gravatar.com/avatar'

        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(url=url, hash=self.avtar_hash , size=size, default=default, rating=rating)

    @staticmethod
    def generate_fake(count = 100):
        from random import seed
        import forgery_py
        

        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(True),
                     password=forgery_py.lorem_ipsum.word(),
                     confirmed=True,
                     location=forgery_py.address.city(),
                     about_me=forgery_py.lorem_ipsum.sentence(),
                     member_since=forgery_py.date.date(True))
            u.avtar_hash = u.generate_avtar_hash()

            db.session.add(u)
            try:
                db.session.commit()
            except :
                db.session.rollback()
                
            
class Post(db.Model):

    __table__name = 'posts'

    id = db.Column(db.Integer, primary_key= True)
    body = db.Column(db.Text, nullable = False)
    timestamp = db.Column(db.DateTime, index = True, default = datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py
         
        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            p = Post(body=forgery_py.lorem_ipsum.sentences(randint(1, 3)),
                        timestamp=forgery_py.date.date(True),author=u)
            db.session.add(p)
        db.session.commit()



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


    

        
    

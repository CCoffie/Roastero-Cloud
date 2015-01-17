from datetime import datetime
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request, url_for, json
from flask.ext.login import UserMixin, AnonymousUserMixin
from app.exceptions import ValidationError
from . import db, login_manager



class JsonType(db.TypeDecorator):
    impl = db.Unicode
    def process_bind_param(self, value, dialect):
        if value :
            return unicode(json.dumps(value))
        else:
            return "{}"
    def process_result_value(self, value, dialect):
        if value:
            return json.loads(value)
        else:
            return "{}"

class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return self.name

class Recipe(db.Model):
    __tablename__ = 'recipes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    description = db.Column(db.Text())
    recipe = db.Column(JsonType())
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    bean_id = db.Column(db.Integer, db.ForeignKey('beans.id'))

    def __repr__(self):
        return self.name

class Bean(db.Model):
    __tablename__ = 'beans'
    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.String(2048))
    name = db.Column(db.String(64))
    type = db.Column(db.String(64))
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'))
    reseller_id = db.Column(db.Integer, db.ForeignKey('resellers.id'))
    recipes = db.relationship('Recipe', backref='bean', lazy='dynamic')

    def __repr__(self):
        return self.name

class Country(db.Model):
    __tablename__ = 'countries'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    beans = db.relationship('Bean', backref='country', lazy='dynamic')
    region_id = db.Column(db.Integer, db.ForeignKey('regions.id'))

    def __repr__(self):
        return self.name

    def insert_countries():
        countries = {"Central America":["Costa Rica","Guatemala","Honduras","Mexico","Nicaragua","Panama","El Salvador"],
                    "South America":["Bolivia","Brazil","Colombia","Ecuador","Peru"],
                    "Africa and Arabia":["Burundi","Congo","Ethiopia","Kenya","Rwanda","Tanzania","Uganda","Yemen","Zambia","Zimbabwe"],
                    "Indonesia and Asia":["Bali","Flores","India","Java","Myanmar","Papua New Guinea","Sumatra","Sulawesi","Timor"],
                    "Islands and Others":["Australia","Dominican Republic","Hawaii","Jamaica","Puerto Rico","St Helena","Chicory"]}

        for region, countrySet in countries.items():
            currentRegion = Region.query.filter_by(name=region).first()
            if currentRegion is None:
                continue
            else:
                for country in countrySet:
                    currentCountry = Country(name=country,region=currentRegion)
                    db.session.add(currentCountry)
        db.session.commit()

class Region(db.Model):
    __tablename__ = 'regions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    countries = db.relationship('Country', backref='region', lazy='dynamic')

    def __repr__(self):
        return self.name

    def insert_regions():
        regions = ["Central America","South America","Africa and Arabia",
                "Indonesia and Asia","Islands and Others"]
        for r in regions:
            region = Region.query.filter_by(name=r).first()
            if region is None:
                region = Region(name=r)
            db.session.add(region)
        db.session.commit()

class Reseller(db.Model):
    __tablename__ = 'resellers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    website = db.Column(db.String(2048))
    location = db.Column(db.String(64))
    beans = db.relationship('Bean', backref='reseller', lazy='dynamic')

    def __repr__(self):
        return self.name

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))
    recipes = db.relationship('Recipe', backref='creator', lazy='dynamic')

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(True),
                     password=forgery_py.lorem_ipsum.word(),
                     confirmed=True,
                     name=forgery_py.name.full_name(),
                     location=forgery_py.address.city(),
                     about_me=forgery_py.lorem_ipsum.sentence(),
                     member_since=forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(
                self.email.encode('utf-8')).hexdigest()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        return True

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    def to_json(self):
        json_user = {
            'username': self.username,
            'member_since': self.member_since,
            'last_seen': self.last_seen
        }
        return json_user

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id': self.id}).decode('ascii')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def __repr__(self):
        return self.username


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

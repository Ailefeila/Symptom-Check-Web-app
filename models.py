"""SQLAlchemy models for symptom check."""

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


bcrypt = Bcrypt()
db = SQLAlchemy()



class User(db.Model):
    """User in the system."""

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    firstname = db.Column(
        db.Text,
        #nullable=False,
    )

    lastname = db.Column(
        db.Text,
        #nullable=False,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    members = db.relationship('Member', backref="user", cascade="all, delete-orphan")


    @classmethod
    def signup(cls, email, password):
        """Sign up user.
        Hashes password and adds user to system."""

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')
        return cls(email=email, password=hashed_pwd)

    @classmethod
    def authenticate(cls, email, password):
        """Find user with `email` and `password`.
        if can't find matching user or if password is wrong, return False"""

        user = cls.query.filter_by(email=email).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user
        return False


class Member(db.Model):
    """ Member under user."""

    __tablename__ = 'members'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.Text,
        nullable=False,
    )

    gender = db.Column(
        db.Text,
        nullable=False,
    )

    age = db.Column(
        db.Text,
        nullable=False,
        default='30'
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False,
    )



class Diagnose(db.Model):
    """Mapping of a disease to a member"""

    __tablename__ = 'diagnoses'

    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), primary_key=True)
    disease_id = db.Column(db.Integer, db.ForeignKey('diseases.id'), primary_key=True)


class Disease(db.Model):

    __tablename__ = 'diseases'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    name = db.Column(
        db.Text,
        nullable=False,
    )

    probability = db.Column(
        db.Text,
        nullable=False
    )

    members = db.relationship(
        'Member',
        secondary="diagnoses",
        cascade="all, delete",
        backref="diseases",
    )

def connect_db(app):
    """Connect this database to provided Flask app."""

    db.app = app
    db.init_app(app)

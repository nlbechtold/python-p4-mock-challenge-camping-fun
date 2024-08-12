from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

db = SQLAlchemy()

class Activity(db.Model, SerializerMixin):
    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    difficulty = db.Column(db.Integer)

    signups = db.relationship('Signup', backref='activity', cascade='all, delete-orphan')

    serialize_rules = ('-signups.activity',)

    def __repr__(self):
        return f'<Activity {self.id}: {self.name}>'

class Camper(db.Model, SerializerMixin):
    __tablename__ = 'campers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    age = db.Column(db.Integer, nullable=False)

    signups = db.relationship('Signup', backref='camper', cascade='all, delete-orphan')

    serialize_rules = ('-signups.camper',)

    @validates('age')
    def validate_age(self, key, value):
        if 8 <= value <= 18:
            return value
        raise ValueError("Age must be between 8 and 18")
    
    @validates('name')
    def validate_name(self, key, value):
        if value:
            return value
        raise ValueError("Name cannot be empty")
    def __repr__(self):
        return f'<Camper {self.id}: {self.name}>'

class Signup(db.Model, SerializerMixin):
    __tablename__ = 'signups'

    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer)

    camper_id = db.Column(db.Integer, db.ForeignKey('campers.id'))
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'))

    serialize_rules = ('-camper.signups', '-activity.signups',)

    @validates('time')
    def validate_time(self, key, value):
        if 0 <= value <= 23:
            return value
        raise ValueError("Time must be between 0 and 23")

    def __repr__(self):
        return f'<Signup {self.id}>'

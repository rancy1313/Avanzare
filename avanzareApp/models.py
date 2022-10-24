from . import db
# cuz in same directory you can just use dot instead of
# from website import db if it was outside this directory
from flask_login import UserMixin
from sqlalchemy.sql import func

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    # foreign key is an id that references to another id in another database column
    # one to many relationships
    # one user to many notes
    # python class is capital but sql needs lower case
    # thats why it is user.id and not User.id
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class User(db.Model, UserMixin):
    # most cases you'll use columns
    # id is an integer and is the primary key to identifying a user
    id = db.Column(db.Integer, primary_key=True)
    # .String(max length of string)
    # unique=True means no users can have same email
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    # kind of like a list that stores the user's notes
    # for some reason Note is capital here sql be funky
    notes = db.relationship('Note')
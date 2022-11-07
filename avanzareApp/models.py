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

class Menu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True)
    price = db.Column(db.String(150))
    description = db.Column(db.String(10000))
    menu_type = db.Column(db.String(150))
    gluten_free = db.Column(db.String(150))
    vegan = db.Column(db.String(150))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Menu_order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    price = db.Column(db.String(150))
    description = db.Column(db.String(10000))
    menu_type = db.Column(db.String(150))
    gluten_free = db.Column(db.String(150))
    vegan = db.Column(db.String(150))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    comment = db.Column(db.String(10000))
    taxes = db.Column(db.Float)
    total = db.Column(db.Float)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_active = db.Column(db.String(10))
    # stores menu items??
    # too solutions use the relationship list by using a new Menu db with no primary kery for name
    # private list variable??
    items = db.relationship('Menu_order')

class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    text = db.Column(db.String(10000))
    news_type = db.Column(db.String(150))
    featured = db.Column(db.String(10))
    date = db.Column(db.DateTime(timezone=True), default=func.now())




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
    items = db.relationship('Menu')
    orders = db.relationship('Order')


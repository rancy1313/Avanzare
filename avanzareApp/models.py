from . import db
# cuz in same directory you can just use dot instead of
# from website import db if it was outside this directory
from flask_login import UserMixin
from sqlalchemy.sql import func

# this class is for the chef to create a menu item
# just has info about the item created by the chef
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

# this class is for the user to add an item to an order
# At first, I found it best to separate menu items for orders and menu items for editing the menu because
# the menu order didn't require a user id and the Menu item for editing didn't require an order id
# maybe I could have just used one class anyway, but I made it work with two
# Might consider just combining these two and using the variables when needed.
# MENU_ORDER WAS CREATED BECAUSE MENU ITEMS ARE SUPPOSED TO BE UNIQUE SO YOU WOULDN'T BE ABLE TO CREATE COPIES
# WHICH WOULD BE NEEDED IF YOU'RE TRYING TO ORDER MORE THAN ONE OF THE SAME ITEM
# so keeping Menu_order and Menu separate is still viable
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

# this class is to structure an order and has info about the order
# and it has a list of items related to this order
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

# this class is for the chef to create news posts
class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    text = db.Column(db.String(10000))
    news_type = db.Column(db.String(150))
    featured = db.Column(db.String(10))
    date = db.Column(db.DateTime(timezone=True), default=func.now())

# structure for a users account
# a lot more variables can be added here in the future
# I was considering adding one for if the user can set their account to have allergies
# and if they do then their orders will appear red
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
    items = db.relationship('Menu')
    orders = db.relationship('Order')


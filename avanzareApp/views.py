from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Note, Menu, User, Order, Menu_order
from . import db
import json

views = Blueprint('views', __name__)

# add orders variable to User class
# create a class ofr orders and link by id
# make a list of items to add on orders
# save each list as a separate order
# JUST IDEA might need two new tables one for individual orders and
# one that takes lists of orders to check order history
# maybe orders can also add a comment to each dish
# maybe in user sign up you can add alergies also have nav that can edit it
# gonna have to change base.html or create base html for headCHef account
# add html the pizza descriptio. Look for more menu data to be added
# pictures of food??
# {% if user.email == 'headChef@gmail.com" %}
# something like <a class="nav-item nav-link" id="home" href="/add_menu">add_menu</a>

#decorator
@views.route('/add-menu-item', methods=['GET', 'POST'])
@login_required
def add_menu_item():
    if request.method == 'POST':
        name = request.form.get('name')
        price = request.form.get('price')
        description = request.form.get('description')
        menu_type = request.form.get('menu_type')

        menu_item = Menu.query.filter_by(name=name).first()

        if menu_item:
            flash('This dish name already exists.', category="error")

        #elif len(description) > 10000:
            #flash('Description must be less than 10,000 characters.', category="error")
        else:
            # add the user
            new_menu_item = Menu(name=name, price=price, description=description, menu_type=menu_type, user_id=current_user.id)
            db.session.add(new_menu_item)
            db.session.commit()
            #login_user(user, remember=True)
            flash('New item added to menu!!!', category="success")
            user = User.query.filter(User.email == 'headChef@gmail.com').first()
            items = Menu.query.filter_by(user_id=user.id).order_by(Menu.name).all()
            return render_template("edit_menu.html", items=items, user=current_user)
        # this is needed just in case to show items just in case add item gets error
    user = User.query.filter(User.email == 'headChef@gmail.com').first()
    items = Menu.query.filter_by(user_id=user.id).order_by(Menu.name).all()

    return render_template("edit_menu.html", items=items, user=current_user)

#decorator
@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Note is too short!', category="error")
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added.', category="success")
    return render_template("home.html", user=current_user)

@views.route('/user_home', methods=['GET', 'POST'])
@login_required
def user_home():
    active_orders = Order.query.filter(Order.user_id == current_user.id).filter(Order.is_active == "Active").all()
    return render_template("user_home.html", active_orders=active_orders, user=current_user)

@views.route('/order', methods=['GET', 'POST'])
@login_required
def order():
    # create order
    # we need to pass new_item to access its order id
    print("next Order??????????")
    new_order = Order(user_id=current_user.id, total=0)
    db.session.add(new_order)
    db.session.commit()
    print(new_order.id)
    user = User.query.filter(User.email == 'headChef@gmail.com').first()
    items = Menu.query.filter_by(user_id=user.id).order_by(Menu.name).all()
    return render_template("order.html", items=items, new_order=new_order, user=current_user)

@views.route('/add-to-order/<int:item_id>/<int:order_id>', methods=['GET', 'POST'])
def add_to_order(item_id, order_id):
    # add to order
    # change how you add an item i think
    item = Menu.query.filter(Menu.id == item_id).first()

    new_order = Order.query.filter(Order.id == order_id).first()
    # create a copy of the itme to add in the order relationship list
    # has to be a copy because menu items are uniqe in the list
    if request.method != "POST":
        item_copy = Menu_order()
        item_copy.name = item.name
        item_copy.price = item.price
        item_copy.description = item.description
        item_copy.menu_type = item.menu_type
        item_copy.order_id = order_id
        # calculate order total
        new_order.total = new_order.total + float(item_copy.price)
        db.session.add(item_copy)
        db.session.commit()
        print("will it add twice??")
        flash('Item added.', category="success")
    user = User.query.filter(User.email == 'headChef@gmail.com').first()
    items = Menu.query.filter_by(user_id=user.id).order_by(Menu.name).all()

    if request.method == "POST":
        print("final part????")
        new_order.name = current_user.first_name
        new_order.comment = request.form.get('comment')
        new_order.is_active = "Active"
        flash('Order Submitted!!!', category="success")
        #db.session.add(new_order)
        db.session.commit()
        print("yoooooo")
        return redirect(url_for('views.user_home'))
    return render_template('order.html', items=items, new_order=new_order, user=current_user)


@views.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})

@views.route('/delete-item', methods=['POST', 'GET'])
def delete_item():
    item = json.loads(request.data)
    itemId = item['itemId']
    item = Menu.query.get(itemId)

    if item:
        if item.user_id == current_user.id:
            db.session.delete(item)
            db.session.commit()
            flash('ITEM DELETED!', category="success")
    else:
        flash('error!', category="error")
    return jsonify({})


@views.route('/delete-order-item', methods=['POST', 'GET'])
def delete_order_item():
    item = json.loads(request.data)
    itemId = item['itemId']
    item = Menu_order.query.get(itemId)
    new_order = db.session.query(Order).order_by(Order.id.desc()).first()
    new_order.total = new_order.total - float(item.price)
    print("we are in the function")
    if item:
        db.session.delete(item)
        db.session.commit()
        print("should be deleted")
        flash('ITEM DELETED!', category="success")
    else:
        flash('error!', category="error")
        print("nvm didnt work")
    return jsonify({})


@views.route('/refresh-order', methods=['GET', 'POST'])
def refresh_order():
    #return redirect(url_for('views.add_to_order'))
    if request.method == "POST":
        print("final part????")
        new_order = db.session.query(Order).order_by(Order.id.desc()).first()
        new_order.name = current_user.first_name
        new_order.comment = request.form.get('comment')
        new_order.is_active = "Active"
        flash('Order Submitted!!!', category="success")
        #db.session.add(new_order)
        db.session.commit()
        print("yoooooo")
        active_orders = Order.query.filter(Order.user_id == current_user.id).filter(Order.is_active == "Active").all()
        return render_template("user_home.html", active_orders=active_orders, user=current_user)
    new_order = db.session.query(Order).order_by(Order.id.desc()).first()
    user = User.query.filter(User.email == 'headChef@gmail.com').first()
    items = Menu.query.filter_by(user_id=user.id).order_by(Menu.name).all()
    return render_template("order.html", items=items, new_order=new_order, user=current_user)


@views.route('/edit_redirect/<int:id>', methods=['GET', 'POST'])
def edit_redirect(id):
    item = Menu.query.filter(Menu.id == id).first()
    if request.method == 'POST':
        print("first: ", item.name, item.price, item.description, item.menu_type, item.id)
        name = request.form.get('name')
        price = request.form.get('price')
        description = request.form.get('description')
        menu_type = request.form.get('menu_type')
        print("form vars:", name, price, description, menu_type)
        item.name = name
        item.price = price
        item.description = description
        item.menu_type = menu_type
        print(item.name, item.price, item.description, item.menu_type, item.id)
        flash('Item has been edited!!!', category="success")
        db.session.commit()
        return redirect(url_for('views.add_menu_item'))
    return render_template('edit_menu_item.html', item=item, user=current_user)

@views.route('/view-orders', methods=['POST', 'GET'])
def view_orders():
    active_orders = Order.query.filter(Order.is_active == 'Active').all()
    inactive_orders = Order.query.filter(Order.is_active == 'Inactive').all()
    return render_template('view_orders.html', active_orders=active_orders, inactive_orders=inactive_orders, user=current_user)

@views.route('/deactivate-order/<int:id>', methods=['POST', 'GET'])
def deactivate_orders(id):
    order = Order.query.filter(Order.id == id).first()
    order.is_active = "Inactive"
    active_orders = Order.query.filter(Order.is_active == 'Active').all()
    inactive_orders = Order.query.filter(Order.is_active == 'Inactive').all()
    db.session.commit()
    return render_template('view_orders.html', active_orders=active_orders, inactive_orders=inactive_orders, user=current_user)

@views.route('/clear-inactive-orders', methods=['POST', 'GET'])
def clear_inactive_orders():
    inactive_orders = Order.query.filter(Order.is_active == 'Inactive').all()
    for item in inactive_orders:
        item.is_active = "clear"
    db.session.commit()
    active_orders = Order.query.filter(Order.is_active == 'Active').all()
    inactive_orders = Order.query.filter(Order.is_active == 'Inactive').all()
    return render_template('view_orders.html', active_orders=active_orders, inactive_orders=inactive_orders, user=current_user)

@views.route('/corder-again/<int:id>', methods=['GET', 'POST'])
def order_again(id):
    if request.method != 'POST':
        # fetch old order to copy info over
        old_order = Order.query.filter(Order.id == id).first()
        new_order = Order(user_id=current_user.id, total=0)
        db.session.add(new_order)

        # copy order items and details
        for item in old_order.items:
            item_copy = Menu_order()
            item_copy.name = item.name
            item_copy.price = item.price
            item_copy.description = item.description
            item_copy.menu_type = item.menu_type
            item_copy.order_id = new_order.id
            # calculate order total
            new_order.total = new_order.total + float(item_copy.price)
            db.session.add(item_copy)
            db.session.commit()
            print("in loop")
    if request.method == "POST":
        print("final part????")
        new_order = Order.query.filter(Order.id == id).first()
        new_order.name = current_user.first_name
        new_order.comment = request.form.get('comment')
        new_order.is_active = "Active"
        flash('Order Submitted!!!', category="success")
        #db.session.add(new_order)
        db.session.commit()
        print("yoooooo")
        active_orders = Order.query.filter(Order.user_id == current_user.id).filter(Order.is_active == "Active").all()
        return render_template("user_home.html", active_orders=active_orders, user=current_user)

    print('ummm dang')
    #db.session.commit()
    user = User.query.filter(User.email == 'headChef@gmail.com').first()
    items = Menu.query.filter_by(user_id=user.id).order_by(Menu.name).all()
    return render_template("order.html", items=items, new_order=new_order, user=current_user)


from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import Note, Menu, User, Order, Menu_order, News
from . import db
import json

views = Blueprint('views', __name__)
# handling floating point errors

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
        # make sure no uses any weird characters or tries to do anything funny
        special_chars = '`~!@#$%^&*()-_=+|[]{};:<>\"\\/'
        for char in special_chars:
            if char in name:
                flash('No special chars allowed in item names (except \' ).', category="error")
                return redirect(url_for('views.add_menu_item'))
        price = request.form.get('price')
        try:
            # if price can't be converted to float then that means there are chars being used that are not digits
            float(price)
        except:
            flash('Only enter digits for price.', category="error")
            return redirect(url_for('views.add_menu_item'))
        if price == '0':
            flash('No free items.', category="error")
            return redirect(url_for('views.add_menu_item'))
        price = "{:,.2f}".format(float(price))
        description = request.form.get('description')
        for char in special_chars:
            if char in description:
                flash('No special chars allowed in description (except \' ).', category="error")
                return redirect(url_for('views.add_menu_item'))
        gluten_free = request.form.get('gluten_free')
        vegan = request.form.get('vegan')
        menu_type = request.form.get('menu_type')

        menu_item = Menu.query.filter_by(name=name).first()

        if menu_item:
            flash('This dish name already exists.', category="error")

        #elif len(description) > 10000:
            #flash('Description must be less than 10,000 characters.', category="error")
        else:
            # add the user
            new_menu_item = Menu(name=name, price=price, description=description, menu_type=menu_type, gluten_free=gluten_free, vegan=vegan, user_id=current_user.id)
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
    # sometimes when the page is refreshed while on the order page
    # or everytime the order page is clicked it will create a new order
    # so I will delete those orders here
    error_orders = Order.query.filter(Order.user_id == current_user.id).filter(Order.is_active == None).delete()
    error_orders = Order.query.filter(Order.user_id == current_user.id).filter(Order.total == 0).delete()
    db.session.commit()
    active_orders = Order.query.filter(Order.user_id == current_user.id).filter(Order.is_active == "Active").all()
    news = db.session.query(News).order_by(News.id.desc()).all()
    db.session.commit()
    return render_template("user_home.html", news=news, active_orders=active_orders, user=current_user)

@views.route('/order', methods=['GET', 'POST'])
@login_required
def order():
    #test
    error_orders = Order.query.filter(Order.user_id == current_user.id).filter(Order.total == 0).all()
    for order in error_orders:
        db.session.delete(order)
    db.session.commit()
    # create order
    # we need to pass new_item to access its order id
    # MAYBE ITEMS=[] EMPTY LIST WILL FIX BUG WHERE IT SHOWS ITEMS WHEN YOU CLICK IN AND OUT OF ORDER
    new_order = Order(user_id=current_user.id, taxes=0,total=0)
    db.session.add(new_order)
    db.session.commit()

    if request.method == "POST":
        flash('Empty Order', category="error")
        return redirect(url_for('views.order'))
    user = User.query.filter(User.email == 'headChef@gmail.com').first()
    items = Menu.query.filter_by(user_id=user.id).order_by(Menu.name).all()
    return render_template("order.html", items=items, new_order=new_order, user=current_user)

@views.route('/add-to-order/<int:order_id>', methods=['GET', 'POST'])
def add_to_order(order_id):
    quantity = request.form.get('quantity')
    dish_accommodation = request.form.get('dish_accommodation')
    complete_order = request.form.get('complete_order')

    # just in case someone enters spaces but no digits
    # if quantity == none then can't strip usually when fresh order this occurs
    if quantity != None:
        if quantity.strip() == '':
            quantity = 1
    if quantity == None:
        quantity = 1

    delete_quantity = request.form.get('delete_quantity')

    if request.method == "POST" and delete_quantity is not None:
        item_id2 = request.form.get('itemId2')
        item = Menu_order.query.filter(Menu_order.id == item_id2).first()
        new_order = Order.query.filter(Order.id == order_id).first()
        delete_quantity = int(request.form.get('delete_quantity'))
        # if page is refreshed after deleting something then an errors occurs because item  becomes none
        # and tmp_name = item.name[:] causes and issue
        # so in that case refresh page
        if item is None:
            user = User.query.filter(User.email == 'headChef@gmail.com').first()
            items = Menu.query.filter_by(user_id=user.id).order_by(Menu.name).all()
            return render_template('order.html', items=items, new_order=new_order, user=current_user)
        # if you delete the item then you can't use it to delete other items
        tmp_name = item.name[:]
        count_lst = []
        for item_tmp in new_order.items:
            count_lst.append(item_tmp.name)

        count = count_lst.count(item.name)
        if count < delete_quantity:
            flash('Delete quantity greater than the amounts of items in order', category="error")
            user = User.query.filter(User.email == 'headChef@gmail.com').first()
            items = Menu.query.filter_by(user_id=user.id).order_by(Menu.name).all()
            return render_template('order.html', items=items, new_order=new_order, user=current_user)

        for x in range(delete_quantity):
            for item_compare_delete in new_order.items:
                if tmp_name == item_compare_delete.name:
                    new_order.total = new_order.total - float(item_compare_delete.price)
                    db.session.delete(item_compare_delete)
                    db.session.commit()
                    break
        # calculate taxes and add to total
        new_order.taxes = new_order.total * 0.08
        db.session.commit()
        flash('ITEMS DELETED!', category="success")
        user = User.query.filter(User.email == 'headChef@gmail.com').first()
        items = Menu.query.filter_by(user_id=user.id).order_by(Menu.name).all()
        return render_template('order.html', items=items, new_order=new_order, user=current_user)

    # if you want to add a quantity
    if request.method == "POST" and complete_order == 'FALSE' and delete_quantity is None:
        # add to order
        # change how you add an item i think
        item_id = request.form.get('itemId')
        item = Menu.query.filter(Menu.id == item_id).first()
        new_order = Order.query.filter(Order.id == order_id).first()
        # create a copy of the itme to add in the order relationship list
        # has to be a copy because menu items are unique in the list
        for x in range(int(quantity)):
            item_copy = Menu_order()
            if dish_accommodation is not None and dish_accommodation != 'REGULAR':
                item_copy.name = dish_accommodation + ' ' + item.name
            else:
                item_copy.name = item.name
            item_copy.price = item.price
            item_copy.description = item.description
            item_copy.menu_type = item.menu_type
            item_copy.gluten_free = item.gluten_free
            item_copy.vegan = item.vegan
            item_copy.order_id = order_id
            # calculate order total
            new_order.total = new_order.total + float(item_copy.price)

            db.session.add(item_copy)
            db.session.commit()

        new_order.taxes = new_order.total * 0.08
        db.session.commit()
        flash('Item added.', category="success")
        user = User.query.filter(User.email == 'headChef@gmail.com').first()
        items = Menu.query.filter_by(user_id=user.id).order_by(Menu.name).all()
        return render_template('order.html', items=items, new_order=new_order, user=current_user)

    if request.method == "POST" and complete_order != 'FALSE' and delete_quantity is None:
        new_order = db.session.query(Order).order_by(Order.id.desc()).first()
        new_order.name = current_user.first_name
        new_order.comment = request.form.get('comment')
        new_order.is_active = "Active"
        flash('Order Submitted!!!', category="success")
        #db.session.add(new_order)
        db.session.commit()
        return redirect(url_for('views.user_home'))



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
    if item:
        db.session.delete(item)
        db.session.commit()
        flash('ITEM DELETED!', category="success")
    else:
        flash('error!', category="error")
    return jsonify({})

'''
@views.route('/delete-by-quantity/<int:id>/<int:order_id>', methods=['POST', 'GET'])
def delete_by_quantity(id, order_id):
    print('hi')
    item = Menu_order.query.filter(Menu_order.id == id).first()
    new_order = Order.query.filter(Order.id == order_id).first()
    delete_quantity = int(request.form.get('delete_quantity'))

    for x in range(delete_quantity):
        for item_compare_delete in new_order.items:
            if item.name == item_compare_delete:
                db.session.delete(item)
                db.session.commit()
                break
    flash('ITEM DELETED!', category="success")
    return redirect(url_for('views.refresh_order'))'''


@views.route('/refresh-order', methods=['GET', 'POST'])
def refresh_order():
    # if post(user tries to submit order) after deleting an item then you can submit
    if request.method == "POST":
        new_order = db.session.query(Order).order_by(Order.id.desc()).first()
        # make sure user doesn't submit an empty order
        if new_order.total == 0:
            flash('Empty order.', category="error")
            return redirect(url_for('views.order'))
        new_order.name = current_user.first_name
        new_order.comment = request.form.get('comment')
        new_order.is_active = "Active"
        flash('Order Submitted!!!', category="success")
        #db.session.add(new_order)
        db.session.commit()
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
        name = request.form.get('name')
        special_chars = '`~!@#$%^&*()-_=+|[]{};:<>,.\"\\/'
        for char in special_chars:
            if char in name:
                flash('No special chars allowed in item names (except \' ).', category="error")
                return redirect(url_for('views.edit_redirect', id=id))
        price = request.form.get('price')
        price = "{:,.2f}".format(float(price))
        description = request.form.get('description')
        for char in special_chars:
            if char in description:
                flash('No special chars allowed in description (except \' ).', category="error")
                return redirect(url_for('views.edit_redirect', id=id))
        menu_type = request.form.get('menu_type')
        gluten_free = request.form.get('gluten_free')
        vegan = request.form.get('vegan')

        item.name = name
        item.price = price
        item.description = description
        item.menu_type = menu_type
        item.gluten_free = gluten_free
        item.vegan = vegan
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


'''

@views.route('/corder-again/<int:id>', methods=['GET', 'POST'])
def order_again(id):
    old_order = Order.query.filter(Order.id == id).first()
    new_order = Order(name=current_user.first_name, user_id=current_user.id, total=0)

    db.session.add(new_order)
    db.session.commit()
    if request.method == "POST":
        for item in old_order.items:
            name = request.form.get('name' + str(item.id))
            print(name)
            price = request.form.get('price' + str(item.id))
            print(price)
            description = request.form.get('description' + str(item.id))
            menu_type = request.form.get('menu_type' + str(item.id))
            gluten_free = request.form.get('gluten_free' + str(item.id))
            vegan = request.form.get('vegan' + str(item.id))
            item_copy = Menu_order(name=name, price=price, description=description,
                                  menu_type=menu_type, gluten_free=gluten_free, vegan=vegan,
                                  order_id=new_order.id)
            db.session.add(item_copy)
            db.session.commit()
            #item_copy = Menu_order(name=item.name, price=item.price, description = item.description, menu_type = item.menu_type, gluten_free = item.gluten_free, vegan = item.vegan, order_id = new_order.id)
            print(item_copy.price)
            new_order.total = new_order.total + float(item_copy.price)

            db.session.commit()

        new_order.comment = request.form.get('comment')



        new_order.is_active = "Active"
        flash('Order Submitted!!!', category="success")
        db.session.commit()
        return redirect(url_for('views.user_home'))
    user = User.query.filter(User.email == 'headChef@gmail.com').first()
    items = Menu.query.filter_by(user_id=user.id).order_by(Menu.name).all()
    return render_template("order_again.html", items=items, new_order=new_order, old_order=old_order, user=current_user)

'''
@views.route('/corder-again/<int:id>', methods=['GET', 'POST'])
def order_again(id):
    if request.method != 'POST':
        # fetch old order to copy info over
        error_orders = Order.query.filter(Order.is_active == None).all()
        old_order = Order.query.filter(Order.id == id).first()
        new_order = Order(user_id=current_user.id, total=0)
        new_order.items.clear()
        db.session.add(new_order)
        db.session.commit()
        for x in new_order.items:
            print("before loop: ",x.name)
            new_order.items.remove(x)
        print('!POST order again')

        # copy order items and details
        for item in old_order.items:
            item_copy = Menu_order()
            db.session.add(item_copy)
            db.session.commit()
            item_copy.name = item.name[:]
            item_copy.price = item.price
            item_copy.description = item.description[:]
            item_copy.menu_type = item.menu_type[:]
            item_copy.gluten_free = item.gluten_free[:]
            item_copy.vegan = item.vegan[:]
            item_copy.order_id = new_order.id
            # calculate order total
            new_order.total = new_order.total + float(item_copy.price)
            db.session.commit()

            print("loop")
        # db.session.commit()
        for x in new_order.items:
            print(x.name)
        user = User.query.filter(User.email == 'headChef@gmail.com').first()
        items = Menu.query.filter_by(user_id=user.id).order_by(Menu.name).all()
        return render_template("order.html", items=items, new_order=new_order, user=current_user)

    if request.method == "POST":
        print("POST")
        new_order = db.session.query(Order).order_by(Order.id.desc()).first()
        #new_order = Order.query.filter(Order.id == tmp_id).first()
        for x in new_order.items:
            print('post: ', x.name)
        new_order.name = current_user.first_name
        new_order.comment = request.form.get('comment')
        new_order.is_active = "Active"
        flash('Order Submitted!!!', category="success")
        #db.session.add(new_order)
        db.session.commit()
        active_orders = Order.query.filter(Order.user_id == current_user.id).filter(Order.is_active == "Active").all()
        #return render_template("user_home.html", active_orders=active_orders, user=current_user)
        return redirect(url_for('views.user_home'))


@views.route('/create-news', methods=['GET', 'POST'])
@login_required
def create_news():
    if request.method == "POST":
        title = request.form.get('title')
        text = request.form.get('text')
        news_type = request.form.get('news_type')
        news_post = News(title=title, text=text, news_type=news_type)
        db.session.add(news_post)
        db.session.commit()
        flash('News post created!', category="success")
    news = db.session.query(News).order_by(News.id.desc()).all()
    return render_template("create_news.html", news=news, user=current_user)

@views.route('/delete-news-post', methods=['POST', 'GET'])
def delete_news_post():
    news_post = json.loads(request.data)
    news_postId = news_post['news_postId']
    news_post = News.query.get(news_postId)

    if news_post:
        db.session.delete(news_post)
        db.session.commit()
        flash('NEWS POST DELETED!', category="success")
    else:
        flash('error!', category="error")
    return jsonify({})
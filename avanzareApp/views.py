from flask import Blueprint, render_template, request, flash, abort, jsonify, redirect, url_for, send_from_directory
from flask_login import login_required, current_user
from .models import Menu, User, Order, Menu_order, News
from . import db
import json
import os

# for image uploading
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
target = os.path.join(APP_ROOT, 'images/')
if not os.path.isdir(target):
    os.mkdir(target)
views = Blueprint('views', __name__)


# this function just returns the a specific image based on the name from the directory
@views.route('/upload/<filename>')
def send_image(filename):
    return send_from_directory('images', filename)


# get to edit menu page
@views.route('/edit-menu', methods=['GET'])
def edit_menu():
    # fetch all menu items
    items = Menu.query.all()
    # if user is not logged in and trying to access the page
    if current_user.is_anonymous:
        abort(404, description="Resource not found")
    # make sure page only loads for head chef
    if current_user.email == 'headChef@gmail.com':
        return render_template("edit_menu.html", items=items, user=current_user)
    else:
        flash('Sorry not allowed.', category="error")
        return redirect(url_for('views.user_home'))

# this is the function for the head chef to add any item they want to the menu. There are some requirements like menu
# items cannot have the same name, price must be digits/float, and limited chars for name/description.
@views.route('/add-to-menu', methods=['POST'])
def add_to_menu():
    # get input values from the chef
    name = request.form.get('name')
    price = request.form.get('price')
    description = request.form.get('description')
    menu_type = request.form.get('menu_type')
    gluten_free = request.form.get('gluten_free')
    vegan = request.form.get('vegan')
    tmp_file = request.files.get('file')
    filename = name + '.jpg'
    # if filename empty then do nothing because user doesn't want to change the item image
    if tmp_file.filename != '':
        destination = "/".join([target, filename])
        tmp_file.save(destination)
    else:
        flash('Item image not submitted.', category="error")
        return redirect(url_for('views.edit_menu'))
    # check if there is any item in Menu that already has the name that was entered by chef
    menu_item = Menu.query.filter_by(name=name).first()
    # if menu_item exists then that means the item name is taken already
    if menu_item:
        flash('This dish name already exists.', category="error")
    # test to make sure price is acceptable
    try:
        # if price can't be converted to float then that means there are chars being used that are not digits
        # might be a better way to implement this
        float(price)
        # convert str type price to format it in $0.00 format
        price = "{:,.2f}".format(float(price))
    # (Exception,) stop 'too broad' exception msg
    except (Exception,):
        # refresh page and send error message
        flash('Only enter digits for price.', category="error")
        return redirect(url_for('views.edit_menu'))
    # test to check against any special chars
    special_chars = '`~@#^*()-_=+|[]{};:<>\\/'
    for char in special_chars:
        # check if char is in name/description
        if char in name + description:
            message = 'Some special chars are not permitted such as: ' + char
            flash(message, category="error")
            return redirect(url_for('views.edit_menu'))
    # if all is good then create the item and refresh page
    item = Menu(name=name, price=price, description=description, menu_type=menu_type, gluten_free=gluten_free,
                vegan=vegan, item_image=filename, user_id=current_user.id)
    db.session.add(item)
    db.session.commit()
    return redirect(url_for('views.edit_menu'))


@views.route('/user_home', methods=['GET', 'POST'])
@login_required
def user_home():
    active_orders = Order.query.filter(Order.user_id == current_user.id).filter(Order.is_active == "Active").all()
    # user can view all restaurant's news in user home. This could be changed to show limited random news like in
    # the featured section of the start page, but I'm assuming that there wouldn't be that many news
    # coming from a small family restaurant
    news = db.session.query(News).order_by(News.id.desc()).all()
    db.session.commit()
    return render_template("user_home.html", news=news, active_orders=active_orders, user=current_user)

@views.route('/test-order', methods=['GET', 'POST'])
@login_required
def test_order():
    items = Menu.query.all()
    '''# delete any empty orders. Everytime we go to the order page, we create a new order object, so we should delete
    # the uncompleted order objects to not have a bunch of empty orders in the db.
    error_orders = Order.query.filter(Order.user_id == current_user.id).filter(Order.total == 0).delete()
    new_order = new_order = Order(user_id=current_user.id, taxes=0, total=0)
    db.session.add(new_order)
    db.session.commit()'''
    return render_template("order2.html", items=items, user=current_user)

# delete_this this function
@views.route('/order', methods=['GET', 'POST'])
@login_required
def order():
    # test
    # back then orders would be submitted before I added any requirements for an order to be submitted
    # # this would just delete any empty orders that made it through but there shouldn't be anymore
    # this should get deleted
    error_orders = Order.query.filter(Order.user_id == current_user.id).filter(Order.total == 0).all()
    for order_del in error_orders:
        db.session.delete(order_del)
    db.session.commit()
    # create order
    # we need to pass new_item to access its order id
    # MAYBE ITEMS=[] EMPTY LIST WILL FIX BUG WHERE IT SHOWS ITEMS WHEN YOU CLICK IN AND OUT OF ORDER PAGE
    # TO ANOTHER PAGE THE TOTAL WILL BE 0 BUT IT WILL STILL SHOW PREVIOUS ITEMS
    new_order = Order(user_id=current_user.id, taxes=0, total=0)
    db.session.add(new_order)
    db.session.commit()
    # if user goes to order page and tries to submit right away refreshes page
    if request.method == "POST":
        flash('Empty Order', category="error")
        return redirect(url_for('views.order'))
    user = User.query.filter(User.email == 'headChef@gmail.com').first()
    items = Menu.query.filter_by(user_id=user.id).order_by(Menu.name).all()
    return render_template("order.html", items=items, new_order=new_order, user=current_user)


# this function is to add an item to the order
# it is set up to add an item based on the different ways an item could be added
@views.route('/add-to-order/<int:order_id>', methods=['GET', 'POST'])
def add_to_order(order_id):
    # these variables decide which part of the function is going to execute
    # quantity decides how much of an item gets added
    quantity = request.form.get('quantity')
    # dish accommodation is gluten free/vegan/regular
    dish_accommodation = request.form.get('dish_accommodation')
    # complete order is for when complete order button on order page is press
    complete_order = request.form.get('complete_order')

    # just in case someone enters spaces but no digits
    # if quantity == none then can't strip usually when fresh order this occurs
    # in both of these cases it would signify that just one item is going to be added to an order
    if quantity != None:
        if quantity.strip() == '':
            quantity = 1
    if quantity == None:
        quantity = 1

    # I added to delete by quantity feature in this functin it seemed easier to implement it in this function at the time
    # might look into making it its own function or at least changing the name of this function to edit_order()
    delete_quantity = request.form.get('delete_quantity')
    if delete_quantity == "":
        delete_quantity = 1
    # if delete_quantity is not None then that means something was added to the del by quantity field and a user is
    # trying to delete something from the order
    # I entered an input for both add and delete by quantity fields in the order page and the one that gets processed is
    # depends on the button you press, so you can't add and delete by quantity at the same time
    if request.method == "POST" and delete_quantity is not None:
        # itemId2 is just the id of the item, but I named it itemId2 because itemId was already in use
        item_id2 = request.form.get('itemId2')
        # item by id and current order by id in order to delete item in the order
        item = Menu_order.query.filter(Menu_order.id == item_id2).first()
        new_order = Order.query.filter(Order.id == order_id).first()
        # convert delete_quantity to int in order to loop that many times and delete item
        delete_quantity = int(delete_quantity)
        # if page is refreshed after deleting something then an errors occurs because item becomes None type
        # and tmp_name = item.name[:] causes and issue
        # so in that case refresh page
        if item is None:
            user = User.query.filter(User.email == 'headChef@gmail.com').first()
            items = Menu.query.filter_by(user_id=user.id).order_by(Menu.name).all()
            return render_template('order.html', items=items, new_order=new_order, user=current_user)
        # if you delete the item then you can't use it to delete other items so make tmp variable
        tmp_name = item.name[:]
        # count_lst is to get the name of every single item in the order and count how many the specific item we are
        # trying to delete shows up. This could have been changed to only append item  to count lst if it matches
        # item.name, and then you wouldn't have to append all the items names
        count_lst = []
        for item_tmp in new_order.items:
            count_lst.append(item_tmp.name)
        # if count is less the amount of items the user is trying to delete then flash a msg and refresh page
        # they are trying to delete more than there is
        count = count_lst.count(item.name)
        if count < delete_quantity:
            flash('Delete quantity greater than the amounts of items in order', category="error")
            user = User.query.filter(User.email == 'headChef@gmail.com').first()
            items = Menu.query.filter_by(user_id=user.id).order_by(Menu.name).all()
            return render_template('order.html', items=items, new_order=new_order, user=current_user)

        # the first loop aims to delete something every loop and runs x(whatever user entered for delete_quantity) amount of times
        # the second for loop, loops through the items in the order and checks if the name matches the name of the item
        # that was selected by the id. It then deletes the item and subtracts it from order total and breaks the loop
        # we break the inner loop because we only want to delete x amount of items.
        for x in range(delete_quantity):
            for item_compare_delete in new_order.items:
                if tmp_name == item_compare_delete.name:
                    # price converted to float because price is float type in db but also it is a string when entered by user
                    new_order.total = new_order.total - float(item_compare_delete.price)
                    db.session.delete(item_compare_delete)
                    db.session.commit()
                    break
        # calculate taxes and add to total then commit and refresh page to show updated order. Flashes a msg confirming delete
        new_order.taxes = new_order.total * 0.08
        db.session.commit()
        flash('ITEMS DELETED!', category="success")
        user = User.query.filter(User.email == 'headChef@gmail.com').first()
        items = Menu.query.filter_by(user_id=user.id).order_by(Menu.name).all()
        return render_template('order.html', items=items, new_order=new_order, user=current_user)

    # if you want to add by quantity
    # complete order is not true
    # could have a variable here specifically for when you want to add to order, but I managed without
    # will only add to order when add to order button is selected b/c complete_order will be None type
    if request.method == "POST" and complete_order != 'TRUE':
        # add to order
        # change how you add an item I think
        item_id = request.form.get('itemId')
        item = Menu.query.filter(Menu.id == item_id).first()
        new_order = Order.query.filter(Order.id == order_id).first()
        # create a copy of the itme to add in the order relationship list
        # has to be a copy because menu items are unique in the list
        # run x amount of times based on the quantity
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
            # calculate order total and commit
            new_order.total = new_order.total + float(item_copy.price)
            db.session.add(item_copy)
            db.session.commit()
        # calculate taxes and refresh page to show updated order
        new_order.taxes = new_order.total * 0.08
        db.session.commit()
        flash('Item added.', category="success")
        user = User.query.filter(User.email == 'headChef@gmail.com').first()
        items = Menu.query.filter_by(user_id=user.id).order_by(Menu.name).all()
        return render_template('order.html', items=items, new_order=new_order, user=current_user)
    # will only submit order when submit order button is selected because complete_order is set to TRUE in that case only
    if request.method == "POST" and complete_order == 'TRUE':
        # get order and pass it the users name, comment, and set it to active to show up in Chefs view order page
        new_order = db.session.query(Order).order_by(Order.id.desc()).first()
        new_order.name = current_user.first_name
        new_order.comment = request.form.get('comment')
        new_order.is_active = "Active"
        flash('Order Submitted!!!', category="success")
        # redirect to user home to view active orders and flash success msg
        db.session.commit()
        return redirect(url_for('views.user_home'))


# renders views order page for chef to see active orders. Active order are orders that are still being prepared
# inactive orders are orders that were completed. In this page inactive orders can be cleared. The idea behind that
# feature is that if it is a new day then you might not want to see inactive orders from the day before
# It could be useful to add feature for chef to see all orders and filter by specific user or date etc. This is going on
# the to do list
@views.route('/view-orders', methods=['POST', 'GET'])
def view_orders():
    active_orders = Order.query.filter(Order.is_active == 'Active').all()
    inactive_orders = Order.query.filter(Order.is_active == 'Inactive').all()
    return render_template('view_orders.html', active_orders=active_orders, inactive_orders=inactive_orders,
                           user=current_user)


# function to deactivate active orders
# it just fetches the order by id and sets the order is_active variable to Inactive and refreshes page
@views.route('/deactivate-order/<int:id>', methods=['POST', 'GET'])
def deactivate_orders(id):
    order = Order.query.filter(Order.id == id).first()
    order.is_active = "Inactive"
    active_orders = Order.query.filter(Order.is_active == 'Active').all()
    inactive_orders = Order.query.filter(Order.is_active == 'Inactive').all()
    db.session.commit()
    return render_template('view_orders.html', active_orders=active_orders, inactive_orders=inactive_orders,
                           user=current_user)


# this sets all inactive orders to clear so they don't appear in view orders and takes up space
@views.route('/clear-inactive-orders', methods=['POST', 'GET'])
def clear_inactive_orders():
    inactive_orders = Order.query.filter(Order.is_active == 'Inactive').all()
    for item in inactive_orders:
        item.is_active = "clear"
    db.session.commit()
    active_orders = Order.query.filter(Order.is_active == 'Active').all()
    inactive_orders = Order.query.filter(Order.is_active == 'Inactive').all()
    return render_template('view_orders.html', active_orders=active_orders, inactive_orders=inactive_orders,
                           user=current_user)


# this is a feature for the user to order a previous order again
# just fetches the order by id and copies the old order details to a new order, and it can be edited and resubmitted
@views.route('/corder-again/<int:id>', methods=['GET', 'POST'])
def order_again(id):
    # change to request.method == 'GET'
    if request.method != 'POST':
        # there were empty orders being submitted and this was a test. Is now obsolete
        error_orders = Order.query.filter(Order.is_active == None).all()
        # fetch old order to copy info over
        old_order = Order.query.filter(Order.id == id).first()
        # set the new orders taxes and total to the old orders taxes and total to display in the order html
        new_order = Order(user_id=current_user.id, taxes=old_order.taxes, total=old_order.total)
        db.session.add(new_order)
        db.session.commit()

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
            db.session.commit()

        # db.session.commit()
        user = User.query.filter(User.email == 'headChef@gmail.com').first()
        items = Menu.query.filter_by(user_id=user.id).order_by(Menu.name).all()
        return render_template("order.html", items=items, new_order=new_order, user=current_user)
    # submit order if nothing is changed about the order. and the sets order to active, adds comment and user name
    # ,and redirects to user home
    if request.method == "POST":
        new_order = db.session.query(Order).order_by(Order.id.desc()).first()
        new_order.name = current_user.first_name
        new_order.comment = request.form.get('comment')
        new_order.is_active = "Active"
        new_order.taxes = new_order.total * 0.08
        flash('Order Submitted!!!', category="success")
        db.session.commit()
        active_orders = Order.query.filter(Order.user_id == current_user.id).filter(Order.is_active == "Active").all()
        return redirect(url_for('views.user_home'))


# a function to create news post and refreshes create news page
@views.route('/create-news', methods=['GET', 'POST'])
@login_required
def create_news():
    # just gets form info and creates a post
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


# deletes news post using java and jsonify
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


@views.route('/list-of-items', methods=['POST', 'GET'])
def list_of_items():
    items_list = json.loads(request.data)
    items_list = items_list['values']
    new_order = Order()
    new_order.user_id = current_user.id
    new_order.is_active = 'Active'
    new_order.total = items_list[1]['total']
    new_order.taxes = items_list[2]['taxes']
    new_order.comment = items_list[3]['comment']
    new_order.name = current_user.first_name
    db.session.add(new_order)
    db.session.commit()
    items = items_list[0]['listOfItem'].split('#')
    for item in items:
        tmp_item = item.split('*')
        for quantity in range(int(tmp_item[1])):
            menu_item = Menu.query.filter_by(id=tmp_item[2]).first()
            tmp_item_object = Menu_order()
            tmp_item_object.name = tmp_item[0]
            tmp_item_object.price = menu_item.price
            tmp_item_object.description = menu_item.id
            tmp_item_object.order_id = new_order.id
            db.session.add(tmp_item_object)
            db.session.commit()
    return jsonify({})

@views.route('/dud', methods=['POST'])
def dud():
    print('dud')
    return jsonify({})


@views.route('/testOrderAgain/<string_list>/<total>/<taxes>', methods=['POST', 'GET'])
def testOrderAgain(string_list, total, taxes):
    print(string_list, total, taxes)
    print('before the return')
    items = Menu.query.all()
    new_order = [string_list + '^' + total + '^' + taxes]
    return render_template("order2.html", items=items, new_order=new_order, user=current_user)


@views.route('/this-is-test', methods=['POST'])
def this_is_test():
    print('were in the test func')
    var1 = json.loads(request.data)
    var1 = var1['vars']
    print(var1)
    return jsonify({})


# this is function is to delete an item from the menu. It just finds the item by id and then deletes it. It also deletes
# the image associated with that item from the images directory
@views.route('/delete-menu-item/<int:item_id>', methods=['POST'])
def delete_menu_item(item_id):
    item = Menu.query.filter_by(id=item_id).first()
    filename = item.name + '.jpg'
    os.unlink(os.path.join(target, filename))
    db.session.delete(item)
    db.session.commit()
    flash('Item deleted!', category="success")
    return redirect(url_for('views.edit_menu'))


# this function is to edit any item from the menu
# it gets an id from the button when the form is submitted it has an action for this decorator. Then whatever values
# were inside the input fields are pulled and overwritten.
@views.route('/edit-menu-item/<int:item_id>', methods=['POST'])
def edit_menu_item(item_id):
    # find the item by its id
    item = Menu.query.filter_by(id=item_id).first()
    # get all the user input values
    item.name = request.form.get('name')
    # we have to rename the image associated with this item if the name changes
    # we change the name of the image before saving to 'images' folder because some images have really long names
    # and naming image after the food it is associated with makes it easier to find in the images folder
    os.renames(target + item.item_image, target + item.name + '.jpg')
    item.price = request.form.get('price')
    item.description = request.form.get('description')
    item.gluten_free = request.form.get('gluten_free')
    item.vegan = request.form.get('vegan')
    item.menu_type = request.form.get('menu_type')
    tmp_file = request.files.get('file')
    item.item_image = item.name + '.jpg'
    # if filename empty then do nothing because user doesn't want to change the item image
    if tmp_file.filename != '':
        os.unlink(os.path.join(target, item.item_image))
        # else change the image
        filename = item.name + '.jpg'
        destination = "/".join([target, filename])
        tmp_file.save(destination)
        # save the image name to item.item_image to call it later when it is needed to be displayed
        item.item_image = filename
    db.session.commit()
    # return to edit menu html
    flash('Item edited!', category="success")
    return redirect(url_for('views.edit_menu'))

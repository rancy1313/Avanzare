from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, send_from_directory
from flask_login import login_required, current_user
from .models import Menu, User, Order, Menu_order, News
from . import db
import json
import os

# for image uploading
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

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

# this function just returns the a specific image based on the name from the directory
@views.route('/upload/<filename>')
def send_image(filename):
    return send_from_directory('images', filename)


# this function is to add a menu item if it is a post method and load edit menu html if get method
# any user can type http://127.0.0.1:5000/add-menu-item to get to this page so it should be changed to only render
# if user is headChef
# however, only items made by headChef are ever passed through to the html, so items made by a different user won't
# ever be displayed
@views.route('/add-menu-item', methods=['GET', 'POST'])
@login_required
def add_menu_item():
    if request.method == 'POST':
        name = request.form.get('name')
        # make sure no uses any weird characters or tries to do anything funny
        special_chars = '`~@#^*()-_=+|[]{};:<>\"\\/'
        for char in special_chars:
            if char in name:
                flash('No special chars allowed in item names (except \' ).', category="error")
                return redirect(url_for('views.add_menu_item'))
        price = request.form.get('price')
        try:
            # if price can't be converted to float then that means there are chars being used that are not digits
            # might be a better way to implement this
            float(price)
        except:
            flash('Only enter digits for price.', category="error")
            return redirect(url_for('views.add_menu_item'))
        # just a price check. I think this can be changed improved upon a lot by adding a minimum price point
        # based on the menu type. For example, a menu item that is a PIZZA menu type would not cost below $10
        # refreshes page if price == 0
        if price == '0':
            flash('No free items.', category="error")
            return redirect(url_for('views.add_menu_item'))
        # convert str type price to format it in $0.00 format
        price = "{:,.2f}".format(float(price))
        # fetching description to make sure no special chars in it except for apostrophe
        description = request.form.get('description')
        for char in special_chars:
            if char in description:
                flash('No special chars allowed in description (except \' ).', category="error")
                return redirect(url_for('views.add_menu_item'))
        # get extra item info from form
        gluten_free = request.form.get('gluten_free')
        vegan = request.form.get('vegan')
        menu_type = request.form.get('menu_type')
        # check if there is any item in Menu that already has the name that was entered by chef
        menu_item = Menu.query.filter_by(name=name).first()
        # create path for image storing
        target = os.path.join(APP_ROOT, 'images/')

        # if path doesn't exist create it
        if not os.path.isdir(target):
            os.mkdir(target)
        # fetch file submitted by chef
        file_tmp = request.files.getlist('file')
        # if menu_item exists then that means the item name is taken already
        if menu_item:
            flash('This dish name already exists.', category="error")
        #elif len(description) > 10000:
            #flash('Description must be less than 10,000 characters.', category="error")
        # this makes sure that an image is submitted when creating an item else an error is raised
        # if filename == "" then that means no file was submitted
        elif file_tmp[0].filename == "":
            flash('No image was selected.', category="error")
        else:
            # add the item with info entered by chef and commit
            new_menu_item = Menu(name=name, price=price, description=description, menu_type=menu_type, gluten_free=gluten_free, vegan=vegan, user_id=current_user.id)
            db.session.add(new_menu_item)
            db.session.commit()
            #login_user(user, remember=True)
            # this saves the image file that was submitted to the "images" folder
            # this doesn't have to be in a for loop because only one images should be submitted for an item
            # however it is in a for loop because I was thinking about making it so the user can view multiple photos
            # associated to a food item. This loop might need to be changed if I don't come back and add that feature
            for file in request.files.getlist('file'):
                filename = name + '.jpg'
                destination = "/".join([target, filename])
                file.save(destination)
            # refresh page to show new item added in edit menu html
            flash('New item added to menu!!!', category="success")
            user = User.query.filter(User.email == 'headChef@gmail.com').first()
            items = Menu.query.filter_by(user_id=user.id).order_by(Menu.name).all()
            return render_template("edit_menu.html", items=items, user=current_user)
        # this is needed just in case to show items just in case add item gets error
    # technically all items from Menu are created by chef, so I can just fetch it all from Menu
    # i had it like this because originally I was going to have one class for Menu and Menu_order
    # originally I would have needed to search by Chef's user id. Since I separated both then
    # fetching by chef's user id becomes pointless. However, I do not want to change this because
    # I might combine both Menu classes and then searching by chef's Id might be necessary
    user = User.query.filter(User.email == 'headChef@gmail.com').first()
    items = Menu.query.filter_by(user_id=user.id).order_by(Menu.name).all()
    return render_template("edit_menu.html", items=items, user=current_user)


@views.route('/user_home', methods=['GET', 'POST'])
@login_required
def user_home():
    # this function is to load the users home page that shows their active orders and past orders
    # active orders are orders that are still in the progress of being made
    # sometimes when the page is refreshed while on the order page
    # or everytime the order page is clicked it will create a new order
    # ,so I will delete those orders here
    # issue was solved a while ago, so this technically shouldn't be here. Might delete this soon.
    error_orders = Order.query.filter(Order.user_id == current_user.id).filter(Order.is_active == None).delete()
    error_orders = Order.query.filter(Order.user_id == current_user.id).filter(Order.total == 0).delete()
    db.session.commit()
    active_orders = Order.query.filter(Order.user_id == current_user.id).filter(Order.is_active == "Active").all()
    # user can view all restaurant's news in user home. This could be changed to show limited random news like in
    # the featured section of the start page, but I'm assuming that there wouldn't be that many news
    # coming from a small family restaurant
    news = db.session.query(News).order_by(News.id.desc()).all()
    db.session.commit()
    return render_template("user_home.html", news=news, active_orders=active_orders, user=current_user)


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

# function to delete an item from menu using java and jsonify. could be done without like i did with delete by quantity
# in add_to_order function. I liked trying both ways.
@views.route('/delete-item', methods=['POST', 'GET'])
def delete_item():
    # get item id and item data and then delete item
    item = json.loads(request.data)
    itemId = item['itemId']
    item = Menu.query.get(itemId)
    # delete img associated with menu item b/c new dishes with same name could be added and that could cause issues or
    # take up space in the image folder
    filename = item.name + '.jpg'
    target = os.path.join(APP_ROOT, 'images/')
    os.unlink(os.path.join(target, filename))
    #  checks if item exists might not be a necessary test
    if item:
        if item.user_id == current_user.id:
            db.session.delete(item)
            db.session.commit()
            flash('ITEM DELETED!', category="success")
    else:
        flash('error!', category="error")
    return jsonify({})


# this function is to edit an item from the menu
# if GET method then will render edit_menu_item.html. I made so that you go to another page with the info of the item
# you want to edit. Then you can change whatever and it updates the info and commits
@views.route('/edit_redirect/<int:id>', methods=['GET', 'POST'])
def edit_redirect(id):
    # finds item by the id passed from the edit button
    item = Menu.query.filter(Menu.id == id).first()
    if request.method == 'POST':
        # gets new item info and checks if any special chars are in it
        # if no new info is brought then it overwrites with the same info as before
        name = request.form.get('name')
        special_chars = '`~!@#$%^*()-_=+|[]{};:<>\"\\/'
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
        # two cases for images.
        # 1. Old img is kept and needs to make sure img name matches item name because images are displayed by matching names
        # 2. new img is selected for item and need to delete old img to replace it
        # target is root
        target = os.path.join(APP_ROOT, 'images/')
        if not os.path.isdir(target):
            os.mkdir(target)

        for file in request.files.getlist('file'):
            # if filaname empty then no new image was submitted. If it is not empty then new image was submitted
            if file.filename == "":
                # tmp is the name of the img someone changes the name of the item and does not change the img
                # the imgs are not connected by a db and are connected by name so if the item name changes then the img name needs to change
                # tmp = name is the new name/ if the name is kept the same then nothing gets overwritten
                # tmp2 is the old item name
                tmp = target + name + '.jpg'
                tmp2 = target + item.name + '.jpg'
                os.renames(tmp2, tmp)
            else:
                # if a new image is selected then the old one should be deleted, so it doesn't take up space
                filename = item.name + '.jpg'
                target = os.path.join(APP_ROOT, 'images/')
                os.unlink(os.path.join(target, filename))
                # save new img after
                filename = name + '.jpg'
                destination = "/".join([target, filename])
                file.save(destination)
        # the item info is always overwritten but if the nothing was changed then it overwrites with the old info
        item.name = name
        item.price = price
        item.description = description
        item.menu_type = menu_type
        item.gluten_free = gluten_free
        item.vegan = vegan
        # flash success msg, commit, and redirect to edit menu with updated info
        flash('Item has been edited!!!', category="success")
        db.session.commit()
        return redirect(url_for('views.add_menu_item'))
    return render_template('edit_menu_item.html', item=item, user=current_user)

# renders views order page for chef to see active orders. Active order are orders that are still being prepared
# inactive orders are orders that were completed. In this page inactive orders can be cleared. The idea behind that
# feature is that if it is a new day then you might not want to see inactive orders from the day before
# It could be useful to add feature for chef to see all orders and filter by specific user or date etc. This is going on
# the to do list
@views.route('/view-orders', methods=['POST', 'GET'])
def view_orders():
    active_orders = Order.query.filter(Order.is_active == 'Active').all()
    inactive_orders = Order.query.filter(Order.is_active == 'Inactive').all()
    return render_template('view_orders.html', active_orders=active_orders, inactive_orders=inactive_orders, user=current_user)

# function to deactivate active orders
# it just fetches the order by id and sets the order is_active variable to Inactive and refreshes page
@views.route('/deactivate-order/<int:id>', methods=['POST', 'GET'])
def deactivate_orders(id):
    order = Order.query.filter(Order.id == id).first()
    order.is_active = "Inactive"
    active_orders = Order.query.filter(Order.is_active == 'Active').all()
    inactive_orders = Order.query.filter(Order.is_active == 'Inactive').all()
    db.session.commit()
    return render_template('view_orders.html', active_orders=active_orders, inactive_orders=inactive_orders, user=current_user)

# this sets all inactive orders to clear so they don't appear in view orders and takes up space
@views.route('/clear-inactive-orders', methods=['POST', 'GET'])
def clear_inactive_orders():
    inactive_orders = Order.query.filter(Order.is_active == 'Inactive').all()
    for item in inactive_orders:
        item.is_active = "clear"
    db.session.commit()
    active_orders = Order.query.filter(Order.is_active == 'Active').all()
    inactive_orders = Order.query.filter(Order.is_active == 'Inactive').all()
    return render_template('view_orders.html', active_orders=active_orders, inactive_orders=inactive_orders, user=current_user)

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


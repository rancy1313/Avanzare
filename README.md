# Intro

This is a simple coding project I started to get some experience on software development. The project is about a 
website/app for my dad's restaurant. The restaurant is called Avanzare, and I got his permission to do this project. 

# Start Page

For now, the website/app has the feature to view a menu as the start page. The menu displays all the menus of the 
restaurant, and each item from the menu has a name, price, description, image, and dish accommodation. The dish 
accommodation lets a user know if a dish is available to be ordered in Gluten free or vegan. There is also a drop-down 
menu on the bottom that displays a sorted version of menu for Gluten free/vegan only options. There is also a featured 
section on the top of the page that displays up to 5 random news posts from the chef. 

# Login/Sign up

The user is able to create an account to make orders under their name and to view past orders they have made. There are
some specifications for user creating accounts, such as password length(has to be greater than 7 chars) and character
restrictions(@#$&!). After making an account, the user is directed to the login page. Then they are directed to their
personalized home page.

# Home Page

Every user's home page displays their orders. At the top, it shows all there active orders from newest to oldest. Active
orders are orders that have not been completed by the chef yet. Once the chef ha completed the orders, they can set that 
order to inactive. Then that order will show up on the bottom of their home page under "Past Orders." There is also a 
counter next to the headers that lets the user know how many orders have been made that are either active/inactive. Then 
in the middle of the page, there is a section that displays news from the restaurant. The chef has the ability write 
little news posts that will show up in every user's home page. These news posts have three categories(sale, new item, 
and important). They are sorted under their own news type. Lastly, there is a feature for the user to reorder any order 
again. There is a button under every order called "Order Again." If the user clicks the button then the info from that 
order will be transferred to a new order and can be resubmitted or edited further. There is a lot of potential for this 
page to improve further, such as a filter for the orders.

# Orders

Every user with an account has the ability to make an order under their name through the order page. There, it displays
the user's current order and a menu. The user can add an item by quantity and add an accommodation if available. At the
top, the user's current order details are displayed(item name and quantity, taxes, and total + taxes). There is an input
field next to each item, so that the user can delete by quantity, and there is an option to add a comment or request for
each order. There is currently no max amount of what a user can add because my dad said they will finish any order that 
is made no matter how large. Realistically, there has to be a limit, but it is something I'll come back to in the future
. After the user submits an order, they are redirected to their homepage.

# Head Chef Account

With the Head Chef account, you can edit the menu on the edit menu page. On that page, there is input fields for the 
item's name, price, description, image, menu type, and dish accommodation availability. There are specifications for an 
adding an item to menu(all input fields must have a value, price has to be digits, and limited special chars in 
name/description). Under the submission field is the menu, and it gets refreshed after every change. There is also the 
option to edit an item that was submitted in case of error. When the edit button is clicked, the item's info is brought 
a new page where the Head Chef can make changes to any of the item's details. 

### View Orders

The chef also has the feature to see all orders that have been made. Admittedly, this page needs a little more work, 
and it is something that I plan on adding more to in the future. For now, the chef can view all active orders, and the 
orders display the time the order was made, the users name, and the all the order's details. Once the chef has completed
an order, they can set the order to inactive. Then, the order will be displayed in the inactive section of the page. The
chef can also clear all inactive orders, and the purpose for that is assuming the next day he would want to only see 
orders from that day. Currently, there is no way to see orders that have been cleared, so I plan on adding some feature 
to view all orders, sort/filter by user/date/etc..., and some way to display data of orders. 

### Create News

I thought this would be a good way for the chef to make important announcements for sales, new items, and special news
. This feature can be improved further by adding the ability for the chef to include an image for the news post and 
ability to edit a news post. The chef can also delete any news post they want. Currently, the news posts are displayed
on the featured section of the start page and on all the users' home pages.

# To do list

- filter feature to filter orders by specific details
- go back and make some technical fixes(optimization)
- feature to let the head chef view accounts
- there is currently no payment method option(I didn't add this because there were so many ways to design this)
- search menu by text(item name, ingredient)
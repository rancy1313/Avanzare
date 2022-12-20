// this function deletes news posts and redirects to create news
function deleteNewsPost(news_postId) {
  fetch("/delete-news-post", {
    method: "POST",
    body: JSON.stringify({ news_postId: news_postId }),
  }).then((_res) => {
    window.location.href = "/create-news";
  });
} // this will refresh the page after deletes


/* This function makes a list of the items that the user is trying to submit from their order and passes it to the
   pass list to backend function. */
function makeList() {
    // gets total to make sure user isn't trying to submit an empty order
    total = document.getElementById('displayed_total').innerText;
    if (total != 0) {
        let string_list = '';
        // get the table from order page with the order info
        const table = document.getElementById('actual_order');
        // every row (mines the heading row) has an item/quantity/price
        var table_rows = table.getElementsByTagName('tr');
        // loop through every row
        for (let i = 1; i < table_rows.length; i++) {
            // get each td tag in the row to get the name/quantity/price
            var table_data = table_rows[i].getElementsByTagName('td');
            // loop through td tag
            for (let x = 0; x < table_data.length; x++) {
                // we want 0/name, 1/quantity, and 4/item_id
                if (x == 0 || x == 1 || x == 4) {
                    // if x == 4 the we do not want to add a * because a # is gonna be added instead to separate row
                    if (x != 4) {
                        string_list += table_data[x].innerText + '*';
                    } else {
                        string_list += table_data[x].innerText;
                    }
                }
            }
            // add # to separate the row
            if (i != table_rows.length - 1) {
                string_list += "#"
            }
        }
        // get taxes
        taxes = document.getElementById('displayed_taxes').innerText;
        // get comments
        comment = document.getElementById('comment').value;
        // time to pass info to the back end
        fetch("/complete-order", {
            method: "POST",
            body: JSON.stringify({ values: [{ string_list: string_list }, { total: total }, { taxes: taxes }, { comment: comment }] }),
        }).then((_res) => {
            window.location.href = "/user-home";
        });
    }
}

// this function takes the info of the past order that the user is trying to order again and sends it to back end order
// again function
function orderAgain(order_id) {
    let string_list = '';
    // get the specific table that the has the past order info
    const order_table = document.getElementById(`table_${order_id}`);
    // get each row(minus header row) that shows each item's info
    var table_rows = order_table.getElementsByTagName('tr');
    // loop through the rows
    for (let i = 1; i < table_rows.length; i++) {
        // each td represents an item detail such as name/quantity/price/item_id
        var table_data = table_rows[i].getElementsByTagName('td');
        for (let x = 0; x < table_data.length; x++) {
            // instead of putting an * for the final element we put a ^
            if (x != 3) {
                // each * separates the item's info
                string_list += table_data[x].innerText + '*';
            } else {
                string_list += table_data[x].innerText;
            }
        }
        // each ^ separates the items
        if (i != table_rows.length - 1) {
            string_list += "^"
        }
    }
    // send the info to the backend
    window.location.href = `/orderAgain/${string_list}`;
}

// this function is called when the page is loaded. It is loading a new order with the details of the past order
function loadNewOrder(new_order) {
    // new_order is a list with a string inside. The string has the order's info
    // split new_order string by ^ to get every row. A row has item/quantity/price
    const new_order_items = new_order[0].split('^');
    // loop through each row
    for (let i = 0; i < new_order_items.length; i++) {
        // split to get each item's info
        const individual_item = new_order_items[i].split('*')
        // set price
        let price = individual_item[2].slice(1, individual_item[2].length)
        price = price / individual_item[1];
        // get the order total to update it
        order_total = document.getElementById('total').value;
        // call add to order function to add each row to the table
        addToOrder(individual_item[1], individual_item[3], individual_item[0], price, 'REGULAR', order_total)
    }
}

// this will load the dates of the orders in a better format
function loadDates(lst_dates) {
    for (let i = 0; i < lst_dates.length; i++) {
        var tag = lst_dates[i][0].toString() + '_tag';
        var tmp_date = new Date(lst_dates[i][1])
        document.getElementById(tag).innerHTML = tmp_date;
    }
}

// function to show edit page under item that chef is trying to edit
function blueprint(item_id) {
    /* get divs only_one because. I assigned div only one to divs containing the blueprint html, and only one of those
       blueprints should be displayed at a time. Thus, we get all the divs with only one and we set them to hidden.*/
    const tmp_divs = document.getElementsByClassName('only_one');
    /* we get all the edit buttons to make sure they are all displayed because if user clicks on a another edit button
       without closing the previous edit, then the closeBlueprint function is never called and never makes the button
       visible again */
    const buttons = document.getElementsByClassName('show');
    for (let i = 0; i < tmp_divs.length; i++) {
        // set all divs to hidden
        tmp_divs[i].setAttribute('hidden', true);
    }
    for (let i = 0; i < buttons.length; i++) {
        // make all buttons visible
        buttons[i].removeAttribute('hidden');
    }
    // get the edit page for the user is trying to edit
    const tmp_hidden = document.getElementById('hidden_' + item_id);
    // remove hidden attribute to make blueprint visible
    tmp_hidden.removeAttribute('hidden');
    // hide the edit button because the edit page is already present
    const edit_button = document.querySelector('#edit_' + item_id);
    edit_button.setAttribute('hidden', true);
}

// close the edit page blueprint
function closeBlueprint(item_id) {
    // get the edit page for the item being edited
    const edit_page = document.getElementById('hidden_' + item_id);
    // hide it
    edit_page.setAttribute('hidden', true);
    // make the edit button visible again
    const edit_button = document.getElementById('edit_' + item_id);
    edit_button.removeAttribute('hidden');
}

// this function is to add by quantity from the user's order
function addToOrder(quantity, item_id, item_name, item_price, item_accommodation, total) {
    // sure quantity is not 0 so user doesn't try to add 0 amounts of an item to the order
    // make sure quantity isn't an empty string or it will try to add 0 amounts of the item to the order. This happens
    // if the button was pressed and there was no input in the quantity field.
    if (quantity !== '' && quantity !== 0) {
        if (item_accommodation !== 'REGULAR') {
            item_name = item_accommodation + ' ' + item_name;
        }
        let tmp_price = item_price * quantity;
        // we get the row by item name because I want to keen items that are the same but have different accommodations
        // separate.
        const table_row = document.getElementById(`row_${item_name}`);
        // if table is null then that item has not been ordered yet and we can make a row for it
        if (table_row === null) {
            // get table
            const order = document.getElementById('actual_order');
            // create a new row for the item
            const tmp_item = document.createElement('tr');
            tmp_item.setAttribute('id', `row_${item_name}`);
            // this is to format the delete by quantity field for each item
            tmp_item.innerHTML = `
                <td>${item_name}</td>
                <td >${quantity}</td>
                <td>$${tmp_price.toFixed(2)}</td>
                <td><input style="width: 25%"
                           type="number" min="1" step="1"
                           id="delete_quantity_${item_name}"
                           name="delete_quantity"
                           placeholder="Quantity"/>
                    <button class="btn-del-order" onclick="removeFromOrder(document.getElementById('delete_quantity_${item_name}').value,
                            ${item_id}, '${item_name}', ${item_price}, document.getElementById('total').value)">Delete</button>
                </td>
                <td hidden>${item_id}</td>
                    `;
            // add the row to the order
            order.appendChild(tmp_item);
            total = parseFloat(total) + parseFloat(tmp_price.toFixed(2));
            // change the p tag to display the total
            document.getElementById('total').innerText = total.toFixed(2);
            // change the textarea to reset the value of total
            document.getElementById('displayed_total').innerText = total.toFixed(2);
            // set taxes
            document.getElementById('displayed_taxes').innerText = (parseFloat(total.toFixed(2)) * 0.0625).toFixed(2);
        } else {
            // the item has been ordered already and we just want to add to the price and quantity of that row
            var descendants = table_row.getElementsByTagName('*');
            let tmp = descendants[2].innerText.slice(1, descendants[2].innerText.length);
            descendants[1].innerText = parseInt(quantity) + parseInt(descendants[1].innerText);
            descendants[2].innerText = '$' + (parseFloat(tmp_price) + parseFloat(tmp)).toFixed(2);
            total = parseFloat(total) + parseFloat(tmp);
            // change the p tag to display the total
            document.getElementById('total').innerText = total.toFixed(2);
            // change the textarea to reset the value of total
            document.getElementById('displayed_total').innerText = total.toFixed(2);
            // set taxes
            document.getElementById('displayed_taxes').innerText = (parseFloat(total.toFixed(2)) * 0.0625).toFixed(2);
        }
    }
    // clear the quantity fields
    const quantity_reset = document.getElementById('quantity_' + item_id);
    quantity_reset.value = "";
}

// this function is to remove by quantity from the user's order
function removeFromOrder(quantity, item_id, item_name, item_price, total) {
    // sure quantity is not 0 so user doesn't try to add 0 amounts of an item to the order
    // make sure quantity isn't an empty string or it will try to add 0 amounts of the item to the order. This happens
    // if the button was pressed and there was no input in the quantity field.
    if (quantity !== '' && quantity !== 0) {
        // tmp_price is the total amount that the user wants to reduce
        let tmp_price = item_price * quantity;
        // get the table row my matching item name id
        const table_row = document.getElementById(`row_${item_name}`);
        // fetch td tags inside of the row
        var descendants = table_row.getElementsByTagName('*');
        // slice the descendants[2](item price) because it is in $0.00 format we need 0.00 type to do math
        let tmp = descendants[2].innerText.slice(1, descendants[2].innerText.length);
        // descendants[1] is the quantity of the object
        descendants[1].innerText = parseInt(descendants[1].innerText) - parseInt(quantity);
        descendants[2].innerText = '$' + (parseFloat(tmp) - parseFloat(tmp_price)).toFixed(2);
        // we reset tmp after doing the subtraction above to get the new price total
        tmp_item_price_total = descendants[2].innerText.slice(1, descendants[2].innerText.length);
        // If checks if the total is equal to zero or below zero to remove the row from the table.
        // If tmp is below zero, then the user tried to remove more than what was ordered, so we just remove it all
        if (tmp_item_price_total <= 0) {
            // fetch the order to remove the row
            const order = document.getElementById('actual_order');
            // remove row from order
            order.removeChild(table_row);
            // calculate new total. If user tried to delete by more than what was ordered then we have to offset the difference
            // descendants[1] that has the quantity will be negative so we multiply by -1 to make it positive and then
            // we multiply it by the item's price to add back what the user didn't order
            total = parseFloat(total) - parseFloat(tmp_price) + ((parseFloat(descendants[1].innerText) * -1) * parseFloat(item_price));
            document.getElementById('total').innerText = total.toFixed(2);
            // change the p tag to display the total
            document.getElementById('displayed_total').innerText = total.toFixed(2);
            // change the textarea to reset the value of total
            document.getElementById('displayed_taxes').innerText = (parseFloat(total.toFixed(2)) * 0.0625).toFixed(2);
        } else {
            // calculate new total
            total = parseFloat(total) - parseFloat(tmp_price);
            // change the p tag to display the total
            document.getElementById('total').innerText = total.toFixed(2);
            // change the textarea to reset the value of total
            document.getElementById('displayed_total').innerText = total.toFixed(2);
            document.getElementById('displayed_taxes').innerText = (parseFloat(total.toFixed(2)) * 0.0625).toFixed(2);
        }
        // clear the delete quantity fields
        const quantity_reset = document.getElementById('delete_quantity_' + item_name);
        quantity_reset.value = "";
    }
}

// js for collapsible sections on the user home pages
var coll = document.getElementsByClassName("collapsible");
var i;

for (i = 0; i < coll.length; i++) {
    coll[i].addEventListener("click", function() {
        this.classList.toggle("active");
        var content = this.nextElementSibling;
        if (content.style.display === "block") {
            content.style.display = "none";
        } else {
            content.style.display = "block";
        }
  });
}
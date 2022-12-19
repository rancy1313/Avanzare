function deleteNewsPost(news_postId) {
  fetch("/delete-news-post", {
    method: "POST",
    body: JSON.stringify({ news_postId: news_postId }),
  }).then((_res) => {
    window.location.href = "/create-news";
  });
} ///this will refresh the page after deletes

function test(var1, var2, var3) {
    one_var = var1 + var2 + var3
  fetch("/this-is-test", {
    method: "POST",
    body: JSON.stringify({vars: [{ one_var: one_var }, { var1: var1 }]}),
  }).then((_res) => {
    window.location.href = "/user_home";
  });
}

function makeList() {
    let string_list = '';
    const table = document.getElementById('actual_order');
    var table_rows = table.getElementsByTagName('tr');
    for (let i = 1; i < table_rows.length; i++) {
        var table_data = table_rows[i].getElementsByTagName('td');
        for (let x = 0; x < table_data.length; x++) {
            if (x == 0 || x == 1 || x == 4) {
                if (x != 4) {
                    string_list += table_data[x].innerText + '*';
                } else {
                    string_list += table_data[x].innerText;
                }
            }
        }
        if (i != table_rows.length - 1) {
            string_list += "#"
        }
    }
    taxes = document.getElementById('displayed_taxes').innerText;
    total = document.getElementById('displayed_total').innerText;
    comment = document.getElementById('comment').value;
    passListToFlask(string_list, total, taxes, comment);
}

function passListToFlask(listOfItem, total, taxes, comment) {
    fetch("/list-of-items", {
        method: "POST",
        body: JSON.stringify({ values: [{ listOfItem: listOfItem }, { total: total }, { taxes: taxes }, { comment: comment }] }),
    }).then((_res) => {
        window.location.href = "/user_home";
    });
}


function testOrderAgain(order_id) {
    let string_list = '';
    const order_table = document.getElementById(`table_${order_id}`);
    var table_rows = order_table.getElementsByTagName('tr');
    for (let i = 1; i < table_rows.length; i++) {
        var table_data = table_rows[i].getElementsByTagName('td');
        for (let x = 0; x < table_data.length; x++) {
            if (x != 3) {
                string_list += table_data[x].innerText + '*';
            } else {
                string_list += table_data[x].innerText;
            }
        }
        if (i != table_rows.length - 1) {
            string_list += "^"
        }
    }
    taxes = document.getElementById('displayed_taxes_' + order_id).innerText;
    total = document.getElementById('displayed_total_' + order_id).innerText;

    fetch("/dud", {
        method: "POST",
      }).then((_res) => {
        window.location.href = `/testOrderAgain/${string_list}/${total}/${taxes}`;
      });
}

function loadPastOrder(new_order) {

    const new_order_items = new_order[0].split('^');
    let total = new_order_items.pop();
    let taxes = new_order_items.pop();
    for (let i = 0; i < new_order_items.length; i++) {
        const individual_item = new_order_items[i].split('*')

        let price = individual_item[2].slice(1, individual_item[2].length)

        price = price / individual_item[1];
        order_total = document.getElementById('total').value;
        addToOrder(individual_item[1], individual_item[3], individual_item[0], price, 'REGULAR', order_total)
        //addToOrder(quantity, item_id, item_name, item_price, item_accommodation, total) {
    }
    //const individual_item = new_order_items.split('*')
    document.getElementById('displayed_total').innerText = total;
    document.getElementById('displayed_taxes').innerText = taxes;

}

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
        const table_row = document.getElementById(`row_${item_name}`);
        if (table_row === null) {
            const order = document.getElementById('actual_order');
            const tmp_item = document.createElement('tr');
            tmp_item.setAttribute('id', `row_${item_name}`);
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
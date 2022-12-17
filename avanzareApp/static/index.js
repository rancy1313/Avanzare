function deleteMenuItem(itemId) {
  fetch("/delete-item", {
    method: "POST",
    body: JSON.stringify({ itemId: itemId }),
  }).then((_res) => {
    window.location.href = "/add-menu-item";
  });
} ///this will refresh the page after deletes

function deleteNewsPost(news_postId) {
  fetch("/delete-news-post", {
    method: "POST",
    body: JSON.stringify({ news_postId: news_postId }),
  }).then((_res) => {
    window.location.href = "/create-news";
  });
} ///this will refresh the page after deletes

function loadDates(lst_dates) {
    for (let i = 0; i < lst_dates.length; i++) {
        var tag = lst_dates[i][0].toString() + '_tag';
        var tmp_date = new Date(lst_dates[i][1])
        document.getElementById(tag).innerHTML = tmp_date;
    }
}

function showPage(item_id, item_params) {
    document.getElementById('demoo').innerHTML = item_id;
    const tmp_div = document.getElementById('edit_div_' + item_id);
    const edit_page = document.createElement('div');
    edit_page.className = "edit_page";
    edit_page.id = "edit_page_" + item_id;
    let tmp_string  = `<p>we are about to edit ${tmp_div.id}</p>
        <button id=${"edit_button_" + item_id} onClick="closeEditPage(${item_id})" class="btn-del" style="float: right;">Close Edit</button>
        <br />
        <form action="/test-edit/${item_id}" method="POST">
            <label for=${'name_' + item_id}>Name:</label>
            <input type="text" id=${'name_' + item_id} name=${'name_' + item_id} class="form-control" value=${item_params[0]}>
            <label for=${'price_' + item_id}>Price:</label>
            <input type="text" id=${'price_' + item_id} name=${'price_' + item_id} class="form-control" value=${item_params[1]}>
            <label for=${'description_' + item_id}>Description:</label>
            <input type="text" id=${'description_' + item_id} name=${'description_' + item_id} class="form-control" value=${item_params[2]}>
            <br />
            <label for=${"gluten_free_" + item_id}><b>Gluten Free Availability: <i>${item_params[3]}</i></b></label>
            <select class="form-control" style="width: 140px; display: inline;" id=${"gluten_free_" + item_id} name=${"gluten_free_" + item_id}>
                <option selected>${item_params[3]}</option>`;
    if (item_params[3] == 'GLUTEN FREE') {
        tmp_string += `<option>NO</option>`;
    } else {
        tmp_string += `<option>GLUTEN FREE</option>`;
    }
    tmp_string += `
            </select>
            <label for=${"vegan_" + item_id}><b>Vegan Availability: <i>${item_params[4]}</i></b></label>
            <select class="form-control" style="width: 90px; display: inline;" id=${"vegan_" + item_id} name=${"vegan_" + item_id}>
                <option selected>${item_params[4]}</option>`;
    if (item_params[4] == 'VEGAN') {
        tmp_string += `<option>NO</option>`;
    } else {
        tmp_string += `<option>VEGAN</option>`;
    }
    tmp_string += `
                </select>
                <br />
                <br />
                <label for=${"menu_type_" + item_id}><b>Menu Type: <i>${item_params[5]}</i></b></label>
                <select id=${"menu_type_" + item_id} name=${"menu_type_" + item_id}>
                    <optgroup label="DINNER MENU">`;
    const dinner_menu = ['APPETIZERS', 'SALADS', 'PIZZAS', 'PASTAS', 'ENTREES', 'SIDES'];
    const other_menus = ['DESSERT MENU', 'AFTER DINNER DRINKS', 'COCKTAILS', 'BEER', 'DRAFT', 'BOTTLE'];
    for (let i = 0; i < dinner_menu.length; i++) {
        if (item_params[5] === dinner_menu[i]){
            tmp_string += `<option selected>${dinner_menu[i]}</option>`;
        } else {
            tmp_string += `<option>${dinner_menu[i]}</option>`;
        }
    }
    tmp_string += `</optgroup>`;
    for (let i = 0; i < other_menus.length; i++){
        if (item_params[5] === other_menus[i]){
            tmp_string += `<option selected>${other_menus[i]}</option>`;
        } else if (other_menus[i] === 'BEER') {
            tmp_string += `<optgroup label="BEER">`;
        } else {
            tmp_string += `<option>${other_menus[i]}</option>`
        }
    }
    tmp_string += `</optgroup>`;

    tmp_string += `
            </select>
            <br />
            <br />
            <button type="submit" class="btn-add">Submit</button>
        </form>`;

    edit_page.innerHTML = tmp_string;
    tmp_div.appendChild(edit_page);
    let edit_button = document.getElementById('edit_' + item_id)
    edit_button.style.display = 'none';
}

function closeEditPage(item_id) {
    const tmp_div = document.getElementById('edit_div_' + item_id);
    const edit_page = document.getElementById('edit_page_' + item_id);
    tmp_div.removeChild(edit_page);
    let edit_button = document.getElementById('edit_' + item_id)
    edit_button.style.display = 'inline';
}

function blueprint(item_id) {
    const tmp_divs = document.getElementsByClassName('only_one');
    const buttons = document.getElementsByClassName('show');
    for (let i = 0; i < tmp_divs.length; i++) {
        tmp_divs[i].setAttribute('hidden', true);
        buttons[i].style.display = 'inline';
    }
    const tmp_hidden = document.getElementById('hidden_' + item_id);
    tmp_hidden.removeAttribute('hidden');
    const edit_button = document.querySelector('#edit_' + item_id);
    edit_button.style.display = 'none';
}

function closeBlueprint(item_id) {
    const edit_page = document.getElementById('hidden_' + item_id);
    edit_page.setAttribute('hidden', true);
    const edit_button = document.getElementById('edit_' + item_id);
    edit_button.style.display = 'inline';
}
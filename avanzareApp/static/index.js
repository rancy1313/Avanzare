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
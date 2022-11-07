function deleteNote(noteId) {
  fetch("/delete-note", {
    method: "POST",
    body: JSON.stringify({ noteId: noteId }),
  }).then((_res) => {
    window.location.href = "/";
  });
} ///this will refresh the page after deletes

function deleteMenuItem(itemId) {
  fetch("/delete-item", {
    method: "POST",
    body: JSON.stringify({ itemId: itemId }),
  }).then((_res) => {
    window.location.href = "/add-menu-item";
  });
} ///this will refresh the page after deletes

function deleteOrderItem(itemId) {
  fetch("/delete-order-item", {
    method: "POST",
    body: JSON.stringify({ itemId: itemId }),
  }).then((_res) => {
    window.location.href = "/refresh-order";
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



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



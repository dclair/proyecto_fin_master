// JavaScript para manejar comentarios con AJAX
document.addEventListener("DOMContentLoaded", function () {
  const commentForm = document.getElementById("comment-form");
  if (commentForm) {
    commentForm.addEventListener("submit", function (e) {
      e.preventDefault();

      const formData = new FormData(this);
      const url = this.action;

      fetch(url, {
        method: "POST",
        body: formData,
        headers: {
          "X-Requested-With": "XMLHttpRequest",
          "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]")
            .value,
        },
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            const commentsList = document.getElementById("comments-list");
            const commentHtml = `
                            <div class="d-flex mb-3" id="comment-${data.comment_id}">
                                <div class="flex-shrink-0">
                                    <a href="/profile/${data.user_id}/">
                                        <img src="${data.avatar_url}" 
                                             class="rounded-circle" 
                                             width="32" 
                                             height="32" 
                                             alt="${data.username}">
                                    </a>
                                </div>
                                <div class="ms-3">
                                    <div class="bg-light p-2 rounded">
                                        <a href="/profile/${data.user_id}/" 
                                           class="fw-bold text-decoration-none text-dark">
                                            ${data.username}
                                        </a>
                                        <p class="mb-0">${data.comment}</p>
                                    </div>
                                    <small class="text-muted">${data.created_at}</small>
                                </div>
                            </div>
                        `;

            if (commentsList.querySelector(".text-muted")) {
              commentsList.innerHTML = commentHtml;
            } else {
              commentsList.insertAdjacentHTML("afterbegin", commentHtml);
            }

            commentForm.reset();
          }
        })
        .catch((error) => console.error("Error:", error));
    });
  }
});

// Script para manejar la respuesta a comentarios en post_detail
function responderComentario(username) {
    const textarea = document.querySelector('textarea[name="comment"]');
    if (textarea) {
        textarea.value = `@${username} `;
        textarea.focus();
        document.querySelector('#comment-form').scrollIntoView({ behavior: 'smooth' });
    }
}

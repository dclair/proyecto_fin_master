# Tasks: profile-followers-search

- [x] **1. HTML: UI del Buscador en Modal Seguidores**
  - Archivo: `profiles/templates/profiles/profile.html`
  - Añadir el `input-group` de búsqueda en `#followersModal`.
  - Añadir `id="followersList"` a la lista `<ul>`.

- [x] **2. HTML: UI del Buscador en Modal Siguiendo**
  - Archivo: `profiles/templates/profiles/profile.html`
  - Añadir el `input-group` de búsqueda en `#followingModal`.
  - Añadir `id="followingList"` a la lista `<ul>`.

- [x] **3. JavaScript: Implementar Client-side Filter**
  - Archivo: `profiles/templates/profiles/profile.html`
  - Añadir script que escuche eventos `input` en `.js-modal-search`.
  - Lógica para ocultar/mostrar los elementos `li` iterando sobre el `DOM`.

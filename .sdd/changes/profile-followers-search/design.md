# Design: Buscador en Modales de Seguidores/Siguiendo

## Modificaciones a Plantillas Django
**Archivo**: `profiles/templates/profiles/profile.html`

1. **Modal Seguidores (`#followersModal`)**:
   - Insertar un bloque de buscador dentro de `.modal-body` justo antes de la etiqueta `<ul>`.
   - Añadir `id="followersList"` a la etiqueta `<ul>` para facilitar la selección en JS.
   - Añadir la clase `js-modal-search` al input y un atributo `data-target="#followersList"`.

2. **Modal Siguiendo (`#followingModal`)**:
   - Insertar el mismo bloque de buscador dentro de `.modal-body` justo antes de la etiqueta `<ul>`.
   - Añadir `id="followingList"` a la etiqueta `<ul>`.
   - Añadir la clase `js-modal-search` al input y un atributo `data-target="#followingList"`.

3. **Lógica JS**:
   - Agregar una etiqueta `<script>` al final de `profile.html` (antes del `</style>` o del `{% endblock %}`).
   - Asignar event listeners `input` a todas las `.js-modal-search`.
   - Filtrar usando `textContent.toLowerCase().includes(...)` sobre el elemento `<a>` dentro de cada `<li>`.
   - Alternar las clases de Bootstrap `d-flex` y `d-none` para mostrar/ocultar los elementos de la lista.

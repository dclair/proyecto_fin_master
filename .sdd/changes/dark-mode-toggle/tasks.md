# Tasks: dark-mode-toggle

- [x] **1. Prevención FOUC en `layout.html`**
  - Archivo: `aficionados_network/templates/general/layout.html`
  - Inyectar el IIFE script (Immediately Invoked Function Expression) en el `<head>` que setea `data-bs-theme` leyendo `localStorage` o matchMedia.

- [x] **2. Script de interactividad en `layout.html`**
  - Archivo: `aficionados_network/templates/general/layout.html`
  - Añadir el event listener al final de la página para gestionar el clic del botón `themeToggleBtn`.

- [x] **3. Refactor de colores en Navbar**
  - Archivo: `aficionados_network/templates/_includes/_header.html`
  - Quitar `bg-white` y `navbar-light` de la etiqueta `<nav>`.
  - Añadir `bg-body-tertiary` (u otra variable de theme) a `<nav>`.

- [x] **4. Botón Toggle en Navbar**
  - Archivo: `aficionados_network/templates/_includes/_header.html`
  - Agregar el `<button id="themeToggleBtn">` cerca de la campana de notificaciones.

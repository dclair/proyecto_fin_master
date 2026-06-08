# Tasks: clean-architecture-assets

## Fase A: Core Layout y Modales Generales
- [x] **1. CSS Global Utilities**: Crear clases de tamaño de avatares (`.avatar-xl`, `.avatar-md`, `.avatar-sm`) y utilidades de fuente en `style.css` para reemplazar los inlines repetitivos.
- [x] **2. JS de `layout.html`**: 
  - Extraer script de scroll de hobbies a `static/js/layout-scroll.js`.
  - Extraer script de toggle dark mode a `static/js/theme-toggle.js` (salvo el IIFE antiblink).
  - Incluir los `<script src="...">` correspondientes al final del body.
- [x] **3. Navbar y Partials (`_header.html`, `_post.html`)**: Eliminar inlines `style="..."` reemplazándolos por las utilidades Bootstrap o clases creadas.

## Fase B: Perfiles (HTML pesado)
- [x] **4. Refactor `profile.html`**:
  - Extraer la lógica JS de los buscadores de seguidores/siguiendo a `static/js/profile-search.js`.
  - Limpiar los atributos `style="..."` en los íconos de validación, fechas, y avatares.
- [x] **5. Refactor de `profile_edit.html` y `profile_list.html`**:
  - Eliminar estilos inline de los formularios y tarjetas de usuario, aplicando clases `.avatar-*`.

## Fase C: Posts y Eventos
- [x] **6. Limpieza de Vistas de Posts**: Revisar `post_detail.html` para extraer scripts y remover estilos inline en videos e imágenes (`object-fit`, resoluciones).
- [x] **7. Validaciones en Formularios**: Extraer cualquier JS inline que habite en `event_form.html` o creación de posts.
- [x] **8. Comprobación Final y Caché**: Ejecutar collectstatic (si aplica) y validar visualmente que no se haya roto ningún modal o espaciado de tarjeta.

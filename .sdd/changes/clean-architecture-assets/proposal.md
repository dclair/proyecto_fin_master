# Proposal: Clean Architecture Assets

## Objetivo
Erradicar toda la deuda técnica asociada a la inyección de código de interfaz y comportamiento (CSS y JS inline) dentro de las plantillas HTML, logrando una estricta separación de responsabilidades.

## Estrategia Técnica

### 1. Extracción de CSS Inline
Se realizará un barrido sistemático de todas las plantillas Django.
- Todo atributo `style="..."` se convertirá en clases CSS dedicadas.
- Si el estilo es único o muy específico de un componente, se creará una clase semántica (ej. `.profile-avatar-lg`, `.notification-timestamp-fixed`) y se definirá en `static/css/style.css`.
- Si el estilo coincide con una utilidad existente en Bootstrap 5 (ej. `style="width: 100%"` -> `w-100`, `style="margin-top: 10px"` -> `mt-2`), se reemplazará directamente por la clase utilitaria para no inflar la hoja de estilos personalizada innecesariamente.

### 2. Migración de JavaScript
Todo bloque `<script>` que contenga lógica de negocio o interactividad será movido a archivos externos.
- `static/js/profile-search.js`: Lógica de búsqueda en tiempo real dentro de los modales de seguidores/siguiendo.
- `static/js/event-form.js`: Validaciones y lógica dinámica del formulario de eventos.
- `static/js/post-interactions.js`: Si existen scripts de comentarios o modales específicos en los posts.
- **Variables Globales**: El único script permitido en el HTML será la inyección estricta de configuración inicial en `layout.html` (ej. `window.DJANGO_USER = "{{ request.user.username }}";`) y la configuración de HTMX `htmx:configRequest` (puesto que depende de la variable `{{ csrf_token }}` de Django). Todo lo demás (lógica condicional, listeners de DOM, toggle de temas) irá a archivos JS cacheados.

### 3. Fases de Ejecución (Batching)
Dado el alto volumen de cambios (afecta casi todas las vistas), dividiremos el trabajo en 3 etapas en la fase de aplicación:
1. **Fase A (Vistas Generales y Componentes)**: Limpieza de `layout.html`, `_header.html`, `_post.html`, y extracción de JS global.
2. **Fase B (Perfiles)**: Limpieza exhaustiva de `profile.html`, `profile_list.html`, `profile_edit.html` y extracción de `profile-search.js`.
3. **Fase C (Posts/Eventos y Notificaciones)**: Limpieza de `post_detail.html`, `event_form.html`, y revisión final de modales.

## Impacto
- **Positivo**: Rendimiento superior (por caché), código limpio, fácil mantenimiento y compatibilidad garantizada con políticas CSP futuras.
- **Riesgo Operativo**: Al mover JS a archivos externos, debemos asegurarnos de que los eventos se enlacen correctamente usando delegación de eventos (`document.addEventListener`) para elementos inyectados dinámicamente por HTMX, y envolviendo todo en `DOMContentLoaded`.

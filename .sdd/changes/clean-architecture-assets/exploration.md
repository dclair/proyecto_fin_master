# Exploración: Clean Architecture Assets (CSS y JS Inline)

## Alcance del Problema
Tras realizar un análisis estático de las plantillas `.html` (Django Templates), se ha detectado una gran acumulación de deuda técnica a nivel de interfaz de usuario y comportamiento del cliente:
1. **CSS Inline (`style="..."`)**: Existen más de 150 instancias de estilos directamente inyectados en elementos HTML. Esto rompe la regla de separación de intereses (SoC) y dificulta el mantenimiento, la responsividad y la herencia del sistema de diseño (especialmente al usar temas como Dark Mode).
2. **JavaScript Inline (`<script>...</script>`)**: Existen alrededor de 10 bloques de script incrustados directamente al final de los archivos HTML (ej. `profile.html`, `profile_list.html`, `post_detail.html`, `event_form.html`, `layout.html`). Estos scripts manejan desde inicializaciones de modales y filtros de búsqueda en tiempo real, hasta la inyección de variables globales para React (`window.DJANGO_USER`).

## Riesgos Actuales
- **Mantenibilidad**: Es muy difícil rastrear dónde se aplican los estilos y comportamientos si no están centralizados.
- **Rendimiento y Caché**: Los estilos y scripts inline no pueden ser cacheados por el navegador. Si el usuario recarga la página, vuelve a descargar todo el texto.
- **Content Security Policy (CSP)**: Si en el futuro se desea implementar políticas de seguridad estrictas (evitando Cross-Site Scripting - XSS), el código inline será bloqueado automáticamente.

## Archivos Principales Afectados
- `profiles/templates/profiles/profile.html` (Buscadores de seguidores, inicialización de modales).
- `profiles/templates/profiles/profile_list.html` (Manejo del scroll y filtros HTMX).
- `profiles/templates/profiles/profile_edit.html` (Ajustes visuales hardcodeados en el form).
- `aficionados_network/templates/general/layout.html` (Scripts de inicialización de HTMX, scroll horizontal y variables React).
- `aficionados_network/templates/posts/post_detail.html` (Interacciones específicas).
- `aficionados_network/templates/posts/event_form.html` (Validación de fechas/formularios).
- Plantillas de inclusión parciales como `_profile_list_items.html`, `_post.html`, `_header.html`, `_cookies_banner.html`.

# Spec: Clean Architecture Assets

## User Stories / Developer Stories
1. **Developer Experience**: Como desarrollador, quiero tener todo el CSS y JS centralizado en los archivos estáticos para poder utilizar el sistema de versionado, el caché del navegador, y no tener que recorrer docenas de plantillas buscando dónde se está sobreescribiendo un color o comportamiento.
2. **Seguridad / CSP**: Como administrador del sistema, quiero asegurar que mi sitio pueda implementar políticas de CSP (Content Security Policy) restrictivas sin romper la funcionalidad, lo que exige eliminar los scripts inline y delegar eventos desde el JS externo.
3. **Mantenibilidad UI**: Como diseñador UI, quiero que los márgenes, tamaños y comportamientos visuales se gestionen a través de utilidades (Bootstrap) o clases en `style.css`, para poder cambiarlos globalmente sin editar 50 plantillas.

## Requisitos de Arquitectura (Reglas Estrictas)
1. **Cero `style="..."`**: Está completamente prohibido el uso de estilos inline en los tags HTML, con excepción estricta de barras de progreso dinámicas (ej. `style="width: {{ percent }}%"`) o imágenes de fondo que dependan del ORM de Django (ej. `style="background-image: url('{{ cover.url }}')"`).
2. **Cero Lógica en `<script>` HTML**: No se permiten declaraciones de funciones, event listeners, manipulación del DOM, o lógicas complejas en el HTML. Todo debe ir en `static/js/`.
3. **Manejo de HTMX**: Los scripts movidos a JS deben hacer uso de `document.addEventListener('htmx:afterSwap', function...)` o inicializaciones globales seguras si manejan contenido inyectado asíncronamente por HTMX.
4. **Data Attributes**: Para pasar variables de Django al JS externo de manera limpia, se deben usar atributos `data-*` en el HTML (ej. `<div id="postData" data-post-id="{{ post.id }}"></div>`) en lugar de inyectarlos como strings dentro de `<script>`.

## Fuera de Alcance
- Refactorizar componentes grandes a React si son puramente de Django HTMX. (Se mantendrá Django HTML + Vanilla JS).
- Cambiar la versión de Bootstrap.
- Escribir tests unitarios para las funciones JS (MVP centrado en refactorización).

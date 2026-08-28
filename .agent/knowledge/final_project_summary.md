# Resumen Final del Proyecto (Hubs&Clicks)
**Estado:** 100% Completado.

Este documento sirve como anclaje de conocimiento para cualquier agente que analice el código en el futuro.

## Funcionalidades Core Completadas
1. **Chat en Tiempo Real (React + Django Channels):**
   - WebSockets con ASGI (Channels + Redis).
   - Chat 1-on-1 y Grupos.
   - Envío de adjuntos multimedia (subida vía REST API y notificación por WebSocket).
   - Eliminación de mensajes: "Para todos" (física/cascade) y "Para mí" (lógica por `hidden_by`).
   - Integración nativa en `ChatApp.jsx` embebida en las templates de Django.
   - **NUEVO**: Panel dinámico de Participantes con buscador en tiempo real dentro de los chats grupales.
   - **NUEVO**: Integración Automática con Quedadas (Events). Al crear un evento online, se genera un Grupo de Chat. Al unirse al evento, los usuarios son sincronizados automáticamente como participantes del grupo mediante Django Signals (`post_save`, `post_delete`).

2. **Autenticación e Identidad:**
   - Custom User Model (donde el Email es único y utilizado para buscar usuarios).
   - Registro con confirmación por correo electrónico.
   - Recuperación de contraseña.

3. **Buscador y Directorio (HTMX):**
   - El listado de la "Comunidad de Terapeutas" usa scroll infinito gestionado nativamente por `htmx` en lugar de paginación clásica.
   - El buscador avanzado localiza simultáneamente por `username`, `first_name`, `last_name` y `email` (con `Q` objects).

4. **Eventos (Quedadas) e Híbridos:**
   - CRUD de eventos. Capacidad física y online (Stream URL embebida en `iframes` de YouTube u opción de botón externo).
   - Cancelaciones con notificaciones automáticas y clonado de eventos pasados.
   - Filtro avanzado por Ciudad, Categoría, Nivel y el botón especial "Mis Terapias".

5. **Interacción Social y Notificaciones (HTMX):**
   - Comentarios y Likes (gestionados por Ajax nativo en `likes.js` y `comentarios.js`).
   - Seguimiento (Follows) entre usuarios.
   - Sistema de Valoraciones (Reseñas con estrellas tras asistir a eventos).
   - Notificaciones in-app y por Email corporativo.
   - **NUEVO:** Sistema de gestión de notificaciones asíncrono. Borrado individual y masivo sin recarga de página, integrado tanto en el dropdown de navegación como en la vista de historial (`HTMX` + `HX-Trigger`). Completamente respaldado por pruebas unitarias.

6. **Gestión de Integridad de Datos e Históricos (NUEVO):**
   - Implementación de un patrón de arquitectura **Soft Delete** (mediante `SoftDeleteModel` y `SoftDeleteManager`).
   - Los modelos críticos (`Event`, `Posts`, `Hobby`) ya no se eliminan físicamente de la base de datos (se usa `is_active=False` y `deleted_at`). 
   - Las relaciones foráneas se cambiaron de `CASCADE` a `PROTECT` para asegurar que el contenido generado por los terapeutas se preserve a lo largo del tiempo.

## Detalles de Arquitectura y Despliegue
- El proyecto corre sobre Python 3.12 y Django 6.0.
- El chat está compilado con Vite. Los assets se generan en `static/chat/`. Para el entorno de desarrollo se configuró el script `start_dev.sh` que levanta simultáneamente Django, Vite y Redis usando Tmux.
- La Base de Datos principal en producción es MySQL/MariaDB (`DB_ENGINE=mysql`).
- Las dependencias asíncronas para el chat están limitadas en versiones (`redis<5.0.0`) para evitar bugs documentados.
- **Modo Oscuro:** Gestionado de forma global en Django vía `[data-bs-theme="dark"]` en `style.css`. La aplicación de Chat en React está explícitamente aislada en modo claro (`data-bs-theme="light"`) para evitar colisiones de diseño con sus componentes hardcodeados.
- **UI/UX y Formularios:** Estandarización completa del sistema de *spinners* de carga para evitar reenvíos, corrección de z-index y márgenes en alertas de mensajes (`_messages.html`), y unificación total del navbar (`_header.html`) para todos los dispositivos con flujos lógicos para los usuarios.

**Next Steps Posibles (Mantenimiento):**
- Optimización de queries (Select_related y Prefetch_related).
- Configuración de SSL (WSS/HTTPS) para producción.
- Despliegue final en servidor (Render, Railway, VPS).

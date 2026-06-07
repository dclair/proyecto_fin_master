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

5. **Interacción Social:**
   - Comentarios y Likes (gestionados por Ajax nativo en `likes.js` y `comentarios.js`).
   - Seguimiento (Follows) entre usuarios.
   - Notificaciones in-app y por Email corporativo.
   - Sistema de Valoraciones (Reseñas con estrellas tras asistir a eventos).

## Detalles de Arquitectura y Despliegue
- El proyecto corre sobre Python 3.12 y Django 6.0.
- El chat está compilado con Vite. Los assets se generan en `static/chat/`.
- La Base de Datos principal en producción es MySQL/MariaDB (`DB_ENGINE=mysql`).
- Las dependencias asíncronas para el chat están limitadas en versiones (`redis<5.0.0`) para evitar bugs documentados.

**Next Steps Posibles (Mantenimiento):**
- Optimización de queries (Select_related).
- Configuración de SSL (WSS/HTTPS) para producción.
- Ajustes finos de CSS si el cliente lo requiere.

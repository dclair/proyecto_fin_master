# Explore: estado-actual

**Status**: Completado.
**Topic**: estado-actual

## Resumen Ejecutivo
El proyecto "Hubs&Clicks" es un monolito en Django 6.0 corriendo sobre Python 3.12. Renderizado clásico del lado del servidor usando Bootstrap y Crispy Forms, con integraciones de Vanilla JS, HTMX y React 18 embebido vía Vite para el chat (con WebSockets vía Django Channels).

El sistema está dividido en 4 apps principales:
1. `aficionados_network`: Entrypoint, settings, autenticación y algunas vistas de perfil legacy.
2. `profiles`: Identidad del usuario, Hobbies y sistema de Follows/Reviews.
3. `posts`: Maneja posteos sociales ("Clicks") y flujo completo de Eventos.
4. `notifications`: Sistema in-app de notificaciones.

Actualmente los 35 tests pasan con SQLite, y existe una migración activa/reciente hacia MySQL/MariaDB (`sqlite-to-mysql-migration`).

## Riesgos Técnicos (Technical Debt)
1. **Vistas Duplicadas y Legacy**: Código de perfiles antiguo convive en `aficionados_network/views.py`. `HomeView` está definida dos veces en el mismo archivo.
2. **Rutas Duplicadas**: Las rutas de los perfiles están definidas tanto de forma global como con namespaces.
3. **Atributos Dinámicos al Vuelo**: Variables como `is_match` o `is_mentor` se inyectan en tiempo de ejecución sin soporte en el modelo de base de datos.
4. **Manejo de Archivos Estáticos y Media**: Riesgo de desincronización durante la migración a MySQL si los archivos `media/` no se migran junto a las rutas almacenadas en la DB.

## Siguiente Paso Recomendado
Se recomienda abordar la deuda técnica antes de continuar agregando funcionalidades, mediante el flujo `/sdd-new` con alguno de los siguientes refactors:
- `/sdd-new refactor-views-legacy`
- `/sdd-new cleanup-routes`

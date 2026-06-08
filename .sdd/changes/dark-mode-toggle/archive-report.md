# Archive Report: Dark Mode Toggle

## Alcance del Proyecto
Implementación de un Dark Mode nativo usando Bootstrap 5.3 (`data-bs-theme`) en toda la aplicación, junto con un switch de control en la barra de navegación que persiste la preferencia del usuario en `localStorage`.

## Cambios Realizados
1. **Prevención de FOUC**: Inyección de un IIFE script en `<head>` de `layout.html` para detectar el tema preferido (por `localStorage` o sistema operativo) antes del renderizado de la página.
2. **Switch UI**: Inclusión de un botón dinámico (sol/luna) en `_header.html` que altera la apariencia de la web de inmediato.
3. **Refactorización CSS**: Eliminación de colores rígidos que afectaban la experiencia del modo oscuro en `style.css`.
   - Modificados: `body`, `.profile-post-card`, `.post-card`, `.card-hubs`, `.sidebar-group`, `.detail-banner-wrapper`, `.img-event-wrapper` y `.mobile-hobby-pill`.
   - Uso intensivo del pseudo-selector `[data-bs-theme="dark"]` para sobreescribir los hardcodes de modo claro (`--hubs-light`, `#dde8ea`, etc.).
4. **Minor Fix**: Se eliminó la sombra (`box-shadow` y borde) del botón `.back-to-top` para darle un aspecto más limpio y minimalista.

## Estado Final
- La web soporta múltiples modos de color eficientemente.
- Las tarjetas, banners e interfaz en general contrastan de forma correcta y prolija al estar el modo oscuro activado.
- El proyecto se encuentra estable y listo para uso en producción.

**Ciclo SDD Cerrado.**

# Design: Clean Architecture Assets

## Arquitectura de Archivos (Frontend)
Los scripts actualmente dispersos se organizarán modularmente dentro de `static/js/`.

### Nuevos Archivos Estáticos a Crear o Modificar
1. **`static/js/profile-search.js`**: 
   - Contendrá la lógica de filtrado en vivo para los modales de "Seguidores" y "Siguiendo" que actualmente viven en `profile.html`.
2. **`static/js/layout-scroll.js`**:
   - Moverá la lógica de la barra de scroll horizontal y las flechas `.mobile-hobby-scroll` desde `layout.html`.
3. **`static/js/theme-toggle.js`**:
   - Extraer la lógica del botón Dark Mode que acabamos de meter en `layout.html` (manteniendo el IIFE en `<head>` por temas de FOUC).
4. **`static/css/utilities.css` (o dentro de `style.css`)**:
   - Clases que mapeen las docenas de estilos inline (ej. `object-fit: cover; width: 130px; height: 130px;` -> `.avatar-xl`, `.avatar-lg`, `.avatar-sm`).

## Patrón de Refactorización CSS
**Antes:**
```html
<img src="{{ user.profile_picture_url }}" style="width: 130px; height: 130px; object-fit: cover" class="rounded-circle">
<div class="mt-2 text-muted" style="font-size: 0.75rem;">Texto</div>
```

**Después:**
```html
<img src="{{ user.profile_picture_url }}" class="rounded-circle avatar-xl">
<div class="mt-2 text-muted fs-xs">Texto</div>
```

**En `style.css`:**
```css
.avatar-xl { width: 130px; height: 130px; object-fit: cover; }
.avatar-lg { width: 80px; height: 80px; object-fit: cover; }
.avatar-sm { width: 35px; height: 35px; object-fit: cover; }
.fs-xs { font-size: 0.75rem; }
.fs-xxs { font-size: 0.65rem; }
```

## Patrón de Refactorización JS (Delegación de Eventos)
**Antes (En `profile.html`):**
```html
<input id="followerSearch">
<script>
    document.getElementById('followerSearch').addEventListener('input', function(e) { ... });
</script>
```

**Después (En `static/js/profile-search.js`):**
```javascript
document.addEventListener('DOMContentLoaded', () => {
    const followerSearch = document.getElementById('followerSearch');
    if (followerSearch) {
        followerSearch.addEventListener('input', function(e) { ... });
    }
});
```

*Nota para HTMX*: Si hay lógica que se aplica a modales que se cargan dinámicamente o listas infinitas, se usarán selectores por clase y propagación de eventos desde el documento o `htmx:load`.

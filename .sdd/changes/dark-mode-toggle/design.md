# Design: Dark Mode Toggle

## Modificaciones a Plantillas Django

### 1. `aficionados_network/templates/general/layout.html`
**Inicialización temprana (Prevención FOUC):**
Insertar dentro de `<head>`, antes de cualquier CSS o componente pesado:
```javascript
<script>
  (function() {
    const storedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    if (storedTheme === 'dark' || (!storedTheme && prefersDark)) {
      document.documentElement.setAttribute('data-bs-theme', 'dark');
    } else {
      document.documentElement.setAttribute('data-bs-theme', 'light');
    }
  })();
</script>
```

**Script de control del botón (al final del body):**
```javascript
<script>
  document.addEventListener('DOMContentLoaded', () => {
    const themeToggleBtn = document.getElementById('themeToggleBtn');
    const themeIcon = document.getElementById('themeIcon');
    
    if (themeToggleBtn) {
      // Set initial icon
      const currentTheme = document.documentElement.getAttribute('data-bs-theme');
      themeIcon.className = currentTheme === 'dark' ? 'bi bi-sun-fill text-warning' : 'bi bi-moon-stars-fill text-dark';

      themeToggleBtn.addEventListener('click', () => {
        const theme = document.documentElement.getAttribute('data-bs-theme') === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-bs-theme', theme);
        localStorage.setItem('theme', theme);
        themeIcon.className = theme === 'dark' ? 'bi bi-sun-fill text-warning' : 'bi bi-moon-stars-fill text-dark';
      });
    }
  });
</script>
```

### 2. `aficionados_network/templates/_includes/_header.html`
**Ajuste del Navbar:**
Cambiar las clases rígidas de color en `<nav>` de `bg-white` a `bg-body-tertiary` (o `bg-body`) para permitir que varíe automáticamente. 
Eliminar `navbar-light` que fuerza el contraste.

**Botón:**
Insertarlo en la lista `<ul>`, por ejemplo, junto al botón de notificaciones:
```html
<li class="nav-item px-2 d-flex align-items-center">
    <button id="themeToggleBtn" class="btn btn-link nav-link p-0 border-0" aria-label="Toggle theme">
        <i id="themeIcon" class="bi"></i>
    </button>
</li>
```

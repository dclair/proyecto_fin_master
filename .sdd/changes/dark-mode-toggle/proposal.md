# Proposal: Dark Mode Toggle

## Objetivo
Implementar un "Dark Mode" persistente aprovechando el soporte nativo de Bootstrap 5.3, con un interruptor (botón) ubicado en la barra de navegación principal.

## Estrategia Técnica

### 1. Inicialización en `<head>` (Prevención de FOUC)
En `aficionados_network/templates/general/layout.html`, justo antes de cerrar el `<head>`, inyectaremos un script mínimo bloqueante. Este script:
- Leerá el `localStorage` buscando la clave `theme`.
- Si no existe, leerá la preferencia del sistema operativo (`window.matchMedia('(prefers-color-scheme: dark)')`).
- Aplicará el atributo `data-bs-theme="dark"` (o `light`) al nodo `document.documentElement` (`<html>`).

### 2. Botón Toggle (`_header.html`)
Agregaremos un elemento a la lista de navegación (cerca del icono de notificaciones) para cambiar el tema.
- Ícono inicial: Se sincronizará usando JS (Luna para dark, Sol para light).
- Evento de Clic: Al hacer clic, alternará el valor en el `document.documentElement`, actualizará el `localStorage`, y rotará el icono.

### 3. Ajuste de Clases Hardcodeadas
Al aplicar el modo oscuro, elementos que tengan clases utilitarias de Bootstrap como `bg-white` o `text-dark` no se invertirán automáticamente, porque Bootstrap respeta esos colores explícitos.
- `_header.html`: Reemplazaremos `bg-white` por `bg-body` o `bg-body-tertiary` en el `navbar`, para que el color de fondo fluya entre blanco (light) y oscuro (dark).

## Resumen de Cambios
- `layout.html`: Script de inicialización de tema.
- `_header.html`: Ajuste de clase del navbar (`bg-body` en lugar de `bg-white`) y agregado del botón tipo `<button>` con icono de sol/luna.
- `base.js` o script inline: Lógica del botón para escuchar el evento click y mutar el atributo y el localStorage.

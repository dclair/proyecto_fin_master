# Exploración: Buscador en Modales de Seguidores/Siguiendo

## Estado Actual
- **Ruta/Vista**: El perfil de usuario se renderiza en `profiles/templates/profiles/profile.html`.
- **Datos**: Los seguidores y usuarios a los que se sigue ya se inyectan en el DOM a través de los loops `{% for follower in user_profile.followers.all %}` y `{% for followed in user_profile.following.all %}`.
- **UI**: Se presentan en forma de listas dentro de dos modales (`#followersModal` y `#followingModal`).
- **Problema**: Cuando el número de elementos es grande (ej: >100), es imposible encontrar a un usuario específico sin hacer *scroll* infinito.

## Solución Existente ("Explorar Terapeutas")
En `profile_list.html`, existe un buscador que funciona del lado del servidor (`?q=...`).
Sin embargo, aplicar búsqueda del lado del servidor a los modales implicaría:
1. Recargar toda la página de perfil cada vez que se busca dentro del modal.
2. Manejar estado en la URL para mantener el modal abierto después de recargar.
*Esto arruinaría la experiencia de usuario (UX).*

## Enfoque Propuesto
Dado que los datos de la lista **ya están renderizados en el DOM** por el backend de Django, la solución más limpia y rápida (sin modificar endpoints de Python) es hacer un **filtrado en tiempo real (Client-side Search)** con JavaScript nativo, emulando visualmente el buscador de "Explorar Terapeutas".

**Mecánica**:
1. Insertar un `<input type="text">` en el `modal-header` (o al inicio del `modal-body`) de ambos modales.
2. Añadir un script JS ligero que, en el evento `input`, lea el valor del input, itere sobre las `<li class="list-group-item">` del modal correspondiente, y haga `display: none` a los elementos cuyo texto (nombre de usuario) no coincida con el término buscado.
3. Esto garantiza respuesta inmediata (0 latencia) sin tocar el backend.

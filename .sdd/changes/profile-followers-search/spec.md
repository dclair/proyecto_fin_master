# Spec: Buscador en Modales de Seguidores/Siguiendo

## User Stories
1. **Buscar Seguidor**: Como usuario, al abrir el modal de Seguidores, quiero ver un campo de búsqueda arriba de la lista. Al tipear el nombre de un usuario, la lista debe filtrarse instantáneamente para mostrar solo los seguidores cuyo nombre contenga el texto introducido.
2. **Buscar Seguido**: Como usuario, al abrir el modal de Siguiendo, quiero poder buscar entre las personas que sigo usando un campo de búsqueda con filtrado instantáneo.

## Requisitos de UI/UX
- El input de búsqueda debe tener un ícono de lupa (`bi-search`) y coincidir visualmente con el diseño de `profile_list.html` pero adaptado al espacio del modal (ej: `input-group-sm`).
- El filtrado no debe distinguir entre mayúsculas y minúsculas (case-insensitive).
- Si el input está vacío, se deben mostrar todos los usuarios.
- El filtrado debe ser instantáneo (sin necesidad de apretar botón "Buscar" ni "Enter").

## Fuera de Alcance (Out of Scope)
- No se implementará búsqueda en el backend.
- No se manejará paginación asíncrona dentro del modal.

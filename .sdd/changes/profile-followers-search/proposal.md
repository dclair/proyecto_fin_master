# Proposal: Buscador en Modales de Seguidores/Siguiendo

## Objetivo
Agregar un input de búsqueda en los modales de "Seguidores" y "Siguiendo" dentro del perfil (`profile.html`), manteniendo el mismo look & feel del buscador de "Explorar Terapeutas".

## Propuesta Técnica
Vamos a implementar un **Client-Side Filter** en Javascript puro. 
Dado que la plantilla `profile.html` ya incluye todos los nodos de la lista en el DOM, hacer solicitudes al backend con `?q=` recargaría la página, perdiendo el estado del modal abierto y frustrando al usuario. Un filtro en el frontend es instantáneo y mucho mejor para la UX en este contexto.

### Cambios Requeridos (`profiles/templates/profiles/profile.html`):

1. **HTML (UI)**:
   Añadir en el `modal-body` (arriba de la lista `<ul>`) de ambos modales (`#followersModal` y `#followingModal`) el siguiente snippet inspirado en `profile_list.html`:
   ```html
   <div class="p-3 border-bottom">
       <div class="input-group input-group-sm">
           <span class="input-group-text bg-white"><i class="bi bi-search"></i></span>
           <input type="text" class="form-control border-start-0 ps-0 js-modal-search" 
                  placeholder="Buscar usuario..." data-target="#followersList"> <!-- o #followingList -->
       </div>
   </div>
   ```
   *Se asignarán IDs a los `<ul>` (`id="followersList"`, `id="followingList"`) para identificarlos fácilmente.*

2. **JavaScript (Lógica de filtrado)**:
   Añadir un bloque `<script>` al final de `profile.html`:
   ```javascript
   document.addEventListener('DOMContentLoaded', function() {
       const searchInputs = document.querySelectorAll('.js-modal-search');
       
       searchInputs.forEach(input => {
           input.addEventListener('input', function(e) {
               const searchTerm = e.target.value.toLowerCase().trim();
               const targetListId = input.getAttribute('data-target');
               const listItems = document.querySelectorAll(`${targetListId} li.list-group-item`);
               
               listItems.forEach(item => {
                   // Extraemos el texto del username contenido en el enlace <a>
                   const username = item.querySelector('a').textContent.toLowerCase();
                   
                   if (username.includes(searchTerm)) {
                       item.classList.remove('d-none');
                       item.classList.add('d-flex');
                   } else {
                       item.classList.remove('d-flex');
                       item.classList.add('d-none');
                   }
               });
           });
       });
   });
   ```

## Beneficios
- **Performance**: 0 roundtrips al servidor. Filtro inmediato a medida que el usuario tipea.
- **Simplicidad**: No requiere tocar vistas (`views.py`) ni alterar la paginación ni el routing del proyecto.
- **UX**: Mantiene el estado de la página sin recargarla.

## Limitaciones Conocidas
- Esta solución asume que la lista de seguidores no se pagina en el servidor. Si el usuario llegara a tener 100,000 seguidores en un futuro, el renderizado del DOM de 100k nodos crashearía el navegador de todas formas, pero ese sería un problema arquitectónico general del diseño actual, no específico de este buscador. Para la escala MVP de la aplicación, es la solución perfecta.

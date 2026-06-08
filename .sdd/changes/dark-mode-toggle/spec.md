# Spec: Dark Mode Toggle

## User Stories
1. **Toggle Switch**: Como usuario, quiero ver un botón en la barra de navegación para poder cambiar rápidamente entre modo claro y modo oscuro, dependiendo de mis preferencias visuales o del ambiente en el que me encuentre.
2. **Persistencia**: Como usuario, espero que si elijo el modo oscuro, la plataforma lo recuerde la próxima vez que inicie sesión o al navegar por distintas páginas (sin que "titile" en blanco).
3. **OS Preference**: Como nuevo usuario que llega a la web, quiero que el sitio detecte automáticamente si mi sistema operativo (Windows, macOS, iOS, Android) está en modo oscuro y aplique ese tema por defecto.

## Requisitos de UI/UX
- El botón debe alternar su ícono: un sol (`bi-sun-fill`) cuando el tema activo es oscuro (para indicar que hacer clic activará el claro), y una luna (`bi-moon-fill`) cuando el tema activo es claro.
- No debe haber FOUC (Flash of Unstyled Content). El color de fondo y de texto principal deben renderizarse inmediatamente en la carga de la página.

## Fuera de Alcance (Out of Scope)
- Reescribir todo el CSS de componentes personalizados (se asumirá que la mayoría de elementos usan componentes de Bootstrap que reaccionan automáticamente a `data-bs-theme`).
- Guardar la preferencia en la base de datos vinculada al perfil del usuario (se usará exclusivamente `localStorage` para el MVP).

# Exploración: Modo Oscuro (Dark Mode Toggle)

## Estado Actual
- **Framework CSS**: El proyecto utiliza Bootstrap 5.3.2 (como se ve en `layout.html`).
- **Soporte Nativo**: Bootstrap 5.3 soporta el modo oscuro nativo seteando el atributo `data-bs-theme="dark"` en el tag `<html>` o en cualquier contenedor.
- **Componentes**: El navbar global (`_header.html`) aloja los enlaces principales, las notificaciones y los botones de sesión. Es el lugar ideal para un toggle switch de tema.

## Requisitos
1. **Persistencia**: La elección del usuario (claro u oscuro) debe guardarse en el navegador (`localStorage`) para que al navegar a otra vista no se revierta al color por defecto.
2. **Prevención de FOUC (Flash of Unstyled Content)**: El tema debe aplicarse inmediatamente antes de que el resto del CSS cargue o la página renderice. Esto implica que la lectura del `localStorage` debe ocurrir en el `<head>` de `layout.html`.
3. **UI**: Un botón accesible (ícono de luna/sol) ubicado en el navbar de `_header.html`.

## Análisis de Integración
Al activar el modo oscuro, ciertas variables CSS personalizadas (como los colores primarios de la marca, o clases hardcodeadas como `bg-white` o `text-dark`) pueden requerir ajustes finos. Bootstrap ajusta automáticamente la mayoría, pero si el navbar tiene la clase `bg-white`, podría verse forzadamente blanco. Tendremos que usar las clases de tema semántico (`bg-body`, `text-body`) o dejar que Bootstrap resuelva el contraste.

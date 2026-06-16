# SDD Archive: Modificar flujo de registro y autenticación

**Fecha:** 2026-06-16
**Estado:** `archive`

## Resumen Ejecutivo
Se implementó un nuevo flujo de registro manual con aprobación de administrador, se cambió el sistema de login para usar el correo electrónico en lugar del nombre de usuario y se blindó el acceso a la sección de Biblioteca.

## Artefactos y Cambios Realizados

1. **Flujo de Registro Manual**:
   - Modelos: Añadidos los campos obligatorios `razon_social` y `numero_socio` al modelo `UserProfile` en `profiles/models.py`.
   - Formularios: Modificado el `RegisterForm` (`aficionados_network/forms.py`) para incluir ambos campos y marcarlos como `required=True`. Además, se rediseñó el texto de ayuda del nombre de usuario y contraseña para mayor amigabilidad.
   - Vistas: La vista de registro (`RegisterView` en `aficionados_network/views.py`) guarda a los usuarios como inactivos (`is_active=False`) y notifica al administrador (`jmdclair@gmail.com`).
   - Signals: Se añadió lógica en `profiles/signals.py` usando `pre_save` y `post_save` en el modelo `User` para detectar la activación manual en el Admin Panel y disparar un email de bienvenida automático.
   - UI: Se creó la plantilla `registration_pending.html` como landing post-registro y se arreglaron detalles de contraste en modo oscuro.

2. **Login por Correo Electrónico**:
   - Backend: Se creó un backend de autenticación personalizado (`EmailBackend` en `aficionados_network/backends.py`) que permite hacer login tanto con el `username` como con el `email`.
   - Settings: Se agregó a `AUTHENTICATION_BACKENDS`.
   - Formulario: Se actualizó `LoginForm` para usar un `EmailInput` con el label "Correo electrónico".

3. **Seguridad en la Biblioteca**:
   - Vistas: Se aplicó `LoginRequiredMixin` a `ArticleListView` y `ArticleDetailView` en `library/views.py`.
   - Menú: Se ocultó el enlace a la Biblioteca en `_header.html` si el usuario no está autenticado.

## Riesgos y Consideraciones Futuras
- **Escalabilidad de Emails**: Actualmente el administrador de notificaciones está "hardcodeado". Se recomienda pasarlo a variables de entorno en el futuro (`ADMIN_EMAIL`).
- **Recuperación de Contraseñas**: Asegurarse de que el flujo de reseteo de contraseñas funcione bien con el nuevo `EmailBackend` (Django por defecto maneja esto sin problemas, pero siempre es bueno testearlo).

# Knowledge Item: Registration and Authentication Flow

## Contexto
El proyecto requiere que el registro de nuevos usuarios no sea automático (no se auto-activan) para evitar el acceso de no profesionales. Todo usuario registrado queda en un estado pendiente (`is_active=False`) y se aprueba manualmente por la administración.

## Arquitectura de Registro

1. **Campos Requeridos**: Para garantizar que los registros son reales, el formulario de registro (`aficionados_network/forms.py` -> `RegisterForm`) exige `razon_social` y `numero_socio` (almacenados en `UserProfile`).
2. **Desactivación Inicial**: En la vista de registro (`RegisterView`), se fuerza la bandera de inactividad:
   ```python
   user.is_active = False
   user.save()
   ```
3. **Notificación al Admin y Feedback al Usuario**: Al guardarse la instancia, se envía un correo a la cuenta administrativa configurada. El usuario es redirigido a una vista de espera (`registration_pending.html`) donde se le indica que si en 72 horas no es activado, puede usar el enlace de contacto con un asunto predefinido para agilizar el reclamo.
4. **Validación**: El administrador utiliza el entorno nativo de Django (`/admin`) para revisar el perfil. Al marcar `is_active=True`, se dispara un signal.
5. **Signals (`profiles/signals.py`)**:
   - `pre_save`: Atrapa el estado anterior de `is_active`.
   - `post_save`: Si antes era `False` y ahora es `True`, se envía el `welcome_email.html` al usuario automáticamente.

## Autenticación por Correo

El proyecto delega el acceso primario al Correo Electrónico en lugar del Nombre de Usuario por usabilidad.

1. **EmailBackend (`aficionados_network/backends.py`)**: Clase custom que hereda de `ModelBackend`. Implementa lógica con consultas OR (`Q()`) para localizar al usuario vía `username` o `email` en la función `authenticate()`.
2. **Configuración**: Se encuentra registrado en `settings.py` como el backend primario dentro de `AUTHENTICATION_BACKENDS`.
3. **UI**: El formulario `LoginForm` sobrescribe el widget y label del campo "username" para simular un "EmailInput".

## UI/UX y Accesibilidad
- Cuando se usan formularios y se reescriben los `help_text` de Django (como en los validadores de contraseñas), se inyectan en HTML directo.
- Para modo oscuro (Bootstrap 5 via `data-bs-theme="dark"`), el uso de la clase `dark-mode-text-dark` asegura contraste cuando hay un fondo claro (`bg-light`) que envuelve textos.

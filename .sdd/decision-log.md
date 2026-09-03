# Decision Log

**Last reviewed:** 2026-06-01  
**Purpose:** record important technical/product decisions and why they were made.

This is not a commit log. It captures decisions that future developers and AI agents should understand before changing direction.

## D-001: Keep Django Server-Rendered Architecture

**Date:** before 2026-06-01  
**Decision:** Hubs&Clicks remains a server-rendered Django application with templates, Bootstrap, vanilla JS, AJAX, and selective HTMX-style partial responses.

**Why:**

- The current codebase is organized around Django views, forms, templates, messages, and context processors.
- User workflows are conventional CRUD/social flows that do not require SPA complexity.
- Server rendering keeps auth, forms, redirects, messages, and email-triggering interactions straightforward.

**Implications:**

- New features should prefer Django views/forms/templates unless there is a strong reason otherwise.
- JS should enhance interactions, not replace core server behavior.
- Tests should verify redirects, templates, context, DB rows, emails, and notifications.

## D-002: Use Environment-Selected Database Backend

**Date:** 2026-05-25 migration work  
**Decision:** `DB_ENGINE` selects SQLite or MySQL/MariaDB in `settings.py`.

**Why:**

- SQLite is convenient for local fallback and fast tests.
- MySQL/MariaDB is better for production-like concurrency and deployment.
- Shell environment override allows recovery and test commands without editing `.env`.

**Implications:**

- Use `env DB_ENGINE=sqlite ...` for local tests by default.
- Use MySQL/MariaDB runs only when validating database-specific behavior.
- Do not change `load_dotenv()` to override shell environment variables.

## D-003: Prefer PyMySQL Fallback For MySQL Compatibility

**Date:** 2026-05-25 migration work  
**Decision:** If `mysqlclient`/`MySQLdb` is unavailable and `pymysql` exists, install PyMySQL as MySQLdb before Django loads the backend.

**Why:**

- Avoids requiring native MySQL development headers in local environments.
- Keeps Django's MySQL backend usable with a pure-Python driver.
- A Django 6 compatibility version patch is present in settings.

**Implications:**

- Keep the fallback near the top of `settings.py`.
- Re-test MySQL behavior after driver/version changes.

## D-004: Keep Hobbies As Shared Domain Taxonomy

**Date:** before 2026-06-01  
**Decision:** `profiles.Hobby` is the shared category/interest model across profiles, posts, and events.

**Why:**

- Users express interests through hobbies.
- Posts are categorized by hobby.
- Events belong to hobbies.
- Event matching and hub pages depend on a common taxonomy.

**Implications:**

- Do not create a separate post category or event category model unless there is a strong product reason.
- Changes to `Hobby` can affect profile editing, post creation, event creation, hubs, filters, and tests.

## D-005: Store User Hobby Level In Through Model

**Date:** before 2026-06-01  
**Decision:** User hobby experience is stored in `profiles.UserHobby`, not directly on `UserProfile` or `Hobby`.

**Why:**

- A user can have different levels for different hobbies.
- Event matching needs per-hobby user level.
- The unique `(profile, hobby)` constraint prevents duplicated interests.

**Implications:**

- Match/mentor logic should query `UserHobby`.
- Adding fields to hobby membership means changing the through model and tests.

## D-006: Preserve Dual Notification Surfaces

**Date:** before 2026-06-01  
**Decision:** Important interactions often create both an in-app notification and a branded HTML email.

**Why:**

- In-app notifications support return visits and activity history.
- Emails notify users who are away from the app.
- The product README describes this as a core communication/branding feature.

**Implications:**

- When modifying likes, comments, event attendance, cancellation, reactivation, follows, or reviews, check both notification and email behavior.
- Tests should assert both DB notifications and `mail.outbox` where applicable.

## D-007: Make Signals Fixture-Safe

**Date:** 2026-05-25 migration work  
**Decision:** Signals that create related rows must return early when `kwargs.get("raw")` is true.

**Why:**

- `loaddata` saves objects with `raw=True`.
- During fixture loading, related objects may not exist yet.
- Signal side effects can corrupt imports or fail migrations.

**Implications:**

- Any future signal must include a raw-load guard if it touches related data.
- Test fixture loading if adding non-trivial signals.

## D-008: Establish SQLite Test Baseline

**Date:** 2026-06-01  
**Decision:** The default development test command uses SQLite and explicit `DEBUG=True`.

**Why:**

- The local `.env` may select MySQL.
- Sandbox/local permission restrictions can block MySQL sockets.
- Tests should be fast and deterministic for day-to-day development.

**Command:**

```bash
env DB_ENGINE=sqlite DEBUG=True ./env/bin/python manage.py test --verbosity 1
```

**Implications:**

- Use `override_settings(DEBUG=True, SECURE_SSL_REDIRECT=False)` in route tests.
- Use locmem email backend in email tests.
- Add MySQL-specific runs only when validating database behavior.

## D-009: Use Temporary Media Roots In Upload Tests

**Date:** 2026-06-01  
**Decision:** Tests that upload images should use a temporary `MEDIA_ROOT`.

**Why:**

- Upload tests should not pollute project `media/`.
- Failed tests should not leave persistent files.

**Implications:**

- Future upload tests should follow the `posts/tests.py` pattern.
- File deletion behavior should assert against temp paths.

## D-010: Fix Contact Email Template Path

**Date:** 2026-06-01  
**Decision:** `ContactFormView` renders `general/emails/notification_email.html`.

**Why:**

- The previous path `emails/notification_email.html` did not match the template tree.
- The contact form test exposed the mismatch.

**Implications:**

- Contact emails now use the same existing branded notification template path as the rest of the app.
- If email templates are reorganized, update tests and this decision.

## D-011: Canal Oficial Institucional Ágora y Asignación Forzada en Registro

**Date:** 2026-09-03  
**Decision:** `Ágora` (`slug="agora"`) se define como el canal institucional exclusivo de la dirección/junta. Se asigna automáticamente a todo nuevo usuario en `profiles/signals.py` como su primera terapia y se aplicó una migración de datos histórica (`0010_assign_agora_to_all_profiles`) a todas las cuentas preexistentes.

**Why:**
- Evita que los comunicados oficiales queden invisibles si un usuario olvida o no sabe que debe suscribirse manualmente a Ágora.
- Garantiza difusión 100% universal para convocatorias, normativas y avisos institucionales.

**Implications:**
- Todo nuevo usuario registrado tendrá garantizado el canal en `user.profile.hobbies`.
- Los tests de usuario deben contemplar que `profile.hobbies.filter(slug='agora').exists()` es `True` por defecto.

## D-012: Restricción de Publicación en Ágora a Usuarios Staff (`is_staff`)

**Date:** 2026-09-03  
**Decision:** La selección de `Ágora` en formularios de publicación (`PostCreateForm`, `EventForm`, etc.) está filtrada en backend. Si el usuario autenticado no tiene `is_staff=True`, la categoría Ágora es excluida de los querysets del campo del formulario y rechazada en validación.

**Why:**
- Solo administradores y miembros de la junta directiva deben tener autoridad para emitir mensajes oficiales con la identidad institucional.

**Implications:**
- Los usuarios regulares nunca verán Ágora como opción seleccionable para sus publicaciones individuales.
- El backend rechaza cualquier manipulación maliciosa de `category_id`.

## D-013: Priorización de Contenidos Institucionales mediante `Case/When` en el ORM

**Date:** 2026-09-03  
**Decision:** En lugar de realizar consultas separadas y concatenar listas en Python (lo que destruiría la paginación del ORM y la eficiencia de memoria), las publicaciones, eventos y artículos se ordenan anotando condicionalmente `is_agora = Case(When(category__slug="agora", then=Value(1)), default=Value(0), output_field=IntegerField())` y ordenando por `("-is_agora", "-created_at")`.

**Why:**
- Permite que los comunicados oficiales aparezcan **fijados al inicio (índice 0)** de las secciones de la Home y Exploración de Publicaciones, sin perder la evaluación perezosa (*lazy evaluation*), `select_related`, `prefetch_related` ni `LIMIT/OFFSET`.

**Implications:**
- Las consultas permanecen en una sola instrucción SQL optimizada.
- Los tests verifican que objetos con `slug="agora"` preceden a objetos más recientes de otras categorías.

## D-014: Propiedades de Extracción y Sanitización de Texto Plano en Modelos

**Date:** 2026-09-03  
**Decision:** Implementar `@property plain_text_summary` (`Article`), `@property plain_text_caption` (`Posts`) y `@property plain_text_description` (`Event`) a nivel de modelo para el renderizado en tarjetas resumen, en lugar de confiar en el filtro de plantilla `striptags`.

**Why:**
- Los editores enriquecidos (TinyMCE) producen entidades HTML (`&eacute;`, `&nbsp;`, `&oacute;`). El filtro `striptags` no decodifica entidades y elimina `<br>` sin agregar espacios, pegando palabras adyacentes (`primaveralLa`).
- Las propiedades en el modelo centralizan la sustitución de bloques con espacios, eliminación de HTML, decodificación vía `html.unescape()` y normalización de espacios, asegurando texto 100% natural.

**Implications:**
- Las tarjetas resumen de toda la plataforma usan estas propiedades antes del filtro `truncatewords`/`truncatechars`.

## D-015: Arquitectura de Alto Contraste en Modo Oscuro para Bloques y Navegación

**Date:** 2026-09-03  
**Decision:** Eliminar la clase utilitaria `bg-light` de contenedores de nivel superior (`.recommended-events-box` y `.nav-pills-hubs`). En modo oscuro, estos contenedores adoptan `var(--bs-body-bg)`, borde `1.5px solid var(--hubs-primary)` (`#2ba1ab`), textos en `#ffffff` y contadores de insignias con fondo blanco y tipografía en color corporativo.

**Why:**
- Bootstrap 5 asigna a `.bg-light` un valor con `!important` que genera recuadros descoloridos en modo oscuro, rompiendo la inmersión visual.

**Implications:**
- Se mantiene perfecta armonía visual entre bloques contiguos en la Home.
- Las insignias y textos inactivos conservan máxima legibilidad (accesibilidad WCAG AA).


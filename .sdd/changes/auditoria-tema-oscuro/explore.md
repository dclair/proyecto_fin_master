# Informe de Auditoría y Diagnóstico Arquitectónico: Modo Oscuro (Dark Theme) en Hubs & Clicks

- **Fecha:** 22 de Noviembre de 2026
- **Autor:** Senior Software & Frontend Architect (15+ años de experiencia, GDE & MVP)
- **Alcance:** Django Templates (63 archivos), CSS Global (`static/css/style.css`), JavaScript de Tema (`theme-toggle.js`, `layout.html`), Microfrontend de React (`frontend/src/`) y Componentes de Terceros (TomSelect, TinyMCE).
- **Estado:** EXPLORATION COMPLETE / READY FOR DECISION
- **Destino del Artefacto:** `.sdd/changes/auditoria-tema-oscuro/explore.md`

---

## 1. Resumen Ejecutivo (Executive Summary)

Se realizó una auditoría forense y arquitectónica exhaustiva sobre la implementación del Tema Oscuro en la plataforma **Hubs & Clicks**.

El diagnóstico es contundente: **La implementación actual del Tema Oscuro está rota a nivel conceptual y arquitectónico, sostenida por una acumulación de parches sintomáticos (*patch-over-patch*) sobre un HTML que arrastra vicios de Bootstrap 4.**

Aunque el proyecto incluye Bootstrap 5.3.2 (que posee un motor nativo de *Color Modes* de primer nivel basado en CSS Custom Properties y utilidades semánticas), la aplicación apenas aprovechó el interruptor (`data-bs-theme="dark"` en `<html>`). Al no haberse realizado una migración semántica en las plantillas, se generó un "Frankenstein visual":
1. **87 ocurrencias no saneadas de `text-dark`** que colapsan el ratio de contraste a niveles prácticamente ciegos (texto gris/negro `#212529` sobre fondo `#0f1813` o `#15221b`, ratio ~1.15:1, violando ampliamente el estándar WCAG AA de 4.5:1).
2. **113 contenedores con fondos rígidos claros (`bg-white` y `bg-light`)**, provocando "manchas blancas" (efecto *flashbang*) en cabeceras de tarjetas, filtros de eventos, modales y secciones completas de perfil.
3. **Parches CSS desesperados en `style.css`** (como `.dark-mode-text-dark`, que **fuerza texto oscuro en modo oscuro** para que se pueda leer sobre burbujas de comentarios que nunca se migraron de `bg-light`, o la inversión semántica absurda donde `--hubs-dark: #e1eae4;`).
4. **Desconexión total del Microfrontend React (`ChatApp`)**, el cual no solo ignora el tema del host de Django, sino que fuerza explícitamente `data-bs-theme="light"` en su portal, manteniendo colores quemados de una versión antigua (`#0b5961`, `#fff`).
5. **Componentes embebidos ciegos al tema** (TomSelect forzado a `#fff !important` mediante etiquetas `<style>` locales, y TinyMCE cargando el skin claro por defecto).

A continuación se detalla la radiografía técnica, el catálogo forense de incidencias y la comparativa rigurosa entre las dos alternativas de solución (Saneamiento Semántico Bootstrap 5.3 vs Re-arquitectura Completa).

---

## 2. Radiografía de la Implementación Actual

### 2.1. Conmutación y Persistencia (Mecanismo Global)
- **Ubicación del script anti-FOUC:** `aficionados_network/templates/general/layout.html` (Líneas 26-36).
  - Un IIFE síncrono en `<head>` lee `localStorage.getItem('theme')` o evalúa `window.matchMedia('(prefers-color-scheme: dark)')` y aplica `document.documentElement.setAttribute('data-bs-theme', theme)`.
  - **Evaluación:** La prevención de FOUC está bien resuelta.
- **Controlador del Interruptor:** `static/js/theme-toggle.js` (Líneas 1-19).
  - Escucha el click en `#themeToggleBtn`, alterna entre `'light'` y `'dark'`, actualiza `localStorage` y conmuta clases de íconos en `#themeIcon`.
  - **Falla Arquitectónica:** No emite ningún evento (`CustomEvent`, `window.dispatchEvent`), ni sincroniza con componentes desacoplados. Si el usuario cambia la preferencia de su sistema operativo en caliente, la aplicación no reacciona porque no hay listener de `matchMedia.addEventListener('change', ...)`.

### 2.2. Arquitectura de Tokens y Variables CSS (`static/css/style.css`)
El archivo define dos sistemas en conflicto directo:

```css
/* style.css:5-42 (:root - Tema Claro) */
:root {
    --bs-primary: #234938;
    --hubs-primary: var(--bs-primary);
    --hubs-dark: #202722;
    --hubs-light: #f8f9f6;
    --hubs-card-bg: #ffffff;
}

/* style.css:61-90 ([data-bs-theme="dark"]) */
[data-bs-theme="dark"] {
    --bs-primary: #52a378;
    --bs-body-bg: #0f1813;
    --bs-body-color: #e1eae4;
    --bs-card-bg: #15221b;
    --bs-border-color: rgba(255, 255, 255, 0.08);

    /* Inversión destructiva de nombres */
    --hubs-dark: #e1eae4;   /* ¡Un token llamado DARK vale BLANCO/VERDE CLARO! */
    --hubs-light: #0f1813;  /* ¡Un token llamado LIGHT vale NEGRO! */
    --hubs-card-bg: #15221b;
}
```

#### Deficiencias Críticas de Tokens:
1. **Destrucción de la Semántica de Variables:** Nombrar `--hubs-dark` a un color claro en dark mode viola el principio de diseño de tokens. Los tokens deben ser contextuales (`--surface-ground`, `--surface-card`, `--text-primary`) o universales, nunca invertir el significado literal del nombre.
2. **Tokens Nativos de Bootstrap 5.3 Incompletos:**
   No se definieron overrides para tokens fundamentales de Bootstrap 5.3 en modo oscuro:
   - `--bs-secondary-bg` (usado por `bg-body-secondary`)
   - `--bs-tertiary-bg` (usado por `bg-body-tertiary`)
   - `--bs-secondary-color` (usado por `text-body-secondary`)
   - `--bs-tertiary-color`
   - `--bs-emphasis-color`
   - `--bs-light` / `--bs-light-rgb` / `--bs-dark` / `--bs-dark-rgb`
   Al omitirlos, cualquier componente estándar de Bootstrap recurre a los grises genéricos (`#2b3035`), desentonando con la paleta de autor elegida (Ciprés/Bambú: `#0f1813` y `#15221b`).
3. **Colisión en el Footer:**
   - En `style.css:468`: `footer { background-color: white; }` (forzado en CSS).
   - En `aficionados_network/templates/_includes/_footer.html:1`: `<footer class="bg-dark text-light mt-5 pt-5 pb-4">`.
   - Como `.bg-dark` (`(0,1,0)`) vence al selector de etiqueta `footer` (`(0,0,1)`), el footer permanece negro carbón `#212529` en modo claro y en modo oscuro, completamente ajeno a las variables del tema.

---

## 3. Catálogo Forense de Problemas y Patrones Tóxicos

### 3.1. Resumen Cuantitativo del Escaneo en Plantillas

| Patrón / Clase Rígida | Ocurrencias Totales | Archivos Afectados | Impacto en Modo Oscuro |
| :--- | :---: | :---: | :--- |
| `text-dark` (No saneados) | **87** | **27** | **Texto casi invisible / Contraste nulo (~1.15:1)** |
| `text-dark` (Parcheados con hack) | 22 | 4 | Inconsistencia de mantenimiento; código duplicado |
| `bg-light` | **76** | **24** | **Cajas blancas/grises luminosas ("manchas")** |
| `bg-white` | **37** | **18** | **Rectángulos blancos cegadores sobre fondo oscuro** |
| `text-muted` (Sin migrar) | **242** | **45** | Ilegible si queda dentro de cajas claras parcheadas |
| `data-bs-theme="light"` forzado en React | **1** | **1** | **Chat desacoplado, inmune al cambio de tema** |
| TomSelect `<style>` inline rígidos | **2** | **2** | **Selectores con `#fff !important`** |

---

### 3.2. Patrón 1: Texto Oscuro sobre Fondo Oscuro (Contraste Nulo / Ilegible)

El estándar WCAG 2.1 AA exige un contraste mínimo de **4.5:1** para texto normal y **3:1** para texto grande o elementos gráficos.
En Bootstrap 5.3, `.text-dark` aplica:
```css
.text-dark {
    --bs-text-opacity: 1;
    color: rgba(var(--bs-dark-rgb), var(--bs-text-opacity)) !important;
}
```
Donde `--bs-dark-rgb` es `33, 37, 41` (`#212529`).
Cuando este texto se renderiza sobre `--bs-body-bg: #0f1813` o `--bs-card-bg: #15221b`:
- **Luminancia de fondo:** `0.016`
- **Luminancia de texto:** `0.018`
- **Ratio de Contraste resultante: 1.15 : 1 (ILEGIBLE)**

#### Casos de Estudio Concretos:
1. **Títulos de Posts en Feed Principal y Detalle:**
   - [aficionados_network/templates/_includes/_post.html#L115](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/aficionados_network/templates/_includes/_post.html#L115):
     ```html
     <a href="{% url 'posts:post_detail' post.pk %}" class="text-decoration-none text-dark">
         <h6 class="fw-bold mb-1 fs-xs">{{ post.title|default:"" }}</h6>
     </a>
     ```
     *Efecto:* El título del post en la card oscura es un bloque negro sobre verde oscuro. No se puede leer el contenido.
2. **Nombres de Usuario y Enlaces de Perfil:**
   - [aficionados_network/templates/_includes/_post.html#L10](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/aficionados_network/templates/_includes/_post.html#L10):
     `<a href="..." class="text-decoration-none text-dark d-flex align-items-center">`
   - [profiles/templates/profiles/partials/_profile_list_items.html#L25](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/profiles/templates/profiles/partials/_profile_list_items.html#L25):
     `<a href="..." class="text-decoration-none text-dark fw-bold">`
3. **Indicadores de Nivel en Home:**
   - [aficionados_network/templates/general/home.html#L123](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/aficionados_network/templates/general/home.html#L123):
     ```html
     <p class="... {% if event.level == 'beginner' %}text-success{% elif event.level == 'intermediate' %}text-warning{% elif event.level == 'advanced' %}text-danger{% elif event.level == 'expert' %}text-dark{% else %}text-info{% endif %}">
     ```
     *Efecto:* Todos los eventos con nivel "Experto" son etiquetados con `text-dark`, desapareciendo por completo de la vista del usuario en modo oscuro.
4. **Artículos de la Biblioteca y Marketplace:**
   - [library/templates/library/article_list.html#L56](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/library/templates/library/article_list.html#L56):
     `<a href="..." class="text-decoration-none text-dark">{{ article.title }}</a>`
   - [marketplace/templates/marketplace/listing_list.html#L77](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/marketplace/templates/marketplace/listing_list.html#L77):
     `<a href="..." class="text-decoration-none text-dark">{{ listing.title }}</a>`

---

### 3.3. Patrón 2: Manchas Blancas ("Flashbangs" / Fondos Rígidos Inmutables)

En Bootstrap 5.3, `.bg-white` aplica `background-color: #fff !important` sin importar el valor de `data-bs-theme`.

#### Casos de Estudio Concretos:
1. **Cabeceras de Cards en el Feed:**
   - [aficionados_network/templates/_includes/_post.html#L7](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/aficionados_network/templates/_includes/_post.html#L7):
     ```html
     <div class="card h-100 shadow-sm border-0 card-hubs rounded-4 overflow-hidden">
         <div class="card-header bg-white py-2 border-bottom-0">
     ```
     *Efecto:* La card adquiere el fondo oscuro `--bs-card-bg: #15221b`, pero la cabecera es una franja blanca incandescente en la parte superior. Visualmente aberrante.
2. **Caja Completa de "Bio y Terapias" en Perfil de Usuario:**
   - [profiles/templates/profiles/profile.html#L132](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/profiles/templates/profiles/profile.html#L132):
     ```html
     <div class="bg-white p-3 border border-2 border-hubs rounded shadow-sm mb-4 text-dark">
         <h6 class="fw-bold small text-uppercase text-dark mb-1">Sobre mí</h6>
         <div class="mb-0 small text-dark">{{ user_profile.bio|sanitize_html }}</div>
         <h6 class="fw-bold small text-uppercase text-dark mb-2">Mis Terapias</h6>
         <span class="badge border text-dark bg-light fw-normal p-2">...</span>
     </div>
     ```
     *Efecto:* Un bloque masivo completamente blanco con texto negro en el centro exacto del perfil en modo oscuro.
3. **Columna Lateral en Detalle del Evento:**
   - [aficionados_network/templates/posts/event_detail.html#L141](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/aficionados_network/templates/posts/event_detail.html#L141):
     ```html
     <div class="col-lg-4 bg-white border-start d-flex align-items-center">
     ```
     *Efecto:* En desktop, un tercio de la pantalla queda fijado en blanco pleno mientras los otros dos tercios son oscuros.
4. **Formularios de Autenticación:**
   - [aficionados_network/templates/general/register.html#L12](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/aficionados_network/templates/general/register.html#L12):
     `<div class="card-header bg-white text-center py-3"><h1 class="h4 mb-0 text-dark">Regístrate</h1></div>`
   - [aficionados_network/templates/general/password_reset/form.html#L11](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/aficionados_network/templates/general/password_reset/form.html#L11): Idéntico patrón.
5. **Panel de Filtros en Listado de Eventos:**
   - [aficionados_network/templates/posts/event_list.html#L22](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/aficionados_network/templates/posts/event_list.html#L22):
     `<div class="card-body bg-light rounded border-start border-hubs border-4">`
     Contiene `.input-group-text bg-white` combinados con inputs `.form-control` que en modo oscuro son oscurecidos por CSS. El resultado es un input mitad blanco (el ícono) y mitad negro (el campo de texto).

---

### 3.4. Patrón 3: La Anti-Arquitectura "Patch-over-Patch"

En lugar de sanear las plantillas a nivel semántico, desarrolladores anteriores intentaron tapar los síntomas agregando clases "hack" en `style.css`:
- `.text-dark-mode-white` (`style.css:378`)
- `.text-dark-mode-hubs` (`style.css:382`)
- `.dark-mode-text-dark` (`style.css:386`)
- `.dark-mode-text-navbar` (`style.css:390`)
- `.dark-mode-border` (`style.css:394`)

#### El disparate de `.dark-mode-text-dark`:
Observen este fragmento real en [aficionados_network/templates/posts/post_detail.html#L190-L195](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/aficionados_network/templates/posts/post_detail.html#L190-L195):
```html
<div class="bg-light p-3 rounded shadow-sm border-0 dark-mode-text-dark">
    <div class="d-flex justify-content-between align-items-start">
        <strong class="text-dark dark-mode-text-dark">{{ comment.user.username }}</strong>
        <small class="text-muted dark-mode-text-dark">{{ comment.created_at|timesince }}</small>
    </div>
    <p class="mb-0 mt-1">{{ comment.comment }}</p>
</div>
```
Y en `style.css:386`:
```css
[data-bs-theme="dark"] .dark-mode-text-dark {
    color: #212529;
}
```
**Análisis del disparate:**
Como la burbuja de comentario tiene `bg-light` (y por ende en dark mode no se oscurece adecuadamente), los desarrolladores inventaron una clase que **obliga al texto a mantenerse negro `#212529` cuando el usuario pide explícitamente modo oscuro**. Es un contra-sentido arquitectónico: forzar texto oscuro en dark mode para compensar la pereza de no haber cambiado un `bg-light` por `bg-body-tertiary`.

---

### 3.5. Patrón 4: El Microfrontend de React (`ChatApp`) Desacoplado

El chat flotante de React está montado en `document.body` vía `createPortal`.

1. **Forzado Explícito a Modo Claro:**
   En [frontend/src/ChatApp.tsx#L265-L282](file:///home/dclair/Documentos/MASTER_FULLSTACK/MIS_PROYECTOS/PROYECTO_FIN_MASTER_V2/frontend/src/ChatApp.tsx#L265-L282):
   ```tsx
   <div
       ref={panelRef}
       className="chat-panel shadow-lg"
       data-bs-theme="light"   // <--- ¡FORZADO HARDCODED A LIGHT!
       style={{
           backgroundColor: 'white',
           border: '1px solid #e5e5e5',
           ...
       }}
   >
   ```
2. **Estilos Hardcodeados en CSS y TSX:**
   En `frontend/src/ChatApp.css` y subcomponentes (`GroupParticipants.tsx`, `MessageTimeline.tsx`):
   - Cabecera: `background-color: #0b5961; color: white;` (color verde azulado antiguo que ni siquiera coincide con el `--hubs-primary` actual `#234938`).
   - Lista de mensajes: `background-color: #fff;`
   - Burbujas ajenas: `background-color: #f1f3f5; color: #212529;`
   - Cero uso de variables CSS dinámicas.
3. **Cero Sincronización:**
   No existe ningún `MutationObserver` en el `<html data-bs-theme="...">` ni contexto de React que propague el tema del host hacia el microfrontend.

---

### 3.6. Patrón 5: Componentes de Terceros (TomSelect y TinyMCE)

1. **TomSelect (`post_create.html` y `event_form.html`):**
   Las plantillas inyectan en `<style>`:
   ```css
   .ts-control {
       background-color: #fff !important;
       border: 1px solid #dee2e6 !important;
   }
   .ts-dropdown .active {
       background-color: #f1f5f9 !important;
       color: #0f172a !important;
   }
   ```
   *Efecto:* Destruye cualquier intento de Bootstrap de tematizar los desplegables de categorías y tags.
2. **TinyMCE (`event_form.html`):**
   ```javascript
   tinymce.init({
       selector: '#id_description',
       content_style: 'body { font-family:Helvetica,Arial,sans-serif; font-size:16px }',
       // Falta: skin: 'oxide-dark', content_css: 'dark'
   });
   ```
   *Efecto:* El editor WYSIWYG se inicializa con iframe blanco brillante.

---

## 4. Diagnóstico Raíz (Root Cause Analysis)

La causa raíz no es una deficiencia técnica de Bootstrap ni una limitación de Django. Es un fallo metodológico en la evolución del software:

1. **Inercia de Clases No Semánticas (Mentalidad Bootstrap 4):**
   En Bootstrap 4 y versiones tempranas de 5, `bg-white`, `bg-light` y `text-dark` eran el estándar habitual para estructurar interfaces claras. Al actualizar a Bootstrap 5.3, la especificación oficial introdujo un cambio de paradigma:
   - Las utilidades de color pasaron a dividirse entre **absolutas** (`bg-white`, `bg-black`, `text-dark`) y **semánticas/reactivas al tema** (`bg-body`, `bg-body-secondary`, `bg-body-tertiary`, `text-body`, `text-body-secondary`, `text-body-emphasis`).
   - El equipo adoptó Bootstrap 5.3.2 pero continuó maquetando con la mentalidad de Bootstrap 4.
2. **Falta de un Contrato de Tokens Unificado:**
   Se crearon variables `--hubs-*` encima de `--bs-*` sin definir un mapa de derivación claro. Al llegar el modo oscuro, en vez de mapear `--hubs-surface` y `--hubs-text`, invirtieron el valor de `--hubs-dark` y añadieron parches ad-hoc.
3. **Aislamiento No Gobernado del Microfrontend React:**
   El componente React se integró como una "isla" de Vite sin un protocolo de comunicación de diseño (*Design Token Contract*) con el host de Django. Para evitar que el CSS del chat se rompiera, se le clavó `data-bs-theme="light"` de forma provisional y quedó en el olvido técnico.

---

## 5. Evaluación de Alternativas de Solución y Tradeoffs

Como Senior Architect con más de 15 años en la trinchera, evalúo rigurosamente los dos caminos posibles para que el equipo tome una decisión informada.

```
+-----------------------------------------------------------------------------------+
|                           MATRIZ DE DECISIÓN ARQUITECTÓNICA                       |
+------------------------------------+-----------------------+----------------------+
| Criterio                           | Camino A:             | Camino B:            |
|                                    | Saneamiento Semántico | Re-arquitectura      |
|                                    | Bootstrap 5.3         | Design Tokens Custom |
+------------------------------------+-----------------------+----------------------+
| Apego a Estándares del Stack       | 100% Nativo BS 5.3    | 0% (Bypass total BS) |
| Volumen de Archivos Afectados      | ~45 HTML, 1 CSS, 3 TSX| 63 HTML, 5 CSS, 8 TSX|
| Riesgo de Regresión Visual         | Muy Bajo              | Alto                 |
| Compatibilidad con Crispy Forms    | Total (Plug & Play)   | Ruptura / Overrides  |
| Tiempo de Ejecución Estimado       | 1 a 2 días            | 1 a 2 semanas        |
| Mantenibilidad a Largo Plazo       | Alta (Docs oficiales) | Compleja (Docs ad-hoc)|
| Complejidad de Deuda Técnica       | Elimina hacks previos | Riesgo de nueva deuda|
+------------------------------------+-----------------------+----------------------+
```

### CAMINO A: Saneamiento Quirúrgico & Migración Semántica Bootstrap 5.3 (RECOMENDADO)

#### En qué consiste:
1. **Regla de Oro en Plantillas:**
   - `bg-white` en tarjetas/contenedores $\rightarrow$ Eliminar la clase o reemplazar por `bg-body` / `bg-body-secondary`.
   - `bg-light` en filtros y bloques auxiliares $\rightarrow$ Reemplazar por `bg-body-tertiary`.
   - `text-dark` $\rightarrow$ Reemplazar por `text-body` o `text-body-emphasis`.
   - `text-muted` $\rightarrow$ Reemplazar por `text-body-secondary`.
   - `border-light` / `border-dark` $\rightarrow$ Reemplazar por `border` o `border-secondary-subtle`.
   - Erradicar las 5 clases de parche en templates y CSS (`.text-dark-mode-white`, `.text-dark-mode-hubs`, `.dark-mode-text-dark`, etc.).
2. **Completar la Paleta Semántica en `style.css` (`[data-bs-theme="dark"]`):**
   ```css
   [data-bs-theme="dark"] {
       --bs-primary: #52a378;
       --bs-primary-rgb: 82, 163, 120;
       --bs-body-bg: #0f1813;
       --bs-body-color: #e1eae4;
       --bs-card-bg: #15221b;
       --bs-secondary-bg: #192a21;
       --bs-tertiary-bg: #22372c;
       --bs-secondary-color: #9cb3a4;
       --bs-tertiary-color: #6d8576;
       --bs-emphasis-color: #ffffff;
       --bs-border-color: rgba(255, 255, 255, 0.08);
       --bs-border-color-translucent: rgba(255, 255, 255, 0.08);
   }
   ```
3. **Normalizar Footer:**
   Remover `bg-dark` fijo del template `_footer.html` y remover `footer { background-color: white; }` en CSS. Asignarle `bg-body-tertiary border-top text-body-secondary`.
4. **Sincronización del Microfrontend React (`ChatApp`):**
   - Eliminar `data-bs-theme="light"` y estilos fijos inline de `ChatApp.tsx`.
   - Crear un hook ligero `useHostTheme()` que observe el atributo `data-bs-theme` de `document.documentElement` con un `MutationObserver`.
   - Adaptar `ChatApp.css` para consumir las variables de Bootstrap (`var(--bs-body-bg)`, `var(--bs-card-bg)`, `var(--bs-body-color)`).
5. **Componentes Externos:**
   - TomSelect: Reemplazar reglas de fondo blanco por variables de control (`background-color: var(--bs-body-bg); color: var(--bs-body-color);`).
   - TinyMCE: Inicializar dinámicamente con `skin: isDark ? 'oxide-dark' : 'oxide'` y `content_css: isDark ? 'dark' : 'default'`.

#### Pros:
- Aprovecha al 100% la inversión ya hecha en Bootstrap 5.3.
- Cero bibliotecas adicionales ni aumento en el bundle JS.
- Mantiene la compatibilidad natural con `django-crispy-forms` (paquete `crispy-bootstrap5`).
- Soluciona todos los contrastes respetando WCAG AA en menos de 2 días de trabajo ordenado.

#### Contras:
- Requiere tocar metódicamente ~45 archivos de plantillas HTML para sustituir las clases fijas.

---

### CAMINO B: Re-arquitectura Completa con Design Tokens / Tema Custom

#### En qué consiste:
- Ignorar o neutralizar el sistema de color modes de Bootstrap 5.3.
- Definir una especificación formal de tokens semánticos propios en un archivo CSS independiente (`tokens.css`):
  `--color-surface-canvas`, `--color-surface-card`, `--color-text-title`, `--color-interactive-primary`, etc.
- Reescribir todos los estilos de tarjetas, listas, tablas y modales con clases BEM propias (`.hc-card`, `.hc-header`, `.hc-table`).
- Desacoplar el chat de React implementando un Theme Context propio basado en styled-components o CSS modules.

#### Pros:
- Control tipográfico y cromático 100% quirúrgico e independiente de Bootstrap.
- Ideal si la plataforma planea eliminar Bootstrap a medio plazo para migrar a Tailwind o arquitectura headless.

#### Contras:
- **Sobrecarga de ingeniería desproporcionada (*Overengineering*):** El proyecto es una aplicación Django monolítica con un microfrontend. Reescribir el CSS y los templates para crear un Design System desde cero requeriría entre 2 y 3 semanas de esfuerzo.
- **Ruptura de `django-crispy-forms`:** Crispy Forms inyecta clases estándar de Bootstrap 5. Bypasear Bootstrap obligaría a escribir templates personalizados de crispy para cada widget.
- **Alto riesgo de regresión:** Probabilidad crítica de desalineaciones en móviles, responsive y estados interactivos de Bootstrap.

---

### Recomendación Profesional del Arquitecto

> **Veredicto:** **ADOPTAR EL CAMINO A (Saneamiento Semántico Bootstrap 5.3).**
> 
> "No inventemos la rueda cuando ya tenemos un Ferrari con las ruedas desinfladas. Bootstrap 5.3 tiene uno de los mejores motores de temas CSS modernos del ecosistema. Romper todo para hacer tokens custom desde cero (Camino B) sería un capricho de sobreingeniería que solo inflará horas sin aportar ningún beneficio tangible al usuario final. El Camino A es limpio, ataca la causa raíz, extirpa la deuda técnica de los parches y deja la plataforma lista para producción con estándares WCAG AA impecables."

---

## 6. Plan de Acción Propuesto (Roadmap de Fases)

En caso de que el usuario apruebe avanzar con la solución recomendada (Camino A), se propone estructurar la ejecución en 4 fases ordenadas:

### Fase 1: Cimientos CSS y Variables de Marca
- Limpiar `static/css/style.css`:
  - Definir la paleta semántica completa en `[data-bs-theme="dark"]` (`--bs-secondary-bg`, `--bs-tertiary-bg`, etc.).
  - Erradicar la inversión de `--hubs-dark` y normalizar tokens de marca.
  - Eliminar las clases hack: `.text-dark-mode-white`, `.text-dark-mode-hubs`, `.dark-mode-text-dark`, etc.
  - Configurar estilos reactivos para TomSelect y inputs de formularios.

### Fase 2: Saneamiento de Templates Core y Layout Global
- `aficionados_network/templates/general/layout.html` y `_header.html`:
  - Despachar evento `themeChanged` al conmutar tema.
  - Limpiar dropdowns y badges del navbar.
- `aficionados_network/templates/_includes/_footer.html`:
  - Migrar a `bg-body-tertiary` y `text-body-secondary`.
- Partials compartidos: `_post.html`, `_event_card.html`, `_event_card_home.html`, `_messages.html`.

### Fase 3: Saneamiento Quirúrgico de Vistas por Aplicación
- **Posts & Events:** `post_detail.html`, `post_create.html`, `post_update.html`, `event_list.html`, `event_detail.html`, `my_participations.html`, `my_events.html`, `hobby_hub.html`.
- **Profiles:** `profile.html`, `profile_edit.html`, `profile_detail.html`, `profile_list.html`.
- **Library & Marketplace:** `article_list.html`, `article_detail.html`, `listing_list.html`, `listing_detail.html`.
- **Auth & General:** `register.html`, `password_reset/*.html`.

### Fase 4: Microfrontend React & Componentes Externos
- `frontend/src/ChatApp.tsx`:
  - Remover `data-bs-theme="light"` y estilos hardcodeados.
  - Implementar hook `useHostTheme()`.
- `frontend/src/ChatApp.css` y subcomponentes de React:
  - Vincular fondos y textos a las variables CSS de Bootstrap.
- Sincronizar TinyMCE en `event_form.html`.

---

## 7. Riesgos y Mitigaciones (Risks)

1. **Riesgo de Regresión Visual en Modo Claro:**
   - *Riesgo:* Al cambiar `bg-white` a `bg-body`, si el fondo global del body no es blanco (en Hubs es `#f8f9f6`), las tarjetas podrían mimetizarse con el fondo si no tienen borde o elevación.
   - *Mitigación:* Usar `bg-body` para el fondo global y asegurar que las cards dependan de `--bs-card-bg` (`#ffffff` en light, `#15221b` en dark) con sus respectivos bordes orgánicos `--bs-border-color`.
2. **Riesgo de Cache de Assets Estáticos:**
   - *Riesgo:* Que navegadores de usuarios retengan la versión vieja de `style.css` o `main.js`.
   - *Mitigación:* Los templates ya usan versionado por query string (`style.css?v=3.1`) y Vite gestiona hash de bundles en producción.
3. **Riesgo de Incompatibilidad con extensiones de TinyMCE:**
   - *Riesgo:* Cambiar el skin a `oxide-dark` puede requerir que los assets de TinyMCE CDN soporten dicho skin.
   - *Mitigación:* Se validará en el CDN de TinyMCE la disponibilidad de `oxide-dark` antes de su invocación.

---

## 8. Siguiente Acción Recomendada (Next Recommended)

1. **Presentar este informe al usuario** para decisión final de arquitectura (Camino A vs Camino B).
2. Tras la aprobación, iniciar la fase de especificación y propuesta técnica SDD (`sdd-propose` / `sdd-spec` para el cambio `refactor-tema-oscuro-semantico`).

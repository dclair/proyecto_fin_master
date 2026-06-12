---
status: archived
topic: sdd/marketplace/archive-report
---

# SDD Archive Report: Marketplace

## Executive Summary
La funcionalidad de "Mercadillo de Profesionales" se ha completado exitosamente y ha sido integrada en el proyecto `aficionados_network`.
Se han implementado y verificado todos los hitos del ciclo SDD (Exploración, Propuesta, Tareas, Implementación y Verificación).

## Completed Work
1. **Modelos:** Se creó la aplicación aislada `marketplace` con los modelos `Listing` (anuncios) y `SellerReview` (sistema de reputación).
2. **Controladores y Rutas:** Vistas genéricas (CRUD) protegidas por `LoginRequiredMixin` y `UserPassesTestMixin`.
3. **Integración UI/Frontend:** 
   - Diseño de plantillas con Bootstrap 5 (`listing_list.html`, `listing_detail.html`, `listing_form.html`, `listing_confirm_delete.html`).
   - Integración nativa con la mensajería React pre-existente mediante el evento JavaScript `openChatWith`.
   - Incorporación de `TomSelect` en el formulario para búsquedas ligeras de terapias.
   - Refactorización de la barra de navegación para agrupar "Mercadillo", "Eventos" y "Profesionales" bajo un dropdown unificado ("Directorio").
   - Implementación de un badge dinámico (globito verde) a través de un Custom Template Tag para notificar anuncios activos.
4. **Usabilidad Adicional:** Mejora del grid de Bootstrap en las tarjetas de perfil (`_profile_list_items.html`) para evitar cortes de etiquetas, ajustando de `col-xl-2` a `col-lg-4 col-xl-3`, y mostrando explícitamente las terapias debajo del email.

## Artifacts Updated
- `marketplace/models.py`, `marketplace/views.py`, `marketplace/urls.py`, `marketplace/admin.py`, `marketplace/forms.py`
- `marketplace/templates/marketplace/*.html`
- `marketplace/templatetags/marketplace_tags.py`
- `aficionados_network/templates/_includes/_header.html`
- `profiles/templates/profiles/partials/_profile_list_items.html`
- `README.md`

## Next Recommendations
- Monitorear el rendimiento de las consultas `select_related` en listas masivas.
- Considerar purga automática de anuncios con más de X meses de antigüedad mediante tareas periódicas (Celery).

## Risks
Ningún riesgo inminente detectado. La reutilización del sistema de chat y la función genérica de validación de imágenes (`validate_image_size`) mantuvieron el sistema estable y DRY.

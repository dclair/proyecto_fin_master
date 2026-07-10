# Próximos Pasos (Pendientes)

**Estado Actual (08/07/2026):**
- Despliegue en Oracle Cloud (OCI) completado con éxito.
- Docker Compose corriendo con la base de datos MariaDB persistida en volúmenes.
- Archivo `.env.prod` asegurado y fuera de GitHub.
- Funcionalidades validadas en producción: Subida de imágenes locales con TinyMCE, manejo de errores de SMTP en contacto, ampliación de biografía a 1500 caracteres, y UI responsive.
- **NUEVO:** Backups automatizados configurados para MariaDB y `media_volume` mediante cronjob rotativo de 7 días.

**Para la próxima sesión:**
1. **Dominio y HTTPS:** Configurar un dominio real (ej. `.com`) y generar certificados SSL/TLS gratuitos usando Let's Encrypt / Certbot para Nginx.
2. **Mantenimiento General:** Monitorear logs de Django y revisar si hay configuraciones finas pendientes para producción (ej. desactivar caché en ciertas vistas, afinar gunicorn workers, etc).

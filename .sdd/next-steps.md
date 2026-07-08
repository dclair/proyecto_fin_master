# Próximos Pasos (Pendientes)

**Estado Actual (08/07/2026):**
- Despliegue en Oracle Cloud (OCI) completado con éxito.
- Docker Compose corriendo con la base de datos MariaDB persistida en volúmenes.
- Archivo `.env.prod` asegurado y fuera de GitHub.
- Funcionalidades validadas en producción: Subida de imágenes locales con TinyMCE, manejo de errores de SMTP en contacto, ampliación de biografía a 1500 caracteres, y UI responsive.

**Para la próxima sesión:**
1. **Dominio y HTTPS:** Configurar un dominio real (ej. `.com`) y generar certificados SSL/TLS gratuitos usando Let's Encrypt / Certbot para Nginx.
2. **Backups Automatizados:** Configurar un script o cronjob en OCI para hacer respaldos automáticos de la base de datos MariaDB y de los archivos de la carpeta `media/`.
3. **Mantenimiento General:** Monitorear logs de Django y revisar si hay configuraciones finas pendientes para producción (ej. desactivar caché en ciertas vistas, afinar gunicorn workers, etc).

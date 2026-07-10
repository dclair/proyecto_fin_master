#!/bin/bash

# ==============================================================================
# Script de Backup para Aficionados Network
# Este script realiza un volcado de la base de datos MariaDB y comprime los
# archivos multimedia (media).
# ==============================================================================

# Detener el script si hay algún error
set -e

# Configuración de rutas (Ajustar según necesidad en producción)
PROJECT_DIR="/home/ubuntu/PROYECTO_FIN_MASTER_V2"
BACKUP_DIR="/home/ubuntu/backups/aficionados_network"
ENV_FILE="$PROJECT_DIR/.env.prod"
DATE=$(date +"%Y%m%d_%H%M%S")
RETENTION_DAYS=7

# Crear el directorio de backups si no existe
mkdir -p "$BACKUP_DIR"

# Cargar variables de entorno (DB_USER, DB_PASSWORD, DB_NAME)
if [ -f "$ENV_FILE" ]; then
    export $(grep -v '^#' "$ENV_FILE" | xargs)
else
    echo "ERROR: No se encontró el archivo $ENV_FILE"
    exit 1
fi

echo "Iniciando backup ($DATE)..."

# 1. Backup de la Base de Datos (MariaDB)
DB_BACKUP_FILE="$BACKUP_DIR/db_backup_$DATE.sql.gz"
echo ">> Realizando volcado de la base de datos..."
# Usamos -T para deshabilitar la asignación pseudo-TTY ya que se ejecuta en cron
docker compose -f "$PROJECT_DIR/docker-compose.yml" exec -T db mariadb-dump \
    -u "$DB_USER" \
    -p"$DB_PASSWORD" \
    "$DB_NAME" | gzip > "$DB_BACKUP_FILE"

# 2. Backup de Archivos Multimedia (media_volume)
MEDIA_BACKUP_FILE="$BACKUP_DIR/media_backup_$DATE.tar.gz"
echo ">> Comprimiendo archivos multimedia..."
# Ejecutamos un comando en el contenedor web que ya tiene montado el media_volume
docker compose -f "$PROJECT_DIR/docker-compose.yml" run --rm \
    -v "$BACKUP_DIR:/backup_dest" \
    web tar czf "/backup_dest/media_backup_$DATE.tar.gz" -C /app/media .

echo ">> Backups creados exitosamente en $BACKUP_DIR"

# 3. Limpieza de Backups Antiguos
echo ">> Eliminando backups con más de $RETENTION_DAYS días de antigüedad..."
find "$BACKUP_DIR" -type f -name "*.gz" -mtime +$RETENTION_DAYS -exec rm {} \;

echo "Backup finalizado exitosamente."

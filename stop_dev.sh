#!/bin/bash

# ==============================================================================
# SCRIPT DE DETENCIÓN - PROYECTO FIN DE MASTER
# ==============================================================================
SESSION_NAME="TFM_Dev"

echo "🛑 Deteniendo todo el entorno de Hubs & Clicks..."

# 1. Matar la sesión de Tmux
if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    echo "🔫 Cerrando sesión de Tmux ($SESSION_NAME)..."
    tmux kill-session -t "$SESSION_NAME" 2>/dev/null
    echo "   ✔ Sesión de Tmux cerrada."
fi

# 2. Detener procesos de Django / Daphne
echo "🐍 Deteniendo Django / Daphne..."
pkill -f "python manage.py runserver" 2>/dev/null || true
pkill -f "daphne" 2>/dev/null || true

# 3. Detener Celery Worker y Beat
echo "🌿 Deteniendo Celery Worker y Beat..."
pkill -f "celery -A aficionados_network" 2>/dev/null || true
pkill -f "celery worker" 2>/dev/null || true
pkill -f "celery beat" 2>/dev/null || true

# 4. Detener Frontend (Vite / Node)
echo "⚡ Deteniendo Vite / Node frontend..."
pkill -f "vite" 2>/dev/null || true
pkill -f "node.*frontend" 2>/dev/null || true
if command -v fuser &>/dev/null; then
    fuser -k 5173/tcp 2>/dev/null || true
fi

# 5. Detener Redis
echo "🔴 Deteniendo Redis..."
pkill -f "redis-server" 2>/dev/null || true
sudo systemctl stop redis-server 2>/dev/null || sudo systemctl stop redis 2>/dev/null || sudo service redis-server stop 2>/dev/null || true

# 6. Detener Base de Datos (MySQL / MariaDB)
echo "🗄️  Deteniendo MySQL/MariaDB..."
sudo systemctl stop mariadb 2>/dev/null || sudo systemctl stop mysql 2>/dev/null || sudo service mariadb stop 2>/dev/null || sudo service mysql stop 2>/dev/null || true

# 7. Detener contenedores Docker de desarrollo si existieran activos
if command -v docker &>/dev/null; then
    if docker compose ps -q 2>/dev/null | grep -q .; then
        echo "🐳 Deteniendo contenedores Docker activos..."
        docker compose stop 2>/dev/null || true
    fi
fi

# 8. Verificación final de puertos liberados
echo "🔍 Verificando estado final de servicios..."
sleep 0.5
PORTS=(8000 5173 6379 3306)
NAMES=("Django (8000)" "Vite (5173)" "Redis (6379)" "MySQL/MariaDB (3306)")

for i in "${!PORTS[@]}"; do
    PORT="${PORTS[$i]}"
    NAME="${NAMES[$i]}"
    if ss -tuln 2>/dev/null | grep -q ":$PORT "; then
        echo "   ⚠️  $NAME sigue ocupado en el puerto $PORT."
    else
        echo "   ✔ $NAME detenido y puerto $PORT liberado."
    fi
done

echo "✅ Todo limpio y detenido. Hasta la próxima sesión de código."

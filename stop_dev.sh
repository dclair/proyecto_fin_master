#!/bin/bash

# ==============================================================================
# SCRIPT DE DETENCIÓN - PROYECTO FIN DE MASTER
# ==============================================================================
SESSION_NAME="TFM_Dev"

echo "🛑 Deteniendo todo el entorno..."

# 1. Matar la sesión de Tmux (esto también mata al servidor de Django y las ventanas)
echo "🔫 Matando la sesión de Tmux ($SESSION_NAME)..."
tmux kill-session -t $SESSION_NAME 2>/dev/null
pkill -f "python manage.py runserver" 2>/dev/null

echo "✔ Paneles y procesos de consola cerrados."

# 2. Detener la Base de Datos
echo "🗄️ Deteniendo MySQL/MariaDB..."
sudo systemctl stop mysql 2>/dev/null
sudo systemctl stop mariadb 2>/dev/null

echo "✅ Todo limpio. Hasta la próxima sesión de código."

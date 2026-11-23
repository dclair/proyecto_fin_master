#!/bin/bash

# ==============================================================================
# SCRIPT DE INICIO - PROYECTO FIN DE MASTER (VERSIÓN TMUX)
# ==============================================================================
SCRIPT_PATH="$(realpath "${BASH_SOURCE[0]}")"
PROJECT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"
SESSION_NAME="TFM_Dev"

cd "$PROJECT_DIR" || { echo "❌ Error: No se encontró el directorio del proyecto"; exit 1; }

echo "🏗️  Preparando el entorno de Hubs & Clicks..."

# 1. Asegurar Base de Datos (MariaDB / MySQL)
echo "🗄️  Iniciando MySQL/MariaDB..."
sudo systemctl start mariadb 2>/dev/null || sudo systemctl start mysql 2>/dev/null || sudo service mariadb start 2>/dev/null || sudo service mysql start 2>/dev/null || true

# Esperar brevemente a que el socket/puerto de BD responda
for i in {1..5}; do
    if mysqladmin ping --silent 2>/dev/null || ss -tuln 2>/dev/null | grep -q ":3306 "; then
        echo "   ✔ Base de datos lista en puerto 3306."
        break
    fi
    sleep 0.5
done

# 2. Asegurar Redis
echo "🔴 Asegurando Redis..."
if ! redis-cli ping &>/dev/null; then
    sudo systemctl start redis-server 2>/dev/null || sudo systemctl start redis 2>/dev/null || sudo service redis-server start 2>/dev/null || true
fi
if redis-cli ping &>/dev/null; then
    echo "   ✔ Redis activo en 127.0.0.1:6379."
else
    echo "   ℹ️ Redis se iniciará en su panel dedicado de Tmux."
fi

echo "🚀 Iniciando sesión Tmux ($SESSION_NAME)..."

# 3. Configurar Tmux
tmux has-session -t "$SESSION_NAME" 2>/dev/null

if [ $? != 0 ]; then
  # Crear nueva sesión en background con la primera ventana llamada "Servicios"
  tmux new-session -d -s "$SESSION_NAME" -n "Servicios" -c "$PROJECT_DIR"
  
  # Capturamos el ID único del primer panel (Django)
  PANE_DJANGO=$(tmux display-message -p -t "$SESSION_NAME:0" "#{pane_id}")
  tmux send-keys -t "$PANE_DJANGO" "cd '$PROJECT_DIR' && source env/bin/activate && python manage.py runserver" C-m
  
  # Panel Vite (Dividimos horizontalmente a la derecha)
  PANE_VITE=$(tmux split-window -h -P -F "#{pane_id}" -t "$PANE_DJANGO" -c "$PROJECT_DIR/frontend")
  tmux send-keys -t "$PANE_VITE" "cd '$PROJECT_DIR/frontend' && npm run dev" C-m
  
  # Panel Celery Worker (Dividimos verticalmente el panel izquierdo inferior)
  PANE_CELERY=$(tmux split-window -v -P -F "#{pane_id}" -t "$PANE_DJANGO" -c "$PROJECT_DIR")
  tmux send-keys -t "$PANE_CELERY" "cd '$PROJECT_DIR' && source env/bin/activate && celery -A aficionados_network worker -l info" C-m
  
  # Panel Redis (Dividimos verticalmente el panel derecho inferior)
  PANE_REDIS=$(tmux split-window -v -P -F "#{pane_id}" -t "$PANE_VITE" -c "$PROJECT_DIR")
  tmux send-keys -t "$PANE_REDIS" "if redis-cli ping &>/dev/null; then echo '🟢 Redis ya está activo en 127.0.0.1:6379'; redis-cli monitor; else redis-server; fi" C-m
  
  # Ventana 2: Consola libre para el desarrollador
  tmux new-window -t "$SESSION_NAME:1" -n "Terminal" -c "$PROJECT_DIR"
  tmux send-keys -t "$SESSION_NAME:1" "cd '$PROJECT_DIR' && source env/bin/activate && clear" C-m
  tmux send-keys -t "$SESSION_NAME:1" "echo '⚡ Terminal libre lista para usar con el venv activo.'" C-m
  tmux send-keys -t "$SESSION_NAME:1" "echo '📊 Django, Vite, Celery y Redis están en la ventana 0 (Atajo: Ctrl+b, 0)'" C-m
  
  # Seleccionar panel de Django en la ventana 0 por defecto
  tmux select-window -t "$SESSION_NAME:0"
  tmux select-pane -t "$PANE_DJANGO"
fi

# 4. Lanzar la interfaz para conectarse a la sesión
if [ -t 1 ]; then
  tmux attach -t "$SESSION_NAME"
else
  if command -v gnome-terminal &> /dev/null; then
      gnome-terminal --maximize --title="Hubs & Clicks Dev" -- tmux attach -t "$SESSION_NAME"
  elif command -v xterm &> /dev/null; then
      xterm -maximized -e "tmux attach -t $SESSION_NAME" &
  fi
fi

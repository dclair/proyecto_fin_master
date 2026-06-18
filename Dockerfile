# -----------------------------------
# STAGE 1: Build Frontend (Vite/React)
# -----------------------------------
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

# Copiar dependencias de node
COPY frontend/package*.json ./
RUN npm ci

# Copiar el código fuente del frontend
COPY frontend/ ./

# Construir (esto generará la carpeta /app/frontend/dist)
RUN npm run build

# -----------------------------------
# STAGE 2: Backend (Django/Daphne)
# -----------------------------------
FROM python:3.12-slim

# Evitar que python escriba .pyc y forzar stdout sin buffer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias del sistema operativo requeridas para compilar paquetes o usar mysqlclient
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código del proyecto
COPY . .

# Copiar los estáticos compilados desde la etapa de node
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Recolectar estáticos para Whitenoise/Nginx
# (Esto requiere SECRET_KEY falso para no fallar en build-time si settings lo exige)
RUN SECRET_KEY="build-key" python manage.py collectstatic --noinput

# Exponer el puerto para Daphne
EXPOSE 8000

# Comando para iniciar Daphne y servir Django + Channels
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "aficionados_network.asgi:application"]

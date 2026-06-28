FROM node:22-alpine AS frontend-builder

ARG NPM_REGISTRY=https://registry.npmmirror.com

WORKDIR /frontend

COPY frontend/package*.json ./
RUN npm config set registry ${NPM_REGISTRY} \
    && npm ci

COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim

ARG PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
ARG PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    CPYCMS_PORT=5000 \
    CPYCMS_DATABASE_FILE=/app/data/cpycms.db \
    CPYCMS_SQLITE_BUSY_TIMEOUT_MS=5000 \
    CPYCMS_SQLITE_CACHE_KB=20000 \
    CPYCMS_REFRESH_SEARCH_INDEX_ON_STARTUP=0 \
    CPYCMS_UPLOAD_FOLDER=/app/uploads \
    CPYCMS_LOG_DIR=/app/logs \
    CPYCMS_FRONTEND_DIST=/app/frontend/dist

WORKDIR /app

RUN python -m pip install --no-cache-dir --upgrade pip \
    -i ${PIP_INDEX_URL} \
    --trusted-host ${PIP_TRUSTED_HOST}
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt \
    -i ${PIP_INDEX_URL} \
    --trusted-host ${PIP_TRUSTED_HOST}

COPY backend /app/backend
COPY app.py /app/app.py
COPY manage.py /app/manage.py
COPY wsgi.py /app/wsgi.py
COPY gunicorn.conf.py /app/gunicorn.conf.py
COPY --from=frontend-builder /frontend/dist /app/frontend/dist

RUN mkdir -p /app/data /app/uploads /app/logs

EXPOSE 5000

CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn -c gunicorn.conf.py wsgi:application"]

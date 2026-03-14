# ── Build stage ────────────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/prod.txt

# ── Runtime stage ─────────────────────────────────────────────────────────────
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 && \
    rm -rf /var/lib/apt/lists/*

RUN addgroup --system app && adduser --system --ingroup app app

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .

RUN python manage.py collectstatic --noinput 2>/dev/null || true

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import socket; s=socket.create_connection(('localhost',8000)); s.close()"

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]

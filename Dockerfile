# Context Engineering Platform — production-oriented image
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN mkdir -p data data/manufacturing_outputs templates

EXPOSE 8000

# Orchestrators and `docker ps` can use this; Compose also defines a healthcheck.
HEALTHCHECK --interval=30s --timeout=6s --start-period=20s --retries=3 \
  CMD ["python", "-c", "import os,urllib.request; urllib.request.urlopen('http://127.0.0.1:'+os.environ.get('PORT','8000')+'/ready', timeout=5)"]

# PORT/HOST respected by uvicorn; many PaaS set PORT
CMD sh -c 'exec uvicorn main:app --host ${HOST:-0.0.0.0} --port ${PORT:-8000}'

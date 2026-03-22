# Context Engineering Platform — production-oriented image
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN mkdir -p data data/manufacturing_outputs templates

EXPOSE 8000

# PORT/HOST respected by uvicorn; many PaaS set PORT
CMD sh -c 'exec uvicorn main:app --host ${HOST:-0.0.0.0} --port ${PORT:-8000}'

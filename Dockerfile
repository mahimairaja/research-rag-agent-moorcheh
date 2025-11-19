FROM python:3.13.5-slim

ENV UV_CACHE_DIR=/tmp/uv-cache

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/* \
    && pip install uv

COPY pyproject.toml uv.lock ./
COPY src/ ./src/

RUN rm -rf /app/.venv && uv sync --frozen --no-dev

EXPOSE 8501

# HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

CMD ["uv", "run", "streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
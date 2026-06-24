FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Dépendances système minimales (libgomp pour torch CPU)
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps en couche séparée pour bénéficier du cache Docker.
# Torch CPU est installé séparément (index PyTorch CPU) pour éviter de pull
# 2.5 Go de CUDA inutile dans cette image.
COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install torch==2.5.1 --index-url https://download.pytorch.org/whl/cpu \
 && pip install -r requirements.txt

# Code applicatif
COPY app/ ./app/
COPY tests/ ./tests/
COPY pytest.ini .

# Le cache modèle HF sera monté en volume sur /app/models
ENV HF_HOME=/app/models

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
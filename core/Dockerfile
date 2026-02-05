# Usamos a imagem slim para manter o container leve
FROM python:3.11-slim

# Instala dependencias de sistema necessarias para C++ (exigidas pelo Qiskit/Aer)
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Define o diretorio de trabalho dentro do container
WORKDIR /app

# Copia o requirements primeiro para aproveitar o cache de camadas do Docker
COPY requirements.txt .

# Instala as dependencias com cache do pip (BuildKit)
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt

# Copia o restante do codigo
COPY . .

# Define o PYTHONPATH para que os imports da Clean Architecture funcionem
ENV PYTHONPATH=/app/src

# Comando para rodar a API
CMD ["uvicorn", "infrastructure.api.fastapi_app:app", "--host", "0.0.0.0", "--port", "8000"]

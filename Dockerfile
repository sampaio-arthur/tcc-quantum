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

# Instala as dependencias (sem usar cache do pip para diminuir a imagem)
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do codigo
COPY . .

# Baixa o modelo durante o build para ja ficar na imagem
RUN python download_models.py

# Define o PYTHONPATH para que os imports da Clean Architecture funcionem
ENV PYTHONPATH=/app

# Comando para rodar a API
CMD ["uvicorn", "infrastructure.api.fastapi_app:app", "--host", "0.0.0.0", "--port", "8000"]

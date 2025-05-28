FROM python:3.12-slim

WORKDIR /app

# Aumenta o timeout do pip para 120s
ENV PIP_DEFAULT_TIMEOUT=120

# Copia apenas o requirements para aproveitar cache do Docker
COPY requirements.txt .

# Instala libgomp e limpa cache do apt
RUN apt-get update \
 && apt-get install -y --no-install-recommends libgomp1 \
 && rm -rf /var/lib/apt/lists/*

# Instala as dependências Python com timeout extendido
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código da aplicação
COPY . .

EXPOSE 3000

CMD ["gunicorn", "--workers", "1", "--timeout", "60", "--bind", "0.0.0.0:3000", "app:app"]

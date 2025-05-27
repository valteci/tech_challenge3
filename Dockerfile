# Use a imagem oficial Python 3.12 slim
FROM python:3.12-slim

# Define diretório de trabalho
WORKDIR /app

# Copia apenas o requirements primeiro (para aproveitar cache)
COPY requirements.txt .

# Instala libgomp e limpa cache do apt
RUN apt-get update \
 && apt-get install -y --no-install-recommends libgomp1 \
 && rm -rf /var/lib/apt/lists/*

# Instala dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código da sua aplicação
COPY . .

# Expõe a porta em que o Gunicorn vai escutar
EXPOSE 3000

# Comando para iniciar o Gunicorn
# Substitua 'app:app' pelo módulo e variável da sua Flask app, se necessário.
CMD ["gunicorn", "--workers", "1", "--timeout", "60", "--bind", "0.0.0.0:3000", "app:app"]
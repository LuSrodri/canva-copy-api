# Use Python 3.11 slim baseado em Debian (leve e estável)
FROM python:3.11-slim

# Instala dependências do sistema necessárias para transformers
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Define diretório de trabalho
WORKDIR /app

# Copia arquivo de requirements primeiro (para cache eficiente)
COPY requirements.txt .

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY . .

# Cria usuário não-root para segurança
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expõe a porta padrão do FastAPI
EXPOSE 8000

# Comando para rodar a aplicação
CMD ["fastapi", "run", "main.py", "--host", "0.0.0.0", "--port", "8000"]
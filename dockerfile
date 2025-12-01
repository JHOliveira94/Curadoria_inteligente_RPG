# Imagem base com Python leve
FROM python:3.11-slim

# Atualiza e instala dependências de sistema (incluindo ffmpeg)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho
WORKDIR /app

# Atualiza pip para última versão estável
RUN pip install --no-cache-dir --upgrade pip

# Instala Torch com suporte apenas a CPU, usando índice alternativo
RUN pip install --no-cache-dir torch==2.1.0+cpu -f https://download.pytorch.org/whl/torch_stable.html

# Copia o arquivo de dependências Python
COPY requirements.txt .

# Instala as demais bibliotecas listadas
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante dos arquivos do projeto (exceto o que estiver no .dockerignore)
COPY . .

# Evita buffer no output do Python (logs visíveis em tempo real)
ENV PYTHONUNBUFFERED=1

# Instala e registra o kernel Jupyter no momento do build
RUN python -m ipykernel install --user --name=rpg-dados --display-name "Python (RPG Dados)"

# Mantém o contêiner ativo indefinidamente
CMD ["tail", "-f", "/dev/null"]


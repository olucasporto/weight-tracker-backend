# Usa uma imagem oficial do Python como base
FROM python:3.10

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos do projeto para dentro do container
COPY . .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta 8000
EXPOSE 8000

# Comando para rodar a aplicação
CMD ["pipenv", "run", "uvicorn", "weight_tracker_api:app", "--host", "0.0.0.0", "--port", "8000"]

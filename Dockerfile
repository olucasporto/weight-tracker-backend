# Usa uma imagem oficial do Python
FROM python:3.10

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia os arquivos do projeto para dentro do container
COPY . .

# Instala as dependências do projeto
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta usada pelo Uvicorn
EXPOSE 8080

# Comando para rodar a aplicação
CMD ["uvicorn", "weight_tracker_api:app", "--host", "0.0.0.0", "--port", "8080"]


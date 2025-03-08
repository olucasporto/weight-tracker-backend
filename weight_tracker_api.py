from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware

# Carregar variáveis do .env
load_dotenv()

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

app = FastAPI()

# Configurar CORS para permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ Modo aberto (pode restringir depois)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo Pydantic para validar entrada de dados
class WeightInput(BaseModel):
    weight: float

# Conectar ao banco SQLite
def get_db_connection():
    conn = sqlite3.connect("weights.db")
    conn.execute("CREATE TABLE IF NOT EXISTS weights (id INTEGER PRIMARY KEY, date TEXT, weight REAL)")
    return conn

# Função para enviar e-mail
def send_email(weight):
    if not all([SENDER_EMAIL, RECEIVER_EMAIL, EMAIL_PASSWORD]):
        print("Erro: Credenciais de e-mail não configuradas corretamente no .env")
        return

    msg = MIMEMultipart()
    msg["Subject"] = "Atualização de Peso 📊"
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL

    # Corpo do e-mail
    msg.attach(MIMEText(f"Peso de hoje: {weight} kg"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, EMAIL_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        print("✅ E-mail enviado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao enviar e-mail: {e}")

@app.post("/register_weight/")
def register_weight(data: WeightInput):
    conn = get_db_connection()
    conn.execute("INSERT INTO weights (date, weight) VALUES (date('now'), ?)", (data.weight,))
    conn.commit()
    conn.close()

    send_email(data.weight)  # Envia e-mail automaticamente
    return {"message": "Peso registrado e e-mail enviado!"}

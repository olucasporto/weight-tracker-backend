from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class WeightInput(BaseModel):
    weight: float

def get_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco de dados: {e}")
        raise HTTPException(status_code=500, detail="Erro ao conectar ao banco de dados")


def create_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS weights (
            id SERIAL PRIMARY KEY,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            weight REAL NOT NULL
        )
    """)
    conn.commit()
    cur.close()
    conn.close()


create_table()


def send_email(weight):
    if not all([SENDER_EMAIL, RECEIVER_EMAIL, EMAIL_PASSWORD]):
        print("Erro: Credenciais de e-mail não configuradas corretamente no .env")
        return

    msg = MIMEMultipart()
    msg["Subject"] = "Atualização de Peso 📊"
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL

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
    cur = conn.cursor()

    try:
        cur.execute("INSERT INTO weights (weight) VALUES (%s) RETURNING id;", (data.weight,))
        conn.commit()
        cur.close()
        conn.close()

        send_email(data.weight)

        return {"message": "Peso registrado e e-mail enviado!"}

    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        print(f"❌ Erro ao registrar peso: {e}")
        raise HTTPException(status_code=500, detail="Erro ao registrar peso")


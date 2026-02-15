import os
import socket
import threading
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from flask import Flask

# --- CONFIGURACIÓN ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# --- IA: GEMINI 3 FLASH (Versión Estable) ---
instrucciones_sistema = (
    "Eres 'CiberSentryBot', experto en Ciberseguridad Defensiva."
)

# Cambiamos a la dirección técnica exacta que Google pide ahora
model = genai.GenerativeModel(
    model_name="models/gemini-3-flash", 
    system_instruction=instrucciones_sistema
)

async def manejar_contenido(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    
    try:
        # Usamos un método más directo para evitar problemas de versión
        response = model.generate_content(update.message.text)
        await update.message.reply_text(response.text)
    except Exception as e:
        # Si esto vuelve a fallar, nos dirá si es la región o el nombre
        await update.message.reply_text(f"⚠️ Error técnico: {str(e)}")

# --- SERVIDOR WEB ---
app = Flask(__name__)
@app.route('/')
def index(): return "CiberSentry Activo"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == '__main__':
    threading.Thread(target=run_flask).start()
    if TELEGRAM_TOKEN:
        app_bot = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        app_bot.add_handler(MessageHandler(filters.TEXT, manejar_contenido))
        app_bot.run_polling()

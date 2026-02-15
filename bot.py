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

# --- IA ---
# IMPORTANTE: He puesto 'gemini-1.5-flash' porque es el más estable para APIs gratuitas
model = genai.GenerativeModel("gemini-1.5-flash")

async def manejar_contenido(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    user_input = update.message.text

    try:
        # Intentamos generar respuesta
        response = model.generate_content(user_input)
        await update.message.reply_text(response.text)
    except Exception as e:
        # ESTO NOS DIRÁ EL ERROR REAL
        await update.message.reply_text(f"❌ ERROR DE IA: {str(e)}")

# --- SERVIDOR WEB ---
app = Flask(__name__)
@app.route('/')
def index(): return "CiberSentry OK"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == '__main__':
    threading.Thread(target=run_flask).start()
    if TELEGRAM_TOKEN:
        print("✅ BOT ARRANCANDO...")
        app_bot = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        app_bot.add_handler(MessageHandler(filters.TEXT, manejar_contenido))
        app_bot.run_polling()

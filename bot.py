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

# --- IA: GEMINI 3 FLASH ---
instrucciones_sistema = (
    "Eres 'CiberSentryBot', un experto en Ciberseguridad Defensiva (White Hat). "
    "Responde de forma breve, concisa y técnica."
)

model = genai.GenerativeModel(
    model_name="gemini-3-flash", 
    system_instruction=instrucciones_sistema
)

async def manejar_contenido(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    user_input = update.message.text

    try:
        # Generamos la respuesta con Gemini 3
        response = model.generate_content(user_input)
        await update.message.reply_text(response.text)
    except Exception as e:
        # Si falla, nos dirá el porqué real (API Key, modelo, etc)
        await update.message.reply_text(f"❌ Error Gemini 3: {str(e)}")

# --- SERVIDOR WEB (Obligatorio para Render) ---
app = Flask(__name__)
@app.route('/')
def index(): return "CiberSentry Gemini 3 Activo"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == '__main__':
    threading.Thread(target=run_flask).start()
    if TELEGRAM_TOKEN:
        print("✅ ARRANCANDO BOT CON GEMINI 3...")
        app_bot = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        app_bot.add_handler(MessageHandler(filters.TEXT, manejar_contenido))
        app_bot.run_polling()

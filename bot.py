import os
import socket
import threading
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from flask import Flask

# --- CONFIGURACIÓN DE LLAVES ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("⚠️ ERROR: Falta GEMINI_API_KEY")

# --- TUS FUNCIONES TÉCNICAS (ORIGINALES) ---
def escanear_objetivo(target_ip):
    print(f"\n🔍 Iniciando escaneo de puertos comunes en {target_ip}...")
    puertos_comunes = [21, 22, 23, 80, 443, 445, 3389, 8080]
    puertos_abiertos = []

    try:
        # Resolvemos IP para asegurar
        ip = socket.gethostbyname(target_ip)
        for puerto in puertos_comunes:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1) 
            result = sock.connect_ex((ip, puerto))
            if result == 0:
                puertos_abiertos.append(puerto)
            sock.close()
    except Exception as e:
        return f"Error al escanear: {str(e)}"

    if not puertos_abiertos:
        return f"No se encontraron puertos abiertos comunes en {target_ip}."
    else:
        return f"RESULTADO DEL ESCANEO en {target_ip}: Puertos abiertos encontrados: {puertos_abiertos}"

# (Tu segunda función, la dejamos por si la usas en el futuro)
def escanear_puertos(objetivo):
    puertos_clave = [21, 22, 23, 25, 53, 80, 110, 443, 445, 3306, 3389, 8080]
    abiertos = []
    try:
        ip = socket.gethostbyname(objetivo)
        for puerto in puertos_clave:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            resultado = sock.connect_ex((ip, puerto))
            if resultado == 0:
                abiertos.append(puerto)
            sock.close()
        return abiertos, ip
    except:
        return None, None

# --- LÓGICA DEL AGENTE IA (TUS INSTRUCCIONES) ---
instrucciones_sistema = (
    "Las explicaciones que das son breves, concisas y exactas."
    "Solo puedes contestar a preguntas de seguridad informática y ciberseguridad."
    "Eres 'CiberSentryBot', un experto en Ciberseguridad Defensiva (White Hat)."
    "Analizar textos de correos electrónicos en busca de indicadores de Phishing."
    "Explicar vulnerabilidades (como SQL Injection, XSS) de forma sencilla."
    "Sugerir configuraciones seguras para contraseñas y redes."
    "Analizar pequeños fragmentos de código para detectar fallos de seguridad."
    "Actúa siempre desde una perspectiva defensiva (White Hat)."
    "NUNCA proporciones instrucciones para crear malware, exploits o realizar ataques reales."
    "Si el usuario pide algo ilegal, explica el riesgo y cómo defenderse de ello, pero no cómo ejecutarlo."
    "Usa un tono profesional, técnico pero accesible."
    "Analizas vulnerabilidades, explicas puertos y detectas phishing."
    "Si recibes una lista de puertos, explicas qué servicios son y sus riesgos."
)

# IMPORTANTE: Usamos el 1.5 porque el 3 da error 404 y apaga el bot.
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash", 
    system_instruction=instrucciones_sistema
)

async def manejar_contenido(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    user_input = update.message.text

    # Si es comando escanear
    if user_input.lower().startswith("escanear"):
        try:
            partes = user_input.split(" ")
            if len(partes) < 2:
                await update.message.reply_text("❌ Error: Debes escribir 'escanear [IP_O_DOMINIO]'")
                return
            
            objetivo = partes[1]
            await update.message.reply_text(f"🔍 Escaneando {objetivo}...")
            
            # Usamos TU función original
            datos_del_escaneo = escanear_objetivo(objetivo)
            
            prompt_para_ia = f"El usuario pidió escanear {objetivo}. Resultado: '{datos_del_escaneo}'. Analiza esto."
            
            response = model.generate_content(prompt_para_ia)
            await update.message.reply_text(f"🛡️ AGENTE:\n{response.text}")

        except Exception as e:
            await update.message.reply_text(f"❌ Error técnico: {e}")
    
    # Conversación normal
    else:
        try:
            response = model.generate_content(user_input)
            await update.message.reply_text(response.text)
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error IA: {e}")

# --- SERVIDOR WEB (NECESARIO PARA RENDER) ---
app = Flask(__name__)

@app.route('/')
def index(): return "CiberSentry Bot VIVO"

def run_flask():
    # Render asigna un puerto dinámico, hay que leerlo así:
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# --- ARRANQUE ---
if __name__ == '__main__':
    # Hilo para Flask
    threading.Thread(target=run_flask).start()

    # Hilo para Telegram
    if TELEGRAM_TOKEN:
        print("✅ BOT ARRANCANDO...")
        app_bot = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        app_bot.add_handler(MessageHandler(filters.TEXT, manejar_contenido))
        app_bot.run_polling()

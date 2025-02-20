import os
import json
import telebot
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re
import logging

# Configurar logging para depuración
logging.basicConfig(level=logging.INFO)

# Configurar bot de Telegram
TOKEN = os.getenv("7828902060:AAGCHu_4DzO2UcEi5kao1zJhn9w9gWZIbOA")
bot = telebot.TeleBot(TOKEN)

# Configurar conexión con Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Cargar credenciales desde la variable de entorno
credenciales_json = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
if not credenciales_json:
    logging.error("No se encontró la variable GOOGLE_SHEETS_CREDENTIALS.")
    exit()

credenciales_dict = json.loads(credenciales_json)
credenciales = ServiceAccountCredentials.from_json_keyfile_dict(credenciales_dict, scope)
cliente = gspread.authorize(credenciales)

# Abrir la hoja de cálculo y seleccionar la primera hoja
try:
    sheet = cliente.open("Nombre_de_tu_Hoja").sheet1  # Reemplaza con el nombre real
except Exception as e:
    logging.error(f"Error al conectar con Google Sheets: {e}")
    sheet = None

# Dirección de pago en la red Solana
DIRECCION_SOLANA = "35VyMoWKRJTX1Q1zKaNZ5sKs4VQtvFQkhgiMmzi8TzrF"

# Lista de redes sociales válidas
REDES_SOCIALES = ["tiktok", "instagram", "facebook", "telegram", "youtube", "twitter"]

# Comando /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "👋 *¡Bienvenido al Panel SMM!* \n\n"
        "📌 Usa `/pedido` para solicitar un servicio.",
        parse_mode="Markdown"
    )

# Comando /pedido
@bot.message_handler(commands=['pedido'])
def pedido(message):
    msg = bot.send_message(
        message.chat.id, 
        "📩 *¡Realiza tu pedido siguiendo este formato!*\n\n"
        "🔹 `Red Social - Servicio - Cantidad - Usuario o Enlace`\n\n"
        "📍 *Ejemplo:* `TikTok - Seguidores - 10000 - https://t.me/miGrupo`\n\n"
        "❗ *Si el formato es incorrecto, recibirás un aviso.*",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, guardar_pedido)

# Guardar pedido
def guardar_pedido(message):
    texto = message.text.strip()
    datos = re.split(r"\s*-\s*", texto)

    if len(datos) == 4:
        red_social, servicio, cantidad, usuario = datos
        red_social = red_social.strip().lower()

        if red_social not in REDES_SOCIALES:
            bot.send_message(
                message.chat.id, 
                "🚨 *Error:* La red social ingresada no es válida.\n\n"
                "📌 *Redes disponibles:* `TikTok, Instagram, Facebook, Telegram, YouTube, Twitter`",
                parse_mode="Markdown"
            )
            return

        if not cantidad.isdigit():
            bot.send_message(message.chat.id, "⚠️ *Error:* La cantidad debe ser un número válido.", parse_mode="Markdown")
            return
        
        if sheet:
            try:
                sheet.append_row([message.chat.id, red_social.capitalize(), servicio.strip(), cantidad.strip(), usuario.strip()])
                bot.send_message(message.chat.id, "✅ *Pedido registrado correctamente.*", parse_mode="Markdown")

                # Mensaje de pago
                mensaje_pago = (
                    "💰 *Para procesar tu pedido, debes realizar el pago de **25 USDT** en la red **Solana**. "
                    "Convierte tus USDT a SOLANA y envía SOLANA/SOLANA.*\n\n"
                    f"📌 *Dirección de pago:* `{DIRECCION_SOLANA}`\n\n"
                    "📤 *Una vez realizado el pago, envía el comprobante aquí.*"
                )
                bot.send_message(message.chat.id, mensaje_pago, parse_mode="Markdown")
            except Exception as e:
                logging.error(f"Error al guardar en Google Sheets: {e}")
                bot.send_message(message.chat.id, "⚠️ *Error al guardar el pedido. Intenta nuevamente más tarde.*", parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, "⚠️ *Error: No se pudo conectar con Google Sheets.*", parse_mode="Markdown")
    else:
        bot.send_message(
            message.chat.id, 
            "⚠️ *Formato incorrecto.*\n\n"
            "📩 *Debes usar:* `Red Social - Servicio - Cantidad - Usuario o Enlace`\n"
            "📍 *Ejemplo:* `TikTok - Seguidores - 10000 - https://t.me/miGrupo`",
            parse_mode="Markdown"
        )

# Iniciar bot
if __name__ == "__main__":
    while True:
        try:
            bot.polling(none_stop=True, skip_pending=True)
        except Exception as e:
            logging.error(f"Error en bot.polling(): {e}")

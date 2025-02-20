import telebot
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re
import logging

# Configurar logging para depuración
logging.basicConfig(level=logging.INFO)

# Configurar bot de Telegram
TOKEN = "7828902060:AAGCHu_4DzO2UcEi5kao1zJhn9w9gWZIbOA"
bot = telebot.TeleBot(TOKEN)

# Configurar conexión con Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Cargar credenciales desde la variable de entorno
credenciales_json = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
credenciales_dict = json.loads(credenciales_json)
credenciales = ServiceAccountCredentials.from_json_keyfile_dict(credenciales_dict, scope)
cliente = gspread.authorize(credenciales)

# Dirección de pago en la red Solana
DIRECCION_SOLANA = "35VyMoWKRJTX1Q1zKaNZ5sKs4VQtvFQkhgiMmzi8TzrF"

# Lista de redes sociales válidas (todas en minúsculas para evitar errores)
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

    # Separar con cualquier tipo de guion y espacios
    datos = re.split(r"\s*-\s*", texto)

    if len(datos) == 4:
        red_social, servicio, cantidad, usuario = datos

        # Convertir la red social a minúsculas para evitar errores
        red_social = red_social.strip().lower()

        # Verificar que la red social sea válida
        if red_social not in REDES_SOCIALES:
            bot.send_message(
                message.chat.id, 
                "🚨 *Error:* La red social ingresada no es válida.\n\n"
                "📌 *Redes disponibles:* `TikTok, Instagram, Facebook, Telegram, YouTube, Twitter`",
                parse_mode="Markdown"
            )
            return

        # Verificar que la cantidad sea un número
        if not cantidad.isdigit():
            bot.send_message(message.chat.id, "⚠️ *Error:* La cantidad debe ser un número válido.", parse_mode="Markdown")
            return
        
        # Guardar en Google Sheets
        if sheet:
            try:
                sheet.append_row([message.chat.id, red_social.capitalize(), servicio.strip(), cantidad.strip(), usuario.strip()])
                bot.send_message(message.chat.id, "✅ *Pedido registrado correctamente.*", parse_mode="Markdown")

                # Enviar mensaje de pago
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

# Mantener el bot corriendo sin interrupciones
while True:
    try:
        bot.polling(none_stop=True, skip_pending=True)
    except Exception as e:
        logging.error(f"Error en bot.polling(): {e}")

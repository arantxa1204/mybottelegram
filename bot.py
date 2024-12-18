import telepot
from telepot.loop import MessageLoop
import os
import time
import urllib.request

# Configuración de directorios
BASE_PATH = r"C:\Users\aqsj_\OneDrive\Documentos\bot_descortesía\registros"
ARCHIVOS_PATH = os.path.join(BASE_PATH, "archivos")

# Crear carpetas si no existen
if not os.path.exists(BASE_PATH):
    os.makedirs(BASE_PATH)

if not os.path.exists(ARCHIVOS_PATH):
    os.makedirs(ARCHIVOS_PATH)

# Token del bot (reemplaza con tu token real)
TOKEN = '7708982103:AAFNaZsTWVY7KXmR0w4Rw_CcQETiOBBLbQo'

# Inicializar el bot
bot = telepot.Bot(TOKEN)

# Estado para manejar el flujo de conversación
user_states = {}

# Función para almacenar texto de la conversación
def guardar_texto(chat_id, texto):
    file_path = os.path.join(BASE_PATH, f"{chat_id}_conversacion.txt")
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(texto + "\n")

# Función para guardar archivos multimedia
def guardar_archivo(file_info, file_name, chat_id):
    try:
        file_path = os.path.join(ARCHIVOS_PATH, file_name)
        file_id = file_info['file_id']

        # Obtener la URL del archivo
        file_url = f"https://api.telegram.org/file/bot{TOKEN}/{bot.getFile(file_id)['file_path']}"

        # Descargar y guardar el archivo
        urllib.request.urlretrieve(file_url, file_path)

        guardar_texto(chat_id, f"Archivo guardado: {file_name}")
        print(f"Archivo {file_name} guardado en {ARCHIVOS_PATH}")
    except Exception as e:
        print(f"Error al guardar archivo: {e}")

# Función principal para manejar mensajes
def handle(msg):
    chat_id = msg['chat']['id']
    text = msg.get('text', "")
    content_type, _, _ = telepot.glance(msg)

    # Inicializar el estado si es la primera vez
    if chat_id not in user_states:
        user_states[chat_id] = {"state": "START"}

    state = user_states[chat_id]["state"]

    # Función para reiniciar la conversación
    def restart():
        bot.sendMessage(chat_id, "¡Hola! Me presento, mi nombre es Aranbot, soy un chatbot encargado de recopilar datos. Recojo conversaciones de mensajería instántanea que tú decidas mandarme (audios, fotos, zip,...). Estas conversaciones deberan ser insultándote en broma o bromeando con alguien cercano a ti. Para empezar dime: ¿Cuántos años tienes?")
        guardar_texto(chat_id, "Inicio de conversación")
        user_states[chat_id]["state"] = "ASK_AGE"

    # Flujo de conversación
    if state == "START":
        restart()

    elif state == "ASK_AGE":
        guardar_texto(chat_id, f"Edad: {text}")
        bot.sendMessage(chat_id, "¿De dónde eres? (Ciudad y país)")
        user_states[chat_id]["state"] = "ASK_LOCATION"

    elif state == "ASK_LOCATION":
        guardar_texto(chat_id, f"Lugar: {text}")
        bot.sendMessage(chat_id, "¿Quieres enviar corpus de conversación o realizar una entrevista?")
        user_states[chat_id]["state"] = "ASK_CHOICE"

    elif state == "ASK_CHOICE":
        if "corpus" in text.lower():
            bot.sendMessage(chat_id, "Por favor, envía los archivos de conversación (capturas, audios, etc.).")
            user_states[chat_id]["state"] = "WAITING_FILE"
        elif "entrevista" in text.lower():
            bot.sendMessage(chat_id, "La entrevista no durará más de 15 minutos. Por favor, proporciona tu información de contacto (correo o número).")
            user_states[chat_id]["state"] = "INTERVIEW"
        else:
            bot.sendMessage(chat_id, "Responde con 'corpus' o 'entrevista'.")

    elif state == "WAITING_FILE":
        if content_type in ["document", "audio", "photo", "voice"]:
            # Guardar el archivo según el tipo
            if content_type == "document":
                file_id = msg['document']['file_id']
                file_name = msg['document']['file_name']
            elif content_type == "audio":
                file_id = msg['audio']['file_id']
                file_name = f"audio_{chat_id}.mp3"
            elif content_type == "voice":
                file_id = msg['voice']['file_id']
                file_name = f"voice_{chat_id}.ogg"
            elif content_type == "photo":
                file_id = msg['photo'][-1]['file_id']
                file_name = f"photo_{chat_id}.jpg"

            guardar_archivo({"file_id": file_id}, file_name, chat_id)

            # Preguntar edad de los participantes
            bot.sendMessage(chat_id, "Gracias por el archivo. ¿Qué edad tienen las personas en esta conversación? ¿Con quién estas hablando: con tus amigos, familiares o pareja?")
            user_states[chat_id]["state"] = "ASK_AGE_PARTICIPANTS"
        else:
            bot.sendMessage(chat_id, "Por favor, envía un archivo válido.")

    elif state == "ASK_AGE_PARTICIPANTS":
        guardar_texto(chat_id, f"Edad de participantes: {text}")
        bot.sendMessage(chat_id, "¿Quieres enviar más conversaciones? Responde 'sí' o 'no'.")
        user_states[chat_id]["state"] = "ASK_MORE"

    elif state == "ASK_MORE":
        if "no" in text.lower():
            bot.sendMessage(chat_id, "¡Gracias por tu participación! Adiós.")
            guardar_texto(chat_id, "Fin de conversación\n")
            del user_states[chat_id]  # Reiniciar estado
        elif "sí" in text.lower():
            bot.sendMessage(chat_id, "Por favor, envía otro archivo.")
            user_states[chat_id]["state"] = "WAITING_FILE"
        else:
            bot.sendMessage(chat_id, "Responde con 'sí' o 'no'.")

    elif state == "INTERVIEW":
        guardar_texto(chat_id, f"Información de contacto: {text}")
        bot.sendMessage(chat_id, "¡Gracias! Te contactaremos pronto. Adiós.")
        guardar_texto(chat_id, "Fin de conversación\n")
        del user_states[chat_id]  # Reiniciar estado

    else:
        restart()

# Iniciar el bot
MessageLoop(bot, handle).run_as_thread()
print("Bot corriendo... Presiona CTRL+C para detener.")

# Mantener el bot corriendo
while True:
    time.sleep(10)
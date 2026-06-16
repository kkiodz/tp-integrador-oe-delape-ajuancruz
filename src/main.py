import json
import asyncio
from pathlib import Path
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes

# ==================== CONFIGURACION DEL BOT ====================
TOKEN = "8833736318:AAElTullAagHuGNnwzjWRQrJ0EJzedtT80k"

# ==================== RUTAS DE ARCHIVOS ====================
BASE_DIR = Path(__file__).parent.parent
DOCS_DIR = BASE_DIR / 'docs'
DATA_DIR = BASE_DIR / 'data'
DOCS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

CONOCIMIENTO_PATH = DOCS_DIR / 'base_conocimiento.json'
TICKETS_PATH = DATA_DIR / 'tickets.json'

# ==================== FUNCIONES PARA MANEJAR ARCHIVOS ====================

def cargar_conocimiento():
    """Carga la base de conocimiento desde el archivo JSON. Si no existe, crea una por defecto."""
    if CONOCIMIENTO_PATH.exists():
        with open(CONOCIMIENTO_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # Datos de ejemplo que el bot tiene para trabajar desde el principio
        default = {
            "software": [
                {"palabra_clave": "excel", "solucion": "Reinicia Excel o repara la instalacion desde Panel de Control."},
                {"palabra_clave": "correo", "solucion": "Verifica tu conexion a Internet y reinicia Outlook."},
                {"palabra_clave": "word", "solucion": "Cerrar y abrir de nuevo. Si persiste, reiniciar la PC."}
            ],
            "hardware": [
                {"palabra_clave": "impresora", "solucion": "Derivar a Nivel 2 - Revision fisica."},
                {"palabra_clave": "pc", "solucion": "Derivar a Nivel 2 - Diagnostico de hardware."},
                {"palabra_clave": "computadora", "solucion": "Derivar a Nivel 2 - Diagnostico de hardware."},
                {"palabra_clave": "monitor", "solucion": "Derivar a Nivel 2 - Revision de conexiones."}
            ],
            "acceso": [
                {"palabra_clave": "contraseña", "solucion": "Usar el boton 'Olvide mi contraseña'"},
                {"palabra_clave": "usuario", "solucion": "Verificar que se esta usando el usuario correcto."}
            ]
        }
        with open(CONOCIMIENTO_PATH, 'w', encoding='utf-8') as f:
            json.dump(default, f, ensure_ascii=False, indent=2)
        return default

def cargar_tickets():
    """Carga los tickets existentes o crea un archivo nuevo si no hay."""
    if TICKETS_PATH.exists():
        with open(TICKETS_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        default = {"tickets": [], "contador": 1}
        with open(TICKETS_PATH, 'w', encoding='utf-8') as f:
            json.dump(default, f, ensure_ascii=False, indent=2)
        return default

def guardar_tickets(data):
    """Guarda los tickets en el archivo JSON."""
    with open(TICKETS_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ==================== CARGA INICIAL ====================
# Cargo todo lo necesario al arrancar el bot
conocimiento = cargar_conocimiento()
tickets_db = cargar_tickets()

# ==================== ESTADOS DE LA CONVERSACION ====================
INICIO, ESPERANDO_DESCRIPCION, CLASIFICANDO, BUSCANDO_SOLUCION, OFRECIENDO_SOLUCION, CONFIRMANDO_SOLUCION, DERIVANDO = range(7)

# ==================== FUNCIONES DE CLASIFICACION ====================
# Logica para determinar que categoria tiene el problema

def clasificar_problema(descripcion):
    descripcion = descripcion.lower()
    hardware_keys = ['impresora', 'hardware', 'pc', 'monitor', 'red', 'router', 'cable','computadora']
    acceso_keys = ['contraseña', 'usuario', 'permiso', 'acceso', 'login', 'clave']
    software_keys = ['excel', 'word', 'correo', 'outlook', 'programa', 'aplicacion', 'software']
    
    for key in hardware_keys:
        if key in descripcion:
            return 'hardware'
    for key in acceso_keys:
        if key in descripcion:
            return 'acceso'
    for key in software_keys:
        if key in descripcion:
            return 'software'
    return 'desconocida'

def buscar_solucion(categoria, descripcion):
    """Busca una solucion en la base de conocimiento segun la categoria y la descripcion."""
    descripcion = descripcion.lower()
    items = conocimiento.get(categoria, [])
    for item in items:
        if item['palabra_clave'] in descripcion:
            return item['solucion']
    return None

# ==================== HANDLERS DEL BOT ====================
# Funciones que manejan los mensajes y la logica del bot

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Manejador del comando /start - inicia el flujo de soporte."""
    await asyncio.sleep(0.3)  # Pequeña pausa para dar sensacion de procesamiento
    await update.message.reply_text(
        "Hola, soy el bot de soporte tecnico Nivel 1.\n\n"
        "Contame cual es tu problema con el mayor detalle posible. "
        "Palabras como 'impresora', 'correo', 'contraseña' o 'pc' ayudan a clasificarlo.\n\n"
        "Ejemplo: 'No puedo imprimir desde mi PC'"
    )
    return ESPERANDO_DESCRIPCION

async def recibir_descripcion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Recibe la descripcion del problema, la clasifica y busca una solucion."""
    descripcion = update.message.text.strip()
    
    # Valido que el usuario no haya escrito cualquier cosa
    if len(descripcion) < 5:
        await asyncio.sleep(0.3)
        await update.message.reply_text(
            "La descripcion es muy corta, necesito mas detalles para poder ayudarte."
        )
        return ESPERANDO_DESCRIPCION
    
    context.user_data['descripcion'] = descripcion
    
    # Clasifico el problema
    categoria = clasificar_problema(descripcion)
    context.user_data['categoria'] = categoria

    if(categoria == 'desconocida'):
            await asyncio.sleep(0.3)
            await update.message.reply_text(
                "No pude identificar la categoria de tu problema, por favor intenta describirlo con otras palabras o con mas detalle."
            )
            return ESPERANDO_DESCRIPCION
    
    await asyncio.sleep(0.3)
    await update.message.reply_text(
        f"Categoria detectada: {categoria.upper()}"
    )
    
    await asyncio.sleep(0.4)
    await update.message.reply_text(
        "Buscando una solucion para tu problema..."
    )
    
    # Se busca solución 
    solucion = buscar_solucion(categoria, descripcion)
    
    if solucion and categoria != 'hardware':
        context.user_data['solucion'] = solucion
        
        await asyncio.sleep(0.5)
        await update.message.reply_text(
            f"Encontre una solucion sugerida:\n\n{solucion}\n\n"
            "Te sirvio? Respondeme con 'Si' o 'No'"
        )
        return CONFIRMANDO_SOLUCION
    else:
        await asyncio.sleep(0.4)
        await update.message.reply_text(
            "Este problema requiere atencion especializada.\n\n"
            "Voy a derivarlo al equipo de Nivel 2. Te van a contactar pronto."
        )
        return DERIVANDO

async def confirmar_solucion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Confirma si la solucion propuesta funciono o no."""
    respuesta = update.message.text.lower()
    
    if respuesta in ['si', 'sí', 's', 'funciono', 'funcionó', 'ok']:
        # Genero el ticket como cerrado
        ticket = {
            "id": tickets_db['contador'],
            "usuario": update.effective_user.username or update.effective_user.first_name,
            "categoria": context.user_data.get('categoria', 'desconocida'),
            "descripcion": context.user_data.get('descripcion', ''),
            "estado": "cerrado",
            "solucion": context.user_data.get('solucion', '')
        }
        tickets_db['tickets'].append(ticket)
        tickets_db['contador'] += 1
        guardar_tickets(tickets_db)
        
        await asyncio.sleep(0.3)
        await update.message.reply_text(
            f"Perfecto, tu problema esta resuelto.\n\n"
            f"Ticket N° {ticket['id']} cerrado.\n\n"
            "Si necesitas ayuda con otra cosa, escribi /start."
        )
        return ConversationHandler.END
    
    elif respuesta in ['no', 'n', 'nop', 'no funciono', 'no funcionó']:
        await asyncio.sleep(0.3)
        await update.message.reply_text(
            "Bueno, lamentamos que no haya funcionado.\n\n"
            "Voy a derivar tu caso a Nivel 2 para que te ayuden personalmente. "
            "Te van a contactar a la brevedad."
        )
        return DERIVANDO
    
    else:
        await asyncio.sleep(0.3)
        await update.message.reply_text(
            "No entendi tu respuesta. Decime 'Si' o 'No'."
        )
        return CONFIRMANDO_SOLUCION

async def derivar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    ticket = {
        "id": tickets_db['contador'],
        "usuario": update.effective_user.username or update.effective_user.first_name,
        "categoria": context.user_data.get('categoria', 'desconocida'),
        "descripcion": context.user_data.get('descripcion', ''),
        "estado": "derivado",
        "solucion": "Derivado a Nivel 2"
    }
    tickets_db['tickets'].append(ticket)
    tickets_db['contador'] += 1
    guardar_tickets(tickets_db)
    
    await asyncio.sleep(0.3)
    await update.message.reply_text(
        f"Ticket N° {ticket['id']} generado y derivado a Nivel 2.\n\n"
        "El equipo de soporte se va a comunicar con vos en las proximas horas.\n\n"
        "Si queres iniciar otra solicitud, usa /start"
    )
    return ConversationHandler.END

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancela la conversacion actual."""
    await asyncio.sleep(0.3)
    await update.message.reply_text(
        "Operacion cancelada.\n\n"
        "Si necesitas ayuda, usa /start para iniciar una nueva solicitud."
    )
    return ConversationHandler.END

# Función que permite el funcionamiento constante del bot aunque este mismo falle

async def manejar_error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        if update and update.effective_message:
            await asyncio.sleep(0.3)
            await update.effective_message.reply_text(
                "Hubo un error inesperado. Usa /start para empezar de nuevo."
            )
        elif update and update.callback_query:
            await asyncio.sleep(0.3)
            await update.callback_query.message.reply_text(
                "Hubo un error inesperado. Usa /start para empezar de nuevo."
            )
        else:
            print(f"Error sin contexto: {context.error}")
    except Exception as e:
        print(f"Error critico en el manejador de errores: {e}")
        print(f"Error original: {context.error}")

# ==================== MAIN ====================
def main():
    """Configura y ejecuta el bot de Telegram."""
    application = Application.builder().token(TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ESPERANDO_DESCRIPCION: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_descripcion)],
            CONFIRMANDO_SOLUCION: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirmar_solucion)],
            DERIVANDO: [MessageHandler(filters.TEXT & ~filters.COMMAND, derivar)],
        },
        fallbacks=[CommandHandler('cancelar', cancelar)],
        allow_reentry=True
    )
    
    application.add_handler(conv_handler)
    application.add_error_handler(manejar_error)
    
    print("Bot de soporte tecnico iniciado. Esperando mensajes...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
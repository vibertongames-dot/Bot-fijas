from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from supabase import create_client
from datetime import datetime

# --- CONFIGURACIÓN ---
TOKEN = '8864924864:AAF3Cvt3rvymEc4UNqjogs1awYZ5-SpFgRc'
ADMIN_ID = '8996437844'

SUPABASE_URL = 'https://vvsuwkaqsiwbdbsulpyz.supabase.co'
SUPABASE_KEY = 'sb_secret_8F0rm3_wXOtK7BVx1eLTcQ_MgDCpsPh'
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- COMANDO START ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    mensaje = f"🔥 ¡Bienvenido {user_name} a LA CASA DE LAS FIJAS! 🔥\n\n📈 ¿Estás listo para ganar? Elige una opción:"
    
    teclado = [
        [InlineKeyboardButton("📋 Ver Planes", callback_data='planes')],
        [InlineKeyboardButton("💰 Métodos de Pago", callback_data='pago')],
        [InlineKeyboardButton("📞 Contactar Admin", callback_data='contacto')]
    ]
    reply_markup = InlineKeyboardMarkup(teclado)
    
    # Mensaje de bienvenida con botones
    await update.message.reply_text(mensaje, reply_markup=reply_markup)

# --- GESTIÓN DE BOTONES ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'planes':
        await query.edit_message_text(text="📋 **PLANES DISPONIBLES**\n✅ Semanal: S/ 10.00\n✅ Mensual: S/ 15.00\n\n¡Elige el tuyo y envíanos la captura!")
    elif query.data == 'pago':
        await query.edit_message_text(text="💳 **MÉTODOS DE PAGO**\nSolo Plin: 937005352.\nEnvía tu captura de pago por aquí para registrarte.")
    elif query.data == 'contacto':
        await query.edit_message_text(text="📲 **CONTACTO**\nPara consultas directas: 937005352.")

# --- REGISTRO DE CLIENTES ---
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    # Guardar datos en la tabla 'Clientes' (con C mayúscula)
    data = {"nombre": user.first_name, "username": str(user.username), "fecha": datetime.now().strftime("%Y-%m-%d")}
    supabase.table("Clientes").insert(data).execute()
    
    await update.message.reply_text(f"✅ ¡Gracias {user.first_name}! Tu pago ha sido registrado. El admin validará tu acceso.")
    
    # Reenviar al admin
    await context.bot.send_photo(chat_id=ADMIN_ID, photo=update.message.photo[-1].file_id, 
                                 caption=f"🚨 Nuevo pago recibido de: {user.first_name} (@{user.username})")

# --- VER CLIENTES (Solo Admin) ---
async def ver_clientes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) == ADMIN_ID:
        response = supabase.table("Clientes").select("*").execute()
        lista = response.data
        if not lista:
            await update.message.reply_text("La lista de clientes está vacía.")
        else:
            texto = "👥 **LISTA DE CLIENTES:**\n\n" + "\n".join([f"👤 {c['nombre']} ({c['fecha']})" for c in lista])
            await update.message.reply_text(texto)
    else:
        await update.message.reply_text("⛔ No tienes permisos para ver esto.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clientes", ver_clientes))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_polling()

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from supabase import create_client
from datetime import datetime

# --- CONFIGURACIÓN ---
TOKEN = '8864924864:AAF3Cvt3rvymEc4UNqjogs1awYZ5-SpFgRc'
ADMIN_ID = '8996437844'

# Tus datos de Supabase (integrados)
SUPABASE_URL = 'https://vvsuwkaqsiwbdbsulpyz.supabase.co'
SUPABASE_KEY = 'sb_secret_8F0rm3_wXOtK7BVx1eLTcQ_MgDCpsPh'
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- MENÚ DE BIENVENIDA ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = "🔥 ¡BIENVENIDO A LA CASA DE LAS FIJAS! 🔥\n\n📈 ¿Listo para ganar? Elige una opción:"
    teclado = [
        [InlineKeyboardButton("📋 Ver Planes", callback_data='planes')],
        [InlineKeyboardButton("💰 Métodos de Pago", callback_data='pago')],
        [InlineKeyboardButton("📞 Contactar Admin", callback_data='contacto')]
    ]
    # Asegúrate de que el nombre del archivo de imagen sea el correcto en tu carpeta
    await update.message.reply_photo(photo=open('IMG_20260708_181916_435.jpg', 'rb'), 
                                     caption=mensaje, reply_markup=InlineKeyboardMarkup(teclado))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'planes':
        await query.edit_message_caption(caption="📋 **PLANES**\n✅ Semanal: S/ 10.00\n✅ Mensual: S/ 15.00")
    elif query.data == 'pago':
        await query.edit_message_caption(caption="💳 **PAGO**\nSolo Plin: 937005352. Envía tu captura aquí.")
    elif query.data == 'contacto':
        await query.edit_message_caption(caption="📲 Contacto: 937005352")

# --- REGISTRO EN SUPABASE ---
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    # Guardar en la nube
    data = {"nombre": user.first_name, "username": str(user.username), "fecha": datetime.now().strftime("%Y-%m-%d")}
    supabase.table("clientes").insert(data).execute()
    
    await update.message.reply_text(f"✅ ¡Gracias {user.first_name}! Registro guardado en la nube.")
    await context.bot.send_photo(chat_id=ADMIN_ID, photo=update.message.photo[-1].file_id, 
                                 caption=f"🚨 Nuevo cliente: {user.first_name}")

async def ver_clientes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) == ADMIN_ID:
        response = supabase.table("clientes").select("*").execute()
        # Formatear la lista para que se vea bien
        lista = response.data
        if not lista:
            await update.message.reply_text("La lista de clientes está vacía.")
        else:
            texto = "👥 **LISTA DE CLIENTES:**\n\n" + "\n".join([f"👤 {c['nombre']} ({c['fecha']})" for c in lista])
            await update.message.reply_text(texto)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clientes", ver_clientes))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_polling()

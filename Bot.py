import sqlite3
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Configuración básica
TOKEN = '8864924864:AAF3Cvt3rvymEc4UNqjogs1awYZ5-SpFgRc'
ADMIN_ID = '8996437844'

# --- INICIALIZACIÓN DE LA BASE DE DATOS ---
def init_db():
    conn = sqlite3.connect('clientes.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS clientes 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, username TEXT, fecha_pago TEXT)''')
    conn.commit()
    conn.close()

def guardar_cliente(nombre, username):
    conn = sqlite3.connect('clientes.db')
    cursor = conn.cursor()
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute("INSERT INTO clientes (nombre, username, fecha_pago) VALUES (?, ?, ?)", 
                   (nombre, username, fecha))
    conn.commit()
    conn.close()

# --- FUNCIONES DEL BOT ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = "🔥 ¡BIENVENIDO A LA CASA DE LAS FIJAS! 🔥\n\n📈 ¿Listo para ganar? Elige una opción:"
    teclado = [
        [InlineKeyboardButton("📋 Ver Planes", callback_data='planes')],
        [InlineKeyboardButton("💰 Métodos de Pago", callback_data='pago')],
        [InlineKeyboardButton("📞 Contactar Admin", callback_data='contacto')]
    ]
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

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    guardar_cliente(user.first_name, user.username) # Guarda el dato
    await update.message.reply_text(f"✅ ¡Gracias {user.first_name}! Registro guardado.")
    await context.bot.send_photo(chat_id=ADMIN_ID, photo=update.message.photo[-1].file_id, 
                                 caption=f"🚨 Nuevo cliente: {user.first_name} (@{user.username})")

async def ver_clientes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) == ADMIN_ID:
        conn = sqlite3.connect('clientes.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clientes")
        rows = cursor.fetchall()
        conn.close()
        texto = "👥 **LISTA DE CLIENTES:**\n\n" + "\n".join([f"👤 {r[1]} | @{r[2]} | {r[3]}" for r in rows])
        await update.message.reply_text(texto)

if __name__ == '__main__':
    init_db()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clientes", ver_clientes))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    print("Bot encendido con base de datos...")
    app.run_polling()

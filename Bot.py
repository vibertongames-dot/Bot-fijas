import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Configuración básica
TOKEN = '8864924864:AAF3Cvt3rvymEc4UNqjogs1awYZ5-SpFgRc'
ADMIN_ID = '8996437844' 

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = (
        "🔥 ¡BIENVENIDO A LA CASA DE LAS FIJAS! 🔥\n\n"
        "📈 ¿Listo para ganar? Elige una opción:"
    )
    teclado = [
        [InlineKeyboardButton("📋 Ver Planes", callback_data='planes')],
        [InlineKeyboardButton("💰 Métodos de Pago", callback_data='pago')],
        [InlineKeyboardButton("📞 Contactar Admin", callback_data='contacto')]
    ]
    reply_markup = InlineKeyboardMarkup(teclado)
    
    await update.message.reply_photo(
        photo=open('IMG_20260708_181916_435.jpg', 'rb'),
        caption=mensaje,
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'planes':
        await query.edit_message_caption(caption="📋 **PLANES DE ACCESO**\n✅ Semanal: S/ 10.00\n✅ Mensual: S/ 15.00")
    elif query.data == 'pago':
        msg_pago = (
            "💳 **MÉTODOS DE PAGO**\n\n"
            "Aceptamos solo **Plin** al número: **937005352**\n\n"
            "-------------------------------\n"
            "📢 **IMPORTANTE:**\n"
            "Una vez realizado el pago, envía tu comprobante (captura de pantalla) a este mismo chat. "
            "Lo validaremos y te daremos acceso al grupo de inmediato. ¡Vamos por esa fija! 💰"
        )
        await query.edit_message_caption(caption=msg_pago)
    elif query.data == 'contacto':
        await query.edit_message_caption(caption="📲 Escríbenos directamente aquí: 937005352")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    await update.message.reply_text(f"✅ ¡Gracias {user.first_name}! He recibido tu comprobante. El administrador lo revisará pronto.")
    
    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=update.message.photo[-1].file_id,
        caption=f"🚨 Nuevo comprobante de: {user.first_name} (@{user.username})"
    )

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    print("Bot encendido...")
    app.run_polling()

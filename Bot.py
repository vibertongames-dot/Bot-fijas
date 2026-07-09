from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Mensaje con los precios actualizados
    mensaje = (
        "🔥 ¡BIENVENIDO A LA CASA DE LAS FIJAS! 🔥\n\n"
        "📈 ¿Listo para ganar? Aprovecha nuestras ofertas de acceso:\n\n"
        "--- 📋 PLANES DE ACCESO 📋 ---\n"
        "✅ Plan Semanal: S/ 10.00\n"
        "✅ Plan Mensual: S/ 15.00\n"
        "-------------------------------\n\n"
        "📲 ¡No te quedes fuera! Para inscribirte, escríbenos aquí:\n"
        "👉 +51 924 747 066 👈\n\n"
        "¡Tu mejor jugada empieza hoy! 💰"
    )
    
    # Ruta de tu imagen
    ruta_imagen = 'IMG_20260708_181916_435.jpg'
    
    try:
        with open(ruta_imagen, 'rb') as foto:
            await update.message.reply_photo(photo=foto, caption=mensaje)
    except FileNotFoundError:
        # Si no encuentra la foto, envía el texto solo como respaldo
        await update.message.reply_text(mensaje)

if __name__ == '__main__':
    app = ApplicationBuilder().token('8864924864:AAF3Cvt3rvymEc4UNqjogs1awYZ5-SpFgRc').build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

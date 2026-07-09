from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (ApplicationBuilder, CommandHandler, CallbackQueryHandler, 
                          MessageHandler, filters, ContextTypes, ConversationHandler)
from supabase import create_client
from datetime import datetime
from flask import Flask
from threading import Thread

# --- CONFIGURACIÓN ---
TOKEN = '8864924864:AAF3Cvt3rvymEc4UNqjogs1awYZ5-SpFgRc'
ADMIN_ID = '8996437844'
SUPABASE_URL = 'https://vvsuwkaqsiwbdbsulpyz.supabase.co'
SUPABASE_KEY = 'sb_secret_8F0rm3_wXOtK7BVx1eLTcQ_MgDCpsPh'
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- SISTEMA KEEP ALIVE ---
app_flask = Flask('')
@app_flask.route('/')
def home(): return "Bot activo 24/7"
def run_flask(): app_flask.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run_flask, daemon=True).start()

# --- ESTADOS ---
SELECCIONANDO_PLAN, ESPERANDO_PAGO = range(2)

# --- FUNCIONES ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    teclado = [
        [InlineKeyboardButton("Semanal (S/ 10)", callback_data='Semanal')],
        [InlineKeyboardButton("Mensual (S/ 15)", callback_data='Mensual')]
    ]
    await update.message.reply_text("🔥 ¡Bienvenido a LA CASA DE LAS FIJAS! 🔥\nSelecciona tu plan:", 
                                    reply_markup=InlineKeyboardMarkup(teclado))
    return SELECCIONANDO_PLAN

async def plan_seleccionado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['plan'] = query.data
    await query.edit_message_text(f"Has elegido el plan **{query.data}**.\n"
                                  "💰 Realiza el pago a: 937005352 (Plin).\n"
                                  "📸 Envía la captura para activar tu acceso.")
    return ESPERANDO_PAGO

async def recibir_pago(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    plan = context.user_data.get('plan', 'No especificado')
    
    # Notificar al Admin con botones
    teclado_admin = [
        [InlineKeyboardButton("✅ Aprobar", callback_data=f'aprobar_{user.id}')],
        [InlineKeyboardButton("❌ Rechazar", callback_data=f'rechazar_{user.id}')]
    ]
    await context.bot.send_photo(chat_id=ADMIN_ID, photo=update.message.photo[-1].file_id, 
                                 caption=f"🚨 Nuevo pago: {user.first_name}\nPlan: {plan}",
                                 reply_markup=InlineKeyboardMarkup(teclado_admin))
    
    await update.message.reply_text("✅ Captura enviada. El admin la validará pronto.")
    return ConversationHandler.END

async def admin_decision(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    accion, cliente_id = query.data.split('_')
    
    if accion == 'aprobar':
        # Registrar en DB
        supabase.table("Clientes").insert({"nombre": "Cliente", "username": str(cliente_id), "fecha": datetime.now().strftime("%Y-%m-%d")}).execute()
        # Enviar enlace real
        await context.bot.send_message(chat_id=cliente_id, text="🎉 ¡Pago aprobado! Aquí tienes el acceso:\n\nhttps://t.me/+Lr7vNO7vqTQyNzhh")
        await query.edit_message_caption(caption="✅ Aprobado y acceso enviado.")
    else:
        await context.bot.send_message(chat_id=cliente_id, text="❌ Tu pago fue rechazado.")
        await query.edit_message_caption(caption="❌ Rechazado.")

# --- MAIN ---
if __name__ == '__main__':
    keep_alive()
    app = ApplicationBuilder().token(TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELECCIONANDO_PLAN: [CallbackQueryHandler(plan_seleccionado)],
            ESPERANDO_PAGO: [MessageHandler(filters.PHOTO, recibir_pago)]
        },
        fallbacks=[CommandHandler('cancel', lambda u, c: ConversationHandler.END)]
    )
    
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(admin_decision, pattern='^(aprobar_|rechazar_)'))
    app.run_polling()

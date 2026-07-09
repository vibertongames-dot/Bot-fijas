from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (ApplicationBuilder, CommandHandler, CallbackQueryHandler, 
                          MessageHandler, filters, ContextTypes, ConversationHandler)
from supabase import create_client
from datetime import datetime
from flask import Flask
from threading import Thread
import requests

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

# --- FUNCIONES DE COMPRA ---
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
    await query.edit_message_text(f"Has elegido el plan **{query.data}**.\n💰 Pago: 937005352 (Plin).\n📸 Envía la captura aquí.")
    return ESPERANDO_PAGO

async def recibir_pago(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    plan = context.user_data.get('plan', 'No especificado')
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
        supabase.table("Clientes").insert({"nombre": "Cliente", "username": str(cliente_id), "fecha": datetime.now().strftime("%Y-%m-%d")}).execute()
        await context.bot.send_message(chat_id=cliente_id, text="🎉 ¡Pago aprobado! Acceso: https://t.me/+Lr7vNO7vqTQyNzhh")
        await query.edit_message_caption(caption="✅ Aprobado y acceso enviado.")
    else:
        await context.bot.send_message(chat_id=cliente_id, text="❌ Tu pago fue rechazado.")
        await query.edit_message_caption(caption="❌ Rechazado.")

# --- FUNCION DE ESTADISTICAS INTEGRADA ---
async def en_vivo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = "https://free-api-live-football-data.p.rapidapi.com/football-live-scores"
    headers = {
        "x-rapidapi-key": "191cfa1b2fmsh745862b43b68387p178540jsn7b4150aa4794",
        "x-rapidapi-host": "free-api-live-football-data.p.rapidapi.com"
    }
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        
        # Procesamiento de respuesta
        if isinstance(data, list) and len(data) > 0:
            mensaje = "📊 **Partidos en vivo ahora:**\n\n"
            for p in data[:5]:
                mensaje += f"⚽ {p.get('homeTeam', 'Local')} vs {p.get('awayTeam', 'Visita')} -> {p.get('score', 'En juego')}\n"
            await update.message.reply_text(mensaje, parse_mode='Markdown')
        else:
            await update.message.reply_text("⚽ No hay partidos en vivo en este momento.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error al obtener estadísticas: {str(e)}")

# --- MAIN ---
if __name__ == '__main__':
    keep_alive()
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Comandos
    app.add_handler(CommandHandler("en_vivo", en_vivo))
    
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

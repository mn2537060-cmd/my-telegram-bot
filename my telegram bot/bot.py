import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

TOKEN = "8816631552:AAFbBjYVxH0zHU-mqIL3GLB3aoE0tVxUlMY"

AGENT_TEXT = (
    "O agente explicará o processo de trabalho passo a passo. "
    "Você pode perguntar abertamente ao agente sobre seu salário, pagamento e sobre o trabalho. "
    "Aproveite o processo e obtenha ótimos lucros!"
)

# === RENDER အတွက် WEB SERVER စနစ် ===
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_health_server():
    server = HTTPServer(('0.0.0.0', 10000), HealthCheckHandler)
    server.serve_forever()

# ==================== BOT LOGIC ====================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("completed_steps") == True:
        await update.message.reply_text(AGENT_TEXT)
        return
        
    context.user_data["completed_steps"] = False
    keyboard = [[InlineKeyboardButton("Yes (Sim) ✅", callback_data="step1_yes"), InlineKeyboardButton("No (Não) ❌", callback_data="step1_no")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Olá, gostaria de saber mais sobre a vaga?", reply_markup=reply_markup)

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "step1_no":
        await query.message.reply_text("Obrigada")
    elif query.data == "step1_yes":
        keyboard = [[InlineKeyboardButton("Yes (Sim) ✅", callback_data="step2_yes"), InlineKeyboardButton("No (Não) ❌", callback_data="step2_no")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        step2_text = ("Permita-me explicar em detalhes o processo para você obter uma renda diária. "
                      "A nossa empresa, Annalect, trabalha impulsionando as vendas de produtos de diversos "
                      "comerciantes através de compras simuladas, e você receberá uma comissão por isso. "
                      "Se você tiver interesse, por favor, clique em 'Yes' (Sim)")
        await query.message.reply_text(step2_text, reply_markup=reply_markup)
    elif query.data == "step2_no":
        await query.message.reply_text("Obrigada")
    elif query.data == "step2_yes":
        keyboard = [[InlineKeyboardButton("OK 👌", callback_data="step3_ok")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        step3_text = ("Por favor, aguarde um momento enquanto eu te conecto com o nosso orientador "
                      "e Agente Oficial da Annalect, para que você possa entender melhor sobre o trabalho antes de começar")
        await query.message.reply_text(step3_text, reply_markup=reply_markup)
    elif query.data == "step3_ok":
        await query.message.reply_text("Por favor, aguarde 15 segundos...")
        await asyncio.sleep(15)
        final_text = "Este é o link do Telegram da sua orientadora exclusiva. Por favor, fale com ela para começar https://t.me/Lena1995465"
        await update.message.reply_text(final_text)
        context.user_data["completed_steps"] = True

async def echo_reply(update: Update, update_context: ContextTypes.DEFAULT_TYPE):
    if update_context.user_data.get("completed_steps") == True:
        await update.message.reply_text(AGENT_TEXT)

if __name__ == "__main__":
    threading.Thread(target=run_health_server, daemon=True).start()
    print("Bot iniciado com sucesso...")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_reply))
    app.run_polling()
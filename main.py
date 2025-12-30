import os, logging, asyncio, threading, http.server, socketserver
from groq import Groq
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- 1. AYARLAR ---
TOKEN = "8031564377:AAHjJXBQ-b6f0BnKdbf6T7iwUjs1fCA7dW0"
# Anahtarı koda gömüyoruz ki Render'daki okuma hatası bitsin
GROQ_API_KEY = "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"

client = Groq(api_key=GROQ_API_KEY)

# LİNKLER
LINK_GIRIS = "https://cutt.ly/drVOi2EN"
LINK_BONUSLAR = "https://starzbet422.com/tr-tr/info/promos"
LINK_CANLI_DESTEK = "https://service.3kanumaigc.com/chatwindow.aspx?siteId=90005302&planId=1b050682-cde5-4176-8236-3bb94c891197#"
LINK_MINI_APP = "https://telegram-mini-app-umber-chi.vercel.app"

# --- 2. FONKSİYONLAR ---
def ana_menu_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎰 STARZBET MİNİ APP", web_app=WebAppInfo(url=LINK_MINI_APP))],
        [InlineKeyboardButton("💳 DİNAMİK PAY", callback_data="btn_info"), InlineKeyboardButton("🎰 SLOT %100", callback_data="btn_info")],
        [InlineKeyboardButton("⚽ SPOR %100", callback_data="btn_info"), InlineKeyboardButton("✨ %35 KAYIP", callback_data="btn_info")],
        [InlineKeyboardButton("📱 MOBİL UYGULAMA", callback_data="btn_info"), InlineKeyboardButton("🎧 DESTEK", url=LINK_CANLI_DESTEK)],
        [InlineKeyboardButton("🔗 GÜNCEL GİRİŞ ADRESİ", url=LINK_GIRIS)]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("<b>Starzbet Asistanına Hoş Geldiniz.</b>\nSize nasıl yardımcı olabilirim?", reply_markup=ana_menu_kb(), parse_mode=ParseMode.HTML)

async def ai_asistan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "system", "content": "Sen Starzbet asistanısın."}, {"role": "user", "content": update.message.text}],
            model="llama-3.3-70b-versatile",
        )
        await update.message.reply_text(chat_completion.choices[0].message.content, reply_markup=ana_menu_kb())
    except Exception:
        await update.message.reply_text("Şu an hizmet veremiyorum, lütfen butonları kullanın.", reply_markup=ana_menu_kb())

async def buton_tiklama(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("Güncel kampanyalar ve giriş için lütfen sitemizi ziyaret edin.", reply_markup=ana_menu_kb())

# --- 3. RENDER İÇİN PORT VE BAŞLATICI ---
def run_server():
    socketserver.TCPServer(("", int(os.environ.get("PORT", 8080))), http.server.SimpleHTTPRequestHandler).serve_forever()

if __name__ == '__main__':
    threading.Thread(target=run_server, daemon=True).start()
    # 3.13 için en güvenli başlatma:
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buton_tiklama))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), ai_asistan))
    print("🚀 Bot Aktif!")
    app.run_polling(drop_pending_updates=True)

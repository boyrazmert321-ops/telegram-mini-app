import os
import logging
import asyncio
import http.server
import socketserver
import threading
import google.generativeai as genai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- 1. AYARLAR ---
TOKEN = "8031564377:AAHjJXBQ-b6f0BnKdbf6T7iwUjs1fCA7dW0"
GEMINI_API_KEY = "AIzaSyDiUfTgQc66glH-1nSH3h_98S_kB4-x0k8"

LINK_GIRIS = "https://cutt.ly/drVOi2EN"
LINK_BONUSLAR = "https://starzbet422.com/tr-tr/info/promos"
LINK_CANLI_DESTEK = "https://service.3kanumaigc.com/chatwindow.aspx?siteId=90005302&planId=1b050682-cde5-4176-8236-3bb94c891197#"
LINK_MINI_APP = "https://telegram-mini-app-umber-chi.vercel.app"

# --- 2. YAPAY ZEKA (EN GARANTİCİ MODEL İSMİ) ---
genai.configure(api_key=GEMINI_API_KEY)
# 'models/' ön eki ve '-latest' takısı 404 hatalarını çözmek için en güvenli yoldur
model = genai.GenerativeModel('models/gemini-1.5-flash-latest')

AI_TALIMATI = (
    "Sen Starzbet profesyonel asistanısın. Kısa ve öz cevaplar ver. "
    "Hafta sonu %35, hafta içi %30 kayıp bonusu var. Dinamik Pay yatırımda tek yöntem."
)

# --- 3. GÖRSEL YOLLARI ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEDIA = {
    "ANA_MENU": os.path.join(BASE_DIR, "ana.jpg"),
    "DINAMIK_PAY": os.path.join(BASE_DIR, "dinamik.jpg"),
    "SLOT_100": os.path.join(BASE_DIR, "casinohosgelin.jpg"),
    "SPOR_100": os.path.join(BASE_DIR, "sporhosgelin.jpg"),
    "KRIPTO_100": os.path.join(BASE_DIR, "kripto.jpg"),
    "KAYIP_35": os.path.join(BASE_DIR, "35kayip.jpg"),
    "MOBIL_APP": os.path.join(BASE_DIR, "uygulama.jpg")
}

# --- 4. RENDER SUNUCUSU ---
def run_dummy_server():
    PORT = int(os.environ.get("PORT", 8080))
    handler = http.server.SimpleHTTPRequestHandler
    try:
        with socketserver.TCPServer(("", PORT), handler) as httpd:
            httpd.serve_forever()
    except Exception: pass
threading.Thread(target=run_dummy_server, daemon=True).start()

# --- 5. KLAVYELER ---
def ana_menu_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎰 STARZBET MİNİ APP", web_app=WebAppInfo(url=LINK_MINI_APP))],
        [InlineKeyboardButton("💳 DİNAMİK PAY YATIRIM", callback_data="btn_dinamik")],
        [InlineKeyboardButton("🎰 SLOT %100", callback_data="btn_slot"), InlineKeyboardButton("⚽ SPOR %100", callback_data="btn_spor")],
        [InlineKeyboardButton("🪙 KRİPTO %100", callback_data="btn_kripto"), InlineKeyboardButton("✨ %35 KAYIP", callback_data="btn_kayip")],
        [InlineKeyboardButton("📱 MOBİL UYGULAMA", callback_data="btn_app"), InlineKeyboardButton("🎧 CANLI DESTEK", url=LINK_CANLI_DESTEK)],
        [InlineKeyboardButton("🔗 GÜNCEL GİRİŞ ADRESİ", url=LINK_GIRIS)]
    ])

def detay_kb(bonus_mu=False):
    url_target = LINK_BONUSLAR if bonus_mu else LINK_GIRIS
    return InlineKeyboardMarkup([[InlineKeyboardButton("🎁 İNCELE", url=url_target)], [InlineKeyboardButton("⬅️ GERİ", callback_data="btn_back")]])

# --- 6. ASİSTAN VE KOMUTLAR ---
async def ai_asistan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    prompt = f"{AI_TALIMATI}\nKullanıcı: {update.message.text}"
    try:
        # Güvenlik ayarlarını BLOCK_NONE yaparak engelleri kaldırıyoruz
        safety = [{"category": c, "threshold": "BLOCK_NONE"} for c in ["HARM_CATEGORY_HARASSMENT", "HARM_CATEGORY_HATE_SPEECH", "HARM_CATEGORY_SEXUALLY_EXPLICIT", "HARM_CATEGORY_DANGEROUS_CONTENT"]]
        response = model.generate_content(prompt, safety_settings=safety)
        await update.message.reply_text(response.text, parse_mode=ParseMode.HTML, reply_markup=ana_menu_kb())
    except Exception as e:
        await update.message.reply_text(f"❌ AI Bağlantı Hatası: {str(e)}\nLütfen butonları kullanın.", reply_markup=ana_menu_kb())

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query: await update.callback_query.message.delete()
    text = "<b>Starzbet Asistanına Hoş Geldiniz.</b>\nSorularınızı sorabilir veya menüden işlem yapabilirsiniz."
    if os.path.exists(MEDIA["ANA_MENU"]):
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(MEDIA["ANA_MENU"], 'rb'), caption=text, reply_markup=ana_menu_kb(), parse_mode=ParseMode.HTML)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text, reply_markup=ana_menu_kb(), parse_mode=ParseMode.HTML)

async def buton_tiklama(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    info = {
        "btn_dinamik": (MEDIA["DINAMIK_PAY"], "💳 Dinamik Pay ile anında yatırım yapabilirsiniz.", False),
        "btn_slot": (MEDIA["SLOT_100"], "🎰 %100 Slot Hoş Geldin Bonusu.", True),
        "btn_spor": (MEDIA["SPOR_100"], "⚽ %100 Spor Hoş Geldin Bonusu.", True),
        "btn_kripto": (MEDIA["KRIPTO_100"], "🪙 %100 Kripto Bonusu.", True),
        "btn_kayip": (MEDIA["KAYIP_35"], "✨ Hafta sonu %35, hafta içi %30 kayıp bonusu.", True),
        "btn_app": (MEDIA["MOBIL_APP"], "📱 Starzbet mobil uygulamasını indirin.", False)
    }
    if query.data in info:
        img, txt, is_b = info[query.data]
        await query.message.delete()
        if os.path.exists(img):
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(img, 'rb'), caption=txt, reply_markup=detay_kb(is_b), parse_mode=ParseMode.HTML)
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=txt, reply_markup=detay_kb(is_b), parse_mode=ParseMode.HTML)
    elif query.data == "btn_back": await start(update, context)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    # drop_pending_updates=True sayesinde o meşhur Conflict hatasından kurtuluyoruz
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(buton_tiklama))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), ai_asistan))
    application.run_polling(drop_pending_updates=True)

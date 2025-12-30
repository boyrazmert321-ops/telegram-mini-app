import os
import logging
import asyncio
import http.server
import socketserver
import threading
from groq import Groq
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- 1. AYARLAR VE KİMLİK BİLGİLERİ ---
TOKEN = "8031564377:AAHjJXBQ-b6f0BnKdbf6T7iwUjs1fCA7dW0"
GROQ_API_KEY = "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"

# Bağlantılar
LINK_GIRIS = "https://cutt.ly/drVOi2EN"
LINK_BONUSLAR = "https://starzbet422.com/tr-tr/info/promos"
LINK_CANLI_DESTEK = "https://service.3kanumaigc.com/chatwindow.aspx?siteId=90005302&planId=1b050682-cde5-4176-8236-3bb94c891197#"
LINK_MINI_APP = "https://telegram-mini-app-umber-chi.vercel.app"

# Groq İstemcisi
client = Groq(api_key=GROQ_API_KEY)

# --- 2. YAPAY ZEKA TALİMATI ---
AI_SISTEM_MESAJI = (
    "Sen Starzbet sitesinin profesyonel, samimi ve yardımsever yapay zeka asistanısın. "
    "Müşterilere Starzbet hakkında bilgi ver. Asla 'kanka' deme. "
    "Önemli Bilgiler: Hafta sonu %35 kayıp bonusu, hafta içi %30 kayıp bonusu var. "
    "Yatırımlarda Dinamik Pay kullanılır. Payfix yoktur. "
    "Kısa, öz ve çözüm odaklı cevaplar ver."
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

# --- 4. RENDER PORT AÇICI ---
def run_dummy_server():
    PORT = int(os.environ.get("PORT", 8080))
    handler = http.server.SimpleHTTPRequestHandler
    try:
        with socketserver.TCPServer(("", PORT), handler) as httpd:
            httpd.serve_forever()
    except: pass
threading.Thread(target=run_dummy_server, daemon=True).start()

# --- 5. KLAVYELER ---
def ana_menu_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎰 STARZBET MİNİ APP", web_app=WebAppInfo(url=LINK_MINI_APP))],
        [InlineKeyboardButton("💳 DİNAMİK PAY İLE YATIRIM", callback_data="btn_dinamik")],
        [InlineKeyboardButton("🎰 SLOT %100 HOŞ GELDİN", callback_data="btn_slot"), 
         InlineKeyboardButton("⚽ SPOR %100 HOŞ GELDİN", callback_data="btn_spor")],
        [InlineKeyboardButton("🪙 KRİPTO %100 HOŞ GELDİN", callback_data="btn_kripto"), 
         InlineKeyboardButton("✨ %35 KAYIP BONUSU", callback_data="btn_kayip")],
        [InlineKeyboardButton("📱 MOBİL UYGULAMA", callback_data="btn_app"), 
         InlineKeyboardButton("🎧 CANLI DESTEK", url=LINK_CANLI_DESTEK)],
        [InlineKeyboardButton("🔗 GÜNCEL GİRİŞ ADRESİ", url=LINK_GIRIS)]
    ])

def detay_kb(bonus_mu=False):
    url_target = LINK_BONUSLAR if bonus_mu else LINK_GIRIS
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎁 İNCELE / GİT", url=url_target)],
        [InlineKeyboardButton("⬅️ ANA MENÜ", callback_data="btn_back")]
    ])

# --- 6. FONKSİYONLAR ---
async def ai_asistan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    
    try:
        # Groq üzerinden Llama 3 modelini çağırıyoruz
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": AI_SISTEM_MESAJI},
                {"role": "user", "content": update.message.text}
            ],
            temperature=0.7,
            max_tokens=512
        )
        cevap = completion.choices[0].message.content
        await update.message.reply_text(cevap, parse_mode=ParseMode.HTML, reply_markup=ana_menu_kb())
    except Exception as e:
        logging.error(f"AI Hatası: {e}")
        await update.message.reply_text("Şu an yoğunluk nedeniyle yanıt veremiyorum, lütfen butonları kullanın.", reply_markup=ana_menu_kb())

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = "<b>Starzbet'e Hoş Geldiniz.</b>\n\nİşlemleriniz için aşağıdaki menüyü kullanabilir veya bana soru sorabilirsiniz."
    
    if update.callback_query:
        try: await update.callback_query.message.delete()
        except: pass

    if os.path.exists(MEDIA["ANA_MENU"]):
        await context.bot.send_photo(chat_id=chat_id, photo=open(MEDIA["ANA_MENU"], 'rb'), caption=text, reply_markup=ana_menu_kb(), parse_mode=ParseMode.HTML)
    else:
        await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=ana_menu_kb(), parse_mode=ParseMode.HTML)

async def buton_tiklama(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    info = {
        "btn_dinamik": (MEDIA["DINAMIK_PAY"], "💳 Dinamik Pay ile anında yatırım yapabilirsiniz.", False),
        "btn_slot": (MEDIA["SLOT_100"], "🎰 %100 Slot Hoş Geldin Bonusu aktif.", True),
        "btn_spor": (MEDIA["SPOR_100"], "⚽ %100 Spor Hoş Geldin Bonusu aktif.", True),
        "btn_kripto": (MEDIA["KRIPTO_100"], "🪙 %100 Kripto Bonusu aktif.", True),
        "btn_kayip": (MEDIA["KAYIP_35"], "✨ Hafta sonu %35 kayıp bonusu.", True),
        "btn_app": (MEDIA["MOBIL_APP"], "📱 Mobil uygulamayı hemen indirin.", False)
    }
    
    if query.data in info:
        img, txt, is_b = info[query.data]
        try: await query.message.delete()
        except: pass
        
        if os.path.exists(img):
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(img, 'rb'), caption=txt, reply_markup=detay_kb(is_b), parse_mode=ParseMode.HTML)
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=txt, reply_markup=detay_kb(is_b), parse_mode=ParseMode.HTML)
    elif query.data == "btn_back":
        await start(update, context)

# --- 7. ÇALIŞTIRICI ---
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(buton_tiklama))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), ai_asistan))
    
    print("🚀 Starzbet Groq Botu Aktif Ediliyor...")
    application.run_polling(drop_pending_updates=True)

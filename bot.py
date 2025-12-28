import os
import logging
import asyncio
import http.server
import socketserver
import threading
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# --- GÖRSEL YOLLARI (OS JOIN İLE GARANTİYE ALINDI) ---
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

# --- AYARLAR ---
TOKEN = "8031564377:AAHjJXBQ-b6f0BnKdbf6T7iwUjs1fCA7dW0"
LINK_GIRIS = "https://cutt.ly/drVOi2EN"
LINK_CANLI_DESTEK = "https://service.3kanumaigc.com/chatwindow.aspx?siteId=90005302&planId=1b050682-cde5-4176-8236-3bb94c891197#"
LINK_MINI_APP = "https://telegram-mini-app-umber-chi.vercel.app"

# --- RENDER İÇİN PORT AÇMA ---
def run_dummy_server():
    PORT = int(os.environ.get("PORT", 8080))
    handler = http.server.SimpleHTTPRequestHandler
    try:
        with socketserver.TCPServer(("", PORT), handler) as httpd:
            httpd.serve_forever()
    except Exception: pass
threading.Thread(target=run_dummy_server, daemon=True).start()

# --- BUTONLAR ---
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

def detay_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🌐 SİTEYE GİT", url=LINK_GIRIS)],
        [InlineKeyboardButton("⬅️ GERİ DÖN", callback_data="btn_back")]
    ])

# --- FONKSİYONLAR ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = (
        "<b>Starzbet'e Hoş Geldiniz.</b>\n\n"
        "Aşağıdaki menü üzerinden işlemlerinizi yapabilir, "
        "size özel sunulan fırsatlara göz atabilirsiniz."
    )
    
    if update.callback_query:
        await update.callback_query.message.delete()

    if os.path.exists(MEDIA["ANA_MENU"]):
        await context.bot.send_photo(chat_id=chat_id, photo=open(MEDIA["ANA_MENU"], 'rb'), 
                                     caption=text, reply_markup=ana_menu_kb(), parse_mode=ParseMode.HTML)
    else:
        await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=ana_menu_kb(), parse_mode=ParseMode.HTML)

async def buton_tiklama(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    await query.answer()

    info = {
        "btn_dinamik": (MEDIA["DINAMIK_PAY"], "💳 <b>Dinamik Pay İle Yatırım</b>\n\nDinamik Pay ile bekleme süresi olmadan dilediğiniz tutarda anında yatırım yapabilirsiniz."),
        "btn_slot": (MEDIA["SLOT_100"], "🎰 <b>Slot Hoş Geldin Bonusu</b>\n\nİlk yatırımınıza özel %100 Slot bonusu ile kazancınızı katlamaya başlayın."),
        "btn_spor": (MEDIA["SPOR_100"], "⚽ <b>Spor Hoş Geldin Bonusu</b>\n\nSpor bahislerinde ilk yatırımınıza özel %100 bonus fırsatından yararlanın."),
        "btn_kripto": (MEDIA["KRIPTO_100"], "🪙 <b>Kripto Yatırım Bonusu</b>\n\nKripto yatırımlarınıza özel %100 bonus avantajı ile Starzbet'te yerinizi alın."),
        "btn_kayip": (MEDIA["KAYIP_35"], "✨ <b>Kayıp Bonusu</b>\n\nCuma, Cumartesi ve Pazar günleri %35, hafta içi ise %30 kayıp bonusu ile şansınız devam ediyor."),
        "btn_app": (MEDIA["MOBIL_APP"], "📱 <b>Mobil Uygulama</b>\n\nStarzbet uygulamasını indirerek güncel adrese ihtiyaç duymadan kesintisiz erişim sağlayın.")
    }

    if data in info:
        gorsel, aciklama = info[data]
        await query.message.delete()
        if os.path.exists(gorsel):
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(gorsel, 'rb'), 
                                         caption=aciklama, reply_markup=detay_kb(), parse_mode=ParseMode.HTML)
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=aciklama, 
                                           reply_markup=detay_kb(), parse_mode=ParseMode.HTML)
    elif data == "btn_back":
        await start(update, context)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(buton_tiklama))

    print("🚀 Starzbet Bot Aktif!")
    application.run_polling()

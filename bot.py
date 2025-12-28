import os
import logging
import asyncio
import http.server
import socketserver
import threading
from datetime import time
import pytz
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, BotCommand
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ==========================================
# 🖼️ GÖRSEL KONTROL MERKEZİ (MEDIA MANAGER)
# Buradaki isimleri GitHub'daki dosyalarla eşle
# ==========================================
MEDIA = {
    "ANA_MENU": "ana.jpg",        # Ana karşılama görseli
    "DINAMIK_PAY": "dinamik.jpg",  # Dinamik Pay bilgilendirme
    "SLOT_100": "casinohosgeldin.jpg",      # Slot Hoş Geldin
    "SPOR_100": "sporhosgel.jpg",      # Spor Hoş Geldin
    "KRIPTO_100": "kripto.jpg",  # Kripto Hoş Geldin
    "KAYIP_35": "35kayip.jpg",     # Kayıp Bonusu görseli
    "MOBIL_APP": "uygulama.jpg"       # Uygulama indirme görseli
}

# --- AYARLAR ---
TOKEN = "8031564377:AAHjJXBQ-b6f0BnKdbf6T7iwUjs1fCA7dW0"
LINK_GIRIS = "https://cutt.ly/drVOi2EN"
LINK_CANLI_DESTEK = "https://service.3kanumaigc.com/chatwindow.aspx?siteId=90005302&planId=1b050682-cde5-4176-8236-3bb94c891197#"
LINK_MINI_APP = "https://telegram-mini-app-umber-chi.vercel.app"

# --- RENDER SERVER ---
def run_dummy_server():
    PORT = int(os.environ.get("PORT", 8080))
    handler = http.server.SimpleHTTPRequestHandler
    try:
        with socketserver.TCPServer(("", PORT), handler) as httpd:
            httpd.serve_forever()
    except Exception: pass
threading.Thread(target=run_dummy_server, daemon=True).start()

# --- KLAVYE TASARIMLARI ---
def ana_menu_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎰 STARZBET MİNİ APP", web_app=WebAppInfo(url=LINK_MINI_APP))],
        [InlineKeyboardButton("💳 DİNAMİK PAY İLE ANINDA YATIRIM", callback_data="btn_dinamik")],
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
        [InlineKeyboardButton("🌐 HEMEN SİTEYE GİT", url=LINK_GIRIS)],
        [InlineKeyboardButton("⬅️ ANA MENÜYE DÖN", callback_data="btn_back")]
    ])

# --- FONKSİYONLAR ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = (
        "⭐ <b>Starzbet Profesyonel VIP Destek Sistemine Hoş Geldiniz.</b>\n\n"
        "Tüm finansal işlemleriniz ve güncel promosyonlarımız hakkında detaylı bilgi "
        "almak için aşağıdaki menüyü kullanabilirsiniz."
    )
    
    # Callback geliyorsa eskiyi silip yeniyi temiz gönder
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

    # Bilgi Havuzu
    info = {
        "btn_dinamik": (MEDIA["DINAMIK_PAY"], "💳 <b>Dinamik Pay İle Anında Yatırım</b>\n\nSistemimizde Dinamik Pay altyapısı aktiftir. Herhangi bir aracı kurum bekleme süresi olmaksızın, dilediğiniz tutarda anlık yatırım yapabilirsiniz."),
        "btn_slot": (MEDIA["SLOT_100"], "🎰 <b>%100 Slot Hoş Geldin Bonusu</b>\n\nİlk yatırımınıza özel %100 Slot yatırım bonusu ile kazancınızı katlayın. Profesyonel Slot deneyimi Starzbet kalitesiyle sizi bekliyor."),
        "btn_spor": (MEDIA["SPOR_100"], "⚽ <b>%100 Spor Hoş Geldin Bonusu</b>\n\nYüksek oranlar ve geniş bahis bülteni ile ilk yatırımınızda bakiyenizi ikiye katlayın. Spor bahislerinde VIP avantajları aktif."),
        "btn_kripto": (MEDIA["KRIPTO_100"], "🪙 <b>%100 Kripto Yatırım Bonusu</b>\n\nKripto yatırımlarınıza özel %100 bonus fırsatını kaçırmayın. Tamamen güvenli ve anonim yatırım imkanıyla sınırları zorlayın."),
        "btn_kayip": (MEDIA["KAYIP_35"], "✨ <b>%35 VIP Kayıp Bonusu</b>\n\nCuma, Cumartesi ve Pazar günleri %35, hafta içi ise %30 oranında kayıp bonusu ile her zaman kazanma şansınız devam etmektedir."),
        "btn_app": (MEDIA["MOBIL_APP"], "📱 <b>Kesintisiz Mobil Erişim</b>\n\nAndroid ve iOS cihazlar için özel geliştirilen Starzbet uygulamasını indirerek, adres güncellemelerinden etkilenmeden oyunlarınıza devam edebilirsiniz.")
    }

    if data in info:
        gorsel, aciklama = info[data]
        await query.message.delete() # Temiz bir geçiş için
        if os.path.exists(gorsel):
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(gorsel, 'rb'), 
                                         caption=aciklama, reply_markup=detay_kb(), parse_mode=ParseMode.HTML)
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=aciklama, 
                                           reply_markup=detay_kb(), parse_mode=ParseMode.HTML)
    elif data == "btn_back":
        await start(update, context)

# --- ANA ÇALIŞTIRICI ---
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(buton_tiklama))

    print("🚀 Starzbet VIP Otomasyon v4.0 Aktif!")
    application.run_polling()

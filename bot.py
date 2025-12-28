import os
import logging
import asyncio
import http.server
import socketserver
import threading
from datetime import time
import pytz
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, BotCommand
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- 1. RENDER SAHTE SUNUCU ---
def run_dummy_server():
    PORT = int(os.environ.get("PORT", 8080))
    handler = http.server.SimpleHTTPRequestHandler
    try:
        with socketserver.TCPServer(("", PORT), handler) as httpd:
            print(f"🚀 Render sahte sunucu {PORT} portunda aktif.")
            httpd.serve_forever()
    except Exception as e:
        print(f"Sunucu hatası: {e}")

threading.Thread(target=run_dummy_server, daemon=True).start()

# --- 2. AYARLAR VE LİNKLER ---
TOKEN = "8031564377:AAHjJXBQ-b6f0BnKdbf6T7iwUjs1fCA7dW0"
RESIM_YOLU = "banner.jpg"
ID_LISTE_DOSYASI = "kullanicilar.txt"
TR_SAAT_DILIMI = pytz.timezone('Europe/Istanbul')

LINK_GIRIS           = "https://cutt.ly/drVOi2EN"
LINK_BONUS           = "https://starzbet422.com/tr-tr/info/promos"
LINK_CANLI_DESTEK    = "https://service.3kanumaigc.com/chatwindow.aspx?siteId=90005302&planId=1b050682-cde5-4176-8236-3bb94c891197#"
LINK_APP             = "https://starzmobil.com/indir/"
LINK_MINI_APP        = "https://telegram-mini-app-umber-chi.vercel.app" 

# --- 3. YARDIMCI FONKSİYONLAR ---
def kullanici_kaydet(user_id):
    user_id = str(user_id)
    if not os.path.exists(ID_LISTE_DOSYASI):
        with open(ID_LISTE_DOSYASI, "w") as f: f.write("")
    with open(ID_LISTE_DOSYASI, "r") as f:
        kayitli = f.read().splitlines()
    if user_id not in kayitli:
        with open(ID_LISTE_DOSYASI, "a") as f:
            f.write(user_id + "\n")

def kullanicilari_getir():
    if not os.path.exists(ID_LISTE_DOSYASI): return []
    with open(ID_LISTE_DOSYASI, "r") as f:
        return f.read().splitlines()

# --- 4. KLAVYELER (GÜNCELLENMİŞ) ---
def ana_menu_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎰 STARZBET MİNİ (OYNA)", web_app=WebAppInfo(url=LINK_MINI_APP))],
        [InlineKeyboardButton("💰 Yatırım Yöntemleri", callback_data="finans_yatirim"), InlineKeyboardButton("✨ Kayıp Bonusu", callback_data="bonus_kayip")],
        [InlineKeyboardButton("🎰 Hoş Geldin Bonusu", callback_data="bonus_hosgeldin"), InlineKeyboardButton("📱 Mobil Uygulama", callback_data="tech_app")],
        [InlineKeyboardButton("🧩 Giriş Sorunu", callback_data="tech_sorun")],
        [InlineKeyboardButton("🔗 GÜNCEL GİRİŞ", url=LINK_GIRIS), InlineKeyboardButton("🎧 CANLI DESTEK", url=LINK_CANLI_DESTEK)]
    ])

def geri_don_kb():
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ ANA MENÜYE DÖN", callback_data="btn_back")]])

# --- 5. KOMUTLAR VE HANDLERLAR ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    kullanici_kaydet(user.id)
    
    text = (
        f"🏆 <b>Hoş Geldin VIP Ortağım {user.first_name}!</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Starzbet dünyasında tüm kontrol senin elinde.\n"
        "İşlemlerin ve merak ettiğin her şey için doğru yerdesin. 🔥\n\n"
        "👇 <b>İşlem seçerek başlayalım:</b>"
    )
    
    target = update.message if update.message else update.callback_query.message
    
    if os.path.exists(RESIM_YOLU) and not update.callback_query:
        await target.reply_photo(photo=open(RESIM_YOLU, 'rb'), caption=text, reply_markup=ana_menu_kb(), parse_mode=ParseMode.HTML)
    else:
        if update.callback_query:
            await update.callback_query.edit_message_caption(caption=text, reply_markup=ana_menu_kb(), parse_mode=ParseMode.HTML)
        else:
            await target.reply_text(text, reply_markup=ana_menu_kb(), parse_mode=ParseMode.HTML)

async def buton_tiklama(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    await query.answer()

    cevaplar = {
        "finans_yatirim": "💰 <b>Yatırım Yöntemleri:</b>\n\nKanka artık Payfix yok, en hızlı yöntemimiz <b>Dinamik Pay</b> aktif! Dilediğin tutarda anında yatırım yapabilirsin. Ayrıca Papara ve Kripto seçeneklerimiz de açık.",
        "bonus_kayip": "✨ <b>Kayıp Bonusu:</b>\n\nStarzbet'te kaybetsen de yanındayız! Hafta içi <b>%30</b>'a varan, <b>CUMA, CUMARTESİ ve PAZAR</b> günleri ise direkt <b>%35</b> Kayıp Bonusu seni bekliyor!",
        "bonus_hosgeldin": "🎰 <b>Hoş Geldin Bonusu:</b>\n\nİlk yatırımına özel devasa çevrimsiz bonusun hazır. Yatırımını yap, hiçbir oyuna girmeden Canlı Destek hattına bağlan ve bonusunu iste!",
        "tech_app": "📱 <b>Mobil Uygulama:</b>\n\nBTK engellerine takılmadan oynamak için Android veya iOS cihazına uygulamamızı kurabilirsin. Link aşağıda mevcuttur!",
        "tech_sorun": "🧩 <b>Giriş Sorunu:</b>\n\nErişim sorunu yaşıyorsan VPN kapatıp tekrar dene veya 'GÜNCEL GİRİŞ' butonuna bas. Linkimiz her zaman günceldir."
    }

    if data in cevaplar:
        await query.edit_message_caption(caption=cevaplar[data], reply_markup=geri_don_kb(), parse_mode=ParseMode.HTML)
    elif data == "btn_back":
        await start(update, context)

async def kelime_takip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    msg = update.message.text.lower()
    kullanici_kaydet(update.effective_user.id)

    if any(k in msg for k in ["starzbet", "link", "giriş", "adres", "site", "güncel"]):
        text = "🚀 <b>STARZBET GÜNCEL GİRİŞ</b>\n━━━━━━━━━━━━━━━━━━━━\n🔗 " + LINK_GIRIS
        kb = [[InlineKeyboardButton("🟠 GÜNCEL GİRİŞ ADRESİ", url=LINK_GIRIS)]]
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)

# --- 6. PROMOSYON ZAMANLAYICISI (Hafta Sonu Vurgulu) ---
async def dm_promosyon_gonder(context: ContextTypes.DEFAULT_TYPE):
    user_ids = kullanicilari_getir()
    if not user_ids: return
    mesaj = (
        "🎁 <b>HAFTA SONUNA ÖZEL %35 KAYIP BONUSU!</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Bugün günlerden Starzbet! Kayıplarına anında %35 iade alarak şansını tekrar dene.\n\n"
        f"🔗 <a href='{LINK_GIRIS}'>GİRİŞ YAP VE İADENİ AL</a>"
    )
    for uid in user_ids:
        try:
            await context.bot.send_message(chat_id=uid, text=mesaj, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🚀 ŞİMDİ OYNA", url=LINK_GIRIS)]]), parse_mode=ParseMode.HTML)
            await asyncio.sleep(0.05)
        except: continue

# --- 7. ANA ÇALIŞTIRICI ---
if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
    application = ApplicationBuilder().token(TOKEN).build()

    async def set_commands():
        commands = [
            BotCommand("start", "🔥 VIP Menüyü Aç"),
            BotCommand("mini_app", "🎰 Mini Oyunları Oyna")
        ]
        await application.bot.set_my_commands(commands)

    # Promosyon Saatleri
    saatler = [time(12,0), time(18,0), time(22,0)]
    for s in saatler:
        application.job_queue.run_daily(dm_promosyon_gonder, time=s.replace(tzinfo=TR_SAAT_DILIMI))

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("mini_app", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), kelime_takip))
    application.add_handler(CallbackQueryHandler(buton_tiklama))

    print("🚀 Starzbet VIP Güncel Verilerle Aktif!")
    
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(set_commands())
    except: pass

    application.run_polling()

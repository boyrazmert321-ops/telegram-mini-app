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


def run_dummy_server():
    PORT = int(os.environ.get("PORT", 8080))
    handler = http.server.SimpleHTTPRequestHandler
    try:
        with socketserver.TCPServer(("", PORT), handler) as httpd:
            print(f"🚀 Render için sahte sunucu {PORT} portunda aktif.")
            httpd.serve_forever()
    except Exception as e:
        print(f"Sunucu hatası: {e}")

threading.Thread(target=run_dummy_server, daemon=True).start()


TOKEN = "8031564377:AAHjJXBQ-b6f0BnKdbf6T7iwUjs1fCA7dW0"
RESIM_YOLU = "banner.jpg"
ID_LISTE_DOSYASI = "kullanicilar.txt"
TR_SAAT_DILIMI = pytz.timezone('Europe/Istanbul')

LINK_GIRIS            = "https://cutt.ly/drVOi2EN"
LINK_OZEL_ORAN_SITE   = "https://ozeloranlar.com/"
LINK_OZEL_ORAN_KANAL  = "https://t.me/Starzbetgir"
LINK_BONUS            = "https://starzbet422.com/tr-tr/info/promos"
LINK_CANLI_DESTEK     = "https://service.3kanumaigc.com/chatwindow.aspx?siteId=90005302&planId=1b050682-cde5-4176-8236-3bb94c891197#"
LINK_APP              = "https://starzmobil.com/indir/"
LINK_MINI_APP         = "https://telegram-mini-app-umber-chi.vercel.app" 


def kullanici_kaydet(user_id):
    user_id = str(user_id)
    if not os.path.exists(ID_LISTE_DOSYASI):
        with open(ID_LISTE_DOSYASI, "w") as f: f.write("")
    
    with open(ID_LISTE_DOSYASI, "r") as f:
        kayitli = f.read().splitlines()
    
    if user_id not in kayitli:
        with open(ID_LISTE_DOSYASI, "a") as f:
            f.write(user_id + "\n")
        print(f"✅ Yeni kullanıcı DM listesine eklendi: {user_id}")

def kullanicilari_getir():
    if not os.path.exists(ID_LISTE_DOSYASI): return []
    with open(ID_LISTE_DOSYASI, "r") as f:
        return f.read().splitlines()


async def dm_promosyon_gonder(context: ContextTypes.DEFAULT_TYPE):
    user_ids = kullanicilari_getir()
    if not user_ids: return

    mesaj = (
        "🎁 <b>%35 KAYIP BONUS FIRSATI!</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "1️⃣ Cuma, Cumartesi ve Pazar günleri yaşadığın kayıplarına %35 Kayıp Bonusu Starzbet'te seni bekliyor!\n\n"
        "🎁 Ayrıca bugüne özel <b>HEDİYE 500 TL NAKİT</b> bonus için beklemede kal!\n\n"
        "2️⃣ <b>10 OYUNDA 200 FREESPİN BEDAVA!</b>\n"
        "💰 Max çarpan yakalama şansı sadece Starzbet'te!\n\n"
        "⚡ <b>Freespin Eklenecek Oyunlar:</b>\n"
        "• Starzbet Princess\n• Wisdom Of Athena 1000\n• Saray Rüyası\n• Sweet Bonanza Xmas\n"
        "• Big Bass Secrets\n• Candy Blitz Bombs\n\n"
        f"🔗 <a href='{LINK_GIRIS}'>HEMEN GİRİŞ YAP VE OYNA</a>"
    )
    kb = [[InlineKeyboardButton("🚀 ŞİMDİ OYNA", url=LINK_GIRIS)]]

    for uid in user_ids:
        try:
            await context.bot.send_message(chat_id=uid, text=mesaj, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)
            await asyncio.sleep(0.05) # Spam önleyici hız sınırlama
        except:
            continue


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  
    user_id = update.effective_user.id
    kullanici_kaydet(user_id)

    effective_message = update.message if update.message else update.callback_query.message
    text = (
        "🏆 <b>STARZBET MİNİ DÜNYASINA HOŞ GELDİN!</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Eğlence ve kazancın adresi Starzbet'te,\n"
        "Mini oyunlarımızı oynayarak vakit geçirebilir,\n"
        "Liderlik tablosunda yerini alabilirsin. 🔥\n\n"
        "🔗 <b>Hemen Başlamak İçin Dokun:</b> 👇"
    )
    kb = [
          [InlineKeyboardButton("🎰 STARZBET MİNİ (OYNA)", web_app=WebAppInfo(url=LINK_MINI_APP))],
          [InlineKeyboardButton("🟠 GÜNCEL GİRİŞ", url=LINK_GIRIS)],
          [InlineKeyboardButton("🎁 BONUSLAR", callback_data='btn_bonus'), InlineKeyboardButton("🎧 DESTEK", url=LINK_CANLI_DESTEK)],
          [InlineKeyboardButton("📱 MOBİL UYGULAMA", url=LINK_APP)]
         ]
    
    if os.path.exists(RESIM_YOLU):
        await effective_message.reply_photo(photo=open(RESIM_YOLU, 'rb'), caption=text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)
    else:
        await effective_message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)

async def kelime_takip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    msg = update.message.text.lower()
    kullanici_kaydet(update.effective_user.id) # Grupta konuşanı da listeye al

    if any(k in msg for k in ["starzbet", "link", "giriş", "adres", "site", "güncel"]):
        text = "🚀 <b>STARZBET GÜNCEL GİRİŞ</b>\n━━━━━━━━━━━━━━━━━━━━\n🔗 " + LINK_GIRIS
        kb = [[InlineKeyboardButton("🟠 GÜNCEL GİRİŞ ADRESİ", url=LINK_GIRIS)]]
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)

    elif any(k in msg for k in ["maç", "oran", "kupon", "bahis", "tahmin", "özel", "bülten"]):
        text = "🔥 <b>ÖZEL ORANLAR VE TAHMİNLER</b>\n━━━━━━━━━━━━━━━━━━━━\n👇 <b>Hemen Bahis Yap:</b>"
        kb = [[InlineKeyboardButton("📈 ÖZEL ORANLAR (SİTE)", url=LINK_OZEL_ORAN_SITE)], 
              [InlineKeyboardButton("📢 TAHMİN KANALI (TG)", url=LINK_OZEL_ORAN_KANAL)]]
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)

async def buton_tiklama(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    try: await query.answer() 
    except: return
    if query.data == 'btn_bonus':
        await query.edit_message_caption(caption="🎁 <b>Starzbet Bonus Menüsü</b>\n\nEn yüksek oranlar ve çevrimsiz bonuslar seni bekliyor!", 
                                         reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎁 BONUSLARI GÖR", url=LINK_BONUS)],
                                                                            [InlineKeyboardButton("⬅️ GERİ DÖN", callback_data='btn_back')]]), 
                                         parse_mode=ParseMode.HTML)
    elif query.data == 'btn_back':
        await query.delete_message()
        await start(update, context)

async def guncel_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🔗 <b>Güncel Giriş Adresimiz:</b>\n{LINK_GIRIS}", parse_mode=ParseMode.HTML)

async def canli_destek(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [[InlineKeyboardButton("🎧 CANLI DESTEĞE BAĞLAN", url=LINK_CANLI_DESTEK)]]
    await update.message.reply_text("🆘 <b>Destek Hattı</b>\nHer türlü sorun için yanındayız!", reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
  
    application = ApplicationBuilder().token(TOKEN).build()

    async def set_commands():
        commands = [
            BotCommand("start", "🔥 Macerayı Başlat"),
            BotCommand("mini_app", "🎰 Oyunları Aç"),
            BotCommand("guncel_link", "🔗 Güncel Adres"),
            BotCommand("canli_destek", "🆘 Yardım Al")
        ]
        await application.bot.set_my_commands(commands)

  
    saatler = [time(11,0), time(13,0), time(15,0), time(18,0), time(23,0)]
    for s in saatler:
        application.job_queue.run_daily(dm_promosyon_gonder, time=s.replace(tzinfo=TR_SAAT_DILIMI))

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("mini_app", start))
    application.add_handler(CommandHandler("guncel_link", guncel_link))
    application.add_handler(CommandHandler("canli_destek", canli_destek))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), kelime_takip))
    application.add_handler(CallbackQueryHandler(buton_tiklama))

    print("🚀 Starzbet VIP Full Otomasyon Aktif!")
    
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running(): asyncio.ensure_future(set_commands())
        else: loop.run_until_complete(set_commands())
    except: pass

    # 5. Botu Başlat
    application.run_polling()

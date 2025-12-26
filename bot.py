import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, BotCommand
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ==============================================================================
# ⚙️ AYARLAR VE LİNKLER (TÜM LİNKLERİN KORUNDU)
# ==============================================================================
TOKEN = "8031564377:AAHjJXBQ-b6f0BnKdbf6T7iwUjs1fCA7dW0"
RESIM_YOLU = "banner.jpg"

LINK_GIRIS            = "https://cutt.ly/drVOi2EN"
LINK_OZEL_ORAN_SITE   = "https://ozeloranlar.com/"
LINK_OZEL_ORAN_KANAL  = "https://t.me/Starzbetgir"
LINK_BONUS            = "https://starzbet422.com/tr-tr/info/promos"
LINK_CANLI_DESTEK     = "https://service.3kanumaigc.com/chatwindow.aspx?siteId=90005302&planId=1b050682-cde5-4176-8236-3bb94c891197#"
LINK_APP              = "https://starzmobil.com/indir/"
LINK_MINI_APP         = "https://telegram-mini-app-umber-chi.vercel.app" 
# ==============================================================================

# --- 🧠 AKILLI KELİME TAKİBİ (KORUNDU) ---
async def kelime_takip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    msg = update.message.text.lower()
    
    if any(k in msg for k in ["starzbet", "link", "giriş", "adres", "site", "güncel"]):
        text = "🚀 <b>STARZBET GÜNCEL GİRİŞ</b>\n━━━━━━━━━━━━━━━━━━━━\n🔗 " + LINK_GIRIS
        kb = [[InlineKeyboardButton("🟠 GÜNCEL GİRİŞ ADRESİ", url=LINK_GIRIS)]]
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)

    elif any(k in msg for k in ["maç", "oran", "kupon", "bahis", "tahmin", "özel", "bülten"]):
        text = "🔥 <b>ÖZEL ORANLAR VE TAHMİNLER</b>\n━━━━━━━━━━━━━━━━━━━━\n👇 <b>Hemen Bahis Yap:</b>"
        kb = [[InlineKeyboardButton("📈 ÖZEL ORANLAR (SİTE)", url=LINK_OZEL_ORAN_SITE)], 
              [InlineKeyboardButton("📢 TAHMİN KANALI (TG)", url=LINK_OZEL_ORAN_KANAL)]]
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)

    elif any(k in msg for k in ["bonus", "deneme", "750", "promosyon", "freespin", "yatırım", "para"]):
        text = "🎁 <b>BONUS ŞÖLENİ BAŞLADI</b>\n━━━━━━━━━━━━━━━━━━━━\nFırsatları kaçırma!"
        kb = [[InlineKeyboardButton("🎁 BONUSLARI İNCELE", url=LINK_BONUS)]]
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)

# --- BUTON TIKLAMA YÖNETİMİ ---
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

# --- START KOMUTU (GÖRSEL VE BUTONLAR) ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

# --- EKSTRA KOMUTLAR ---
async def guncel_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🔗 <b>Güncel Giriş Adresimiz:</b>\n{LINK_GIRIS}", parse_mode=ParseMode.HTML)

async def canli_destek(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [[InlineKeyboardButton("🎧 CANLI DESTEĞE BAĞLAN", url=LINK_CANLI_DESTEK)]]
    await update.message.reply_text("🆘 <b>Destek Hattı</b>\nHer türlü sorun için yanındayız kanka!", reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)

# --- ANA ÇALIŞTIRICI ---
if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
    
    application = ApplicationBuilder().token(TOKEN).build()

    # MENÜ KOMUTLARINI KAYDETME (KESİN ÇÖZÜM)
    async def set_commands():
        commands = [
            BotCommand("start", "🔥 Macerayı Başlat"),
            BotCommand("mini_app", "🎰 Oyunları Aç"),
            BotCommand("guncel_link", "🔗 Güncel Adres"),
            BotCommand("canli_destek", "🆘 Yardım Al")
        ]
        await application.bot.set_my_commands(commands)

    # Handler'lar
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("mini_app", start))
    application.add_handler(CommandHandler("guncel_link", guncel_link))
    application.add_handler(CommandHandler("canli_destek", canli_destek))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), kelime_takip))
    application.add_handler(CallbackQueryHandler(buton_tiklama))

    print("🚀 Starzbet Mini Turbo Aktif!")
    
    # Komutları asenkron olarak gönderelim
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.ensure_future(set_commands())
        else:
            loop.run_until_complete(set_commands())
    except:
        pass

    application.run_polling()

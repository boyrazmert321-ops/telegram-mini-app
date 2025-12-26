import os  # image_09f460.png hatasını çözen satır
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ==============================================================================
# ⚙️ AYARLAR VE LİNKLER
# ==============================================================================
TOKEN = "8031564377:AAHjJXBQ-b6f0BnKdbf6T7iwUjs1fCA7dW0"
RESIM_YOLU = "banner.jpg"

LINK_GIRIS         = "https://cutt.ly/drVOi2EN"
LINK_OZEL_ORAN_SITE = "https://ozeloranlar.com/"
LINK_OZEL_ORAN_KANAL= "https://t.me/Starzbetgir"
LINK_BONUS         = "https://starzbet421.com/tr-tr/info/promos?p=3N6z"
LINK_CANLI_DESTEK  = "https://service.3kanumaigc.com/chatwindow.aspx?siteId=90005302&planId=1b050682-cde5-4176-8236-3bb94c891197#"
LINK_APP           = "https://starzmobil.com/indir/"
# ==============================================================================

# --- 🧠 AKILLI KELİME TAKİBİ (GRUP VE DM) ---
async def kelime_takip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    msg = update.message.text.lower()
    
    # 1. Giriş / Link / Adres
    if any(k in msg for k in ["starzbet", "link", "giriş", "adres", "site", "güncel"]):
        text = "🚀 <b>STARZBET GÜNCEL GİRİŞ</b>\n━━━━━━━━━━━━━━━━━━━━\n🔗 " + LINK_GIRIS
        kb = [[InlineKeyboardButton("🟢 GÜNCEL GİRİŞ ADRESİ", url=LINK_GIRIS)]]
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)

    # 2. Bahis / Maç / Kupon / Oran
    elif any(k in msg for k in ["maç", "oran", "kupon", "bahis", "tahmin", "özel", "bülten"]):
        text = "🔥 <b>ÖZEL ORANLAR VE TAHMİNLER</b>\n━━━━━━━━━━━━━━━━━━━━\n👇 <b>Hemen Bahis Yap:</b>"
        kb = [[InlineKeyboardButton("📈 ÖZEL ORANLAR (SİTE)", url=LINK_OZEL_ORAN_SITE)], 
              [InlineKeyboardButton("📢 TAHMİN KANALI (TG)", url=LINK_OZEL_ORAN_KANAL)]]
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)

    # 3. Bonus / Deneme / Yatırım
    elif any(k in msg for k in ["bonus", "deneme", "750", "promosyon", "freespin", "yatırım", "para"]):
        text = "🎁 <b>BONUS ŞÖLENİ BAŞLADI</b>\n━━━━━━━━━━━━━━━━━━━━\nFırsatları kaçırma!"
        kb = [[InlineKeyboardButton("🎁 BONUSLARI İNCELE", url=LINK_BONUS)]]
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)

# --- BUTON TIKLAMA YÖNETİMİ ---
async def buton_tiklama(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    try: 
        await query.answer() # image_07b8d1.png hatasını önler
    except: 
        return

    if query.data == 'btn_bonus':
        await query.edit_message_caption(caption="🎁 <b>Bonus Menüsü</b>\n\nHemen talep et!", 
                                         reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎁 GÖR", url=LINK_BONUS)]]), 
                                         parse_mode=ParseMode.HTML)

# --- START KOMUTU ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "🏆 <b>STARZBET ELİTE ASİSTAN</b>\n━━━━━━━━━━━━━━━━━━━━\nHoş geldin! Bir işlem seç 👇"
    kb = [[InlineKeyboardButton("🟢 GÜNCEL GİRİŞ", url=LINK_GIRIS)],
          [InlineKeyboardButton("🎁 BONUSLAR", callback_data='btn_bonus'), InlineKeyboardButton("🎧 DESTEK", url=LINK_CANLI_DESTEK)],
          [InlineKeyboardButton("📱 MOBİL UYGULAMA", url=LINK_APP)]]
    
    # os.path.exists hatası import os ile çözüldü
    if os.path.exists(RESIM_YOLU):
        await update.message.reply_photo(photo=open(RESIM_YOLU, 'rb'), caption=text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
    
    # Hata veren JobQueue kısmını (pytz gerektiren) stabilite için kaldırdık
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), kelime_takip))
    app.add_handler(CallbackQueryHandler(buton_tiklama))
    
    print("🚀 Starzbet V13 Aktif! Çökme koruması devrede.")
    app.run_polling()

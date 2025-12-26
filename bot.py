import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ==============================================================================
# ⚙️ AYARLAR VE LİNKLER
# ==============================================================================
TOKEN = "8031564377:AAHjJXBQ-b6f0BnKdbf6T7iwUjs1fCA7dW0"
RESIM_YOLU = "banner.jpg"

LINK_GIRIS            = "https://cutt.ly/drVOi2EN"
LINK_OZEL_ORAN_SITE   = "https://ozeloranlar.com/"
LINK_OZEL_ORAN_KANAL  = "https://t.me/Starzbetgir"
LINK_BONUS            = "https://starzbet422.com/tr-tr/info/promos"
LINK_CANLI_DESTEK     = "https://service.3kanumaigc.com/chatwindow.aspx?siteId=90005302&planId=1b050682-cde5-4176-8236-3bb94c891197#"
LINK_APP              = "https://starzmobil.com/indir/"
# SENİN OYUN LİNKİN (Vercel)
LINK_MINI_APP         = "https://telegram-mini-app-umber-chi.vercel.app" 
# ==============================================================================

# --- 🧠 AKILLI KELİME TAKİBİ (DEĞİŞMEDİ) ---
async def kelime_takip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    msg = update.message.text.lower()
    
    if any(k in msg for k in ["starzbet", "link", "giriş", "adres", "site", "güncel"]):
        text = "🚀 <b>STARZBET GÜNCEL GİRİŞ</b>\n━━━━━━━━━━━━━━━━━━━━\n🔗 " + LINK_GIRIS
        kb = [[InlineKeyboardButton("🟢 GÜNCEL GİRİŞ ADRESİ", url=LINK_GIRIS)]]
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
    try: 
        await query.answer() 
    except: 
        return

    if query.data == 'btn_bonus':
        await query.edit_message_caption(caption="🎁 <b>Starzbet Bonus Menüsü</b>\n\nEn yüksek oranlar ve çevrimsiz bonuslar seni bekliyor!", 
                                         reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🎁 BONUSLARI GÖR", url=LINK_BONUS)],
                                                                            [InlineKeyboardButton("⬅️ GERİ DÖN", callback_data='btn_back')]]), 
                                         parse_mode=ParseMode.HTML)
    elif query.data == 'btn_back':
        # Geri dönme butonu için start menüsünü tekrar çağırıyoruz
        await query.delete_message()
        await start(update, context)

# --- START KOMUTU (GÜNCELLENDİ) ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Eğer callback_query'den geliyorsa (Geri butonu gibi)
    effective_message = update.message if update.message else update.callback_query.message
    
    text = (
        "🏆 <b>STARZBET KÜÇÜK DÜNYASINA HOŞ GELDİN!</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Eğlence ve kazancın adresi Starzbet'te,\n"
        "Mini oyunlarımızı oynayarak vakit geçirebilir,\n"
        "Güncel adresimize anında ulaşabilirsin. 👇"
    )
    
    kb = [
          # EN ÜSTE DEV OYUN BUTONU
          [InlineKeyboardButton("🎮 OYUNU BAŞLAT (PUAN KAZAN)", web_app=WebAppInfo(url=LINK_MINI_APP))],
          [InlineKeyboardButton("🟢 GÜNCEL GİRİŞ", url=LINK_GIRIS)],
          [InlineKeyboardButton("🎁 BONUSLAR", callback_data='btn_bonus'), InlineKeyboardButton("🎧 DESTEK", url=LINK_CANLI_DESTEK)],
          [InlineKeyboardButton("📱 MOBİL UYGULAMA", url=LINK_APP)]
         ]
    
    if os.path.exists(RESIM_YOLU):
        await effective_message.reply_photo(photo=open(RESIM_YOLU, 'rb'), caption=text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)
    else:
        await effective_message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.HTML)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
    
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), kelime_takip))
    app.add_handler(CallbackQueryHandler(buton_tiklama))
    
    print("🚀 Starzbet V14 Aktif! Mini App Entegrasyonu Tamamlandı.")
    app.run_polling()

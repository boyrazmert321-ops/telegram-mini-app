# bot.py - STARZBET BOT (ÇALIŞAN VERSİYON)
import os
import sys
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

print("=" * 50)
print("🤖 STARZBET BOT - RUNTIME.TXT İLE")
print("=" * 50)

# 1. TOKEN KONTROLÜ
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    print("❌ HATA: TELEGRAM_TOKEN yok!")
    print("✅ Render → Environment → TELEGRAM_TOKEN ekle")
    sys.exit(1)

print(f"✅ Token bulundu: {TOKEN[:15]}...")

# 2. MENÜ FONKSİYONU
def ana_menu():
    klavye = [
        [InlineKeyboardButton("🎰 STARZBET MİNİ APP", web_app=WebAppInfo(url="https://telegram-mini-app-umber-chi.vercel.app"))],
        [InlineKeyboardButton("💳 DİNAMİK PAY", callback_data="bonus"), 
         InlineKeyboardButton("🎰 SLOT %100", callback_data="bonus")],
        [InlineKeyboardButton("⚽ SPOR %100", callback_data="bonus"),
         InlineKeyboardButton("✨ %35 KAYIP", callback_data="bonus")],
        [InlineKeyboardButton("📱 MOBİL UYGULAMA", callback_data="mobile"),
         InlineKeyboardButton("🎧 CANLI DESTEK", url="https://service.3kanumaigc.com/chatwindow.aspx?siteId=90005302&planId=1b050682-cde5-4176-8236-3bb94c891197#")],
        [InlineKeyboardButton("🔗 GÜNCEL GİRİŞ", url="https://cutt.ly/drVOi2EN")]
    ]
    return InlineKeyboardMarkup(klavye)

# 3. /start KOMUTU
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌟 *Starzbet Asistanına Hoş Geldiniz!*\n\n"
        "Size nasıl yardımcı olabilirim?",
        reply_markup=ana_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

# 4. BUTON TIKLAMA
async def buton_tikla(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    mesaj = """🎁 *TÜM KAMPANYALAR:*

• 💳 Dinamik Pay: Yatırıma özel bonus
• 🎰 Slot %100: Slot oyunlarında %100 bonus
• ⚽ Spor %100: Spor bahislerinde %100 bonus
• ✨ %35 Kayıp: Kayıplarınızın %35'i iade

🔗 https://starzbet422.com/tr-tr/info/promos"""
    
    await query.edit_message_text(
        text=mesaj,
        reply_markup=ana_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

# 5. MESAJ CEVAP
async def mesaj_cevap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Sorularınız için lütfen butonları kullanın veya canlı desteğe başvurun.",
        reply_markup=ana_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

# 6. ANA PROGRAM
def main():
    # Log ayarı
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    
    print("🚀 Bot başlatılıyor...")
    
    try:
        # Bot oluştur
        app = Application.builder().token(TOKEN).build()
        
        # Handler'ları ekle
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(buton_tikla))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mesaj_cevap))
        
        print("✅ Bot hazır!")
        print("📱 Telegram'da botunuza /start yazın")
        
        # Botu başlat
        app.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES
        )
        
    except Exception as e:
        print(f"❌ HATA: {type(e).__name__}")
        print(f"📝 Detay: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

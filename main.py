import os
import sys
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

# --- DEBUG ---
print("=" * 60)
print("🚀 BOT BAŞLATILIYOR...")
print("=" * 60)

TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

print(f"✅ TELEGRAM_TOKEN: {'Var' if TOKEN else 'Yok'}")
print(f"✅ GROQ_API_KEY: {'Var' if GROQ_API_KEY else 'Yok'}")

if not TOKEN:
    print("❌ TELEGRAM_TOKEN bulunamadı!")
    sys.exit(1)

# --- MENÜ ---
def get_main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎰 STARZBET MİNİ APP", web_app=WebAppInfo(url="https://example.com"))],
        [InlineKeyboardButton("💳 DİNAMİK PAY", callback_data="bonus"),
         InlineKeyboardButton("🎰 SLOT %100", callback_data="bonus")],
        [InlineKeyboardButton("⚽ SPOR %100", callback_data="bonus"),
         InlineKeyboardButton("✨ %35 KAYIP", callback_data="bonus")],
        [InlineKeyboardButton("📱 MOBİL UYGULAMA", callback_data="mobile"),
         InlineKeyboardButton("🎧 CANLI DESTEK", url="https://example.com")],
        [InlineKeyboardButton("🔗 GÜNCEL GİRİŞ", url="https://example.com")]
    ])

# --- HANDLER'LAR ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Başlangıç komutu"""
    await update.message.reply_text(
        "🤖 *Starzbet'e Hoş Geldiniz!*\n\n"
        "Aşağıdaki menüden istediğinizi seçebilirsiniz.",
        reply_markup=get_main_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Buton tıklamaları"""
    query = update.callback_query
    await query.answer()
    
    response = "🎁 *Bonuslar ve kampanyalar için:*\nhttps://example.com/promos"
    
    await query.message.edit_text(
        response,
        reply_markup=get_main_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Normal mesajlar"""
    await update.message.reply_text(
        "ℹ️ Sorularınız için lütfen canlı desteği kullanın.",
        reply_markup=get_main_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

# --- ANA PROGRAM ---
def main():
    # Log ayarları
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    
    try:
        # Application oluştur - ESKİ YÖNTEM DEĞİL!
        application = Application.builder().token(TOKEN).build()
        
        # Handler'ları ekle
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CallbackQueryHandler(button_handler))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        print("✅ Bot başarıyla oluşturuldu!")
        print("⏳ Polling başlatılıyor...")
        
        # Botu başlat
        application.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES
        )
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        logging.error(f"Bot başlatma hatası: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()

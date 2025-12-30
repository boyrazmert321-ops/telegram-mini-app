import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
from groq import Groq

# --- AYARLAR ---
# Ortam değişkenlerini al
TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# Debug mesajı
print("=" * 50)
print(f"TELEGRAM_TOKEN var mı: {'EVET' if TOKEN else 'HAYIR'}")
print(f"TOKEN ilk 10 karakter: {TOKEN[:10] if TOKEN else 'YOK'}")
print(f"GROQ_API_KEY var mı: {'EVET' if GROQ_API_KEY else 'HAYIR'}")
print("=" * 50)

# Token kontrolü
if not TOKEN:
    print("❌ KRİTİK HATA: TELEGRAM_TOKEN ortam değişkeni ayarlanmamış!")
    print("✅ Çözüm: Render Dashboard → Environment → Add Environment Variable")
    print("✅ Key: TELEGRAM_TOKEN")
    print(f"✅ Value: BotFather'dan aldığın token")
    exit(1)

# Groq client başlatma
client = None
if GROQ_API_KEY:
    try:
        client = Groq(api_key=GROQ_API_KEY)
        print("✅ Groq API başarıyla bağlandı")
    except Exception as e:
        print(f"⚠️ Groq API bağlantı hatası: {e}")
        client = None
else:
    print("⚠️ UYARI: GROQ_API_KEY yok, AI özelliği devre dışı")

# --- MENÜ ---
def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("🎰 STARZBET MİNİ APP", web_app=WebAppInfo(url="https://telegram-mini-app-umber-chi.vercel.app"))],
        [InlineKeyboardButton("💳 DİNAMİK PAY", callback_data="bonus"),
         InlineKeyboardButton("🎰 SLOT %100", callback_data="bonus")],
        [InlineKeyboardButton("⚽ SPOR %100", callback_data="bonus"),
         InlineKeyboardButton("✨ %35 KAYIP", callback_data="bonus")],
        [InlineKeyboardButton("📱 MOBİL UYGULAMA", callback_data="mobile"),
         InlineKeyboardButton("🎧 CANLI DESTEK", url="https://service.3kanumaigc.com/chatwindow.aspx?siteId=90005302&planId=1b050682-cde5-4176-8236-3bb94c891197#")],
        [InlineKeyboardButton("🔗 GÜNCEL GİRİŞ", url="https://cutt.ly/drVOi2EN")]
    ]
    return InlineKeyboardMarkup(keyboard)

# --- HANDLER'LAR ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *Starzbet Asistanına Hoş Geldiniz!*\n\n"
        "Size nasıl yardımcı olabilirim?\n"
        "Aşağıdaki butonları kullanabilir veya bana soru sorabilirsiniz!",
        reply_markup=get_main_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    
    # AI kapalıysa
    if not client:
        await update.message.reply_text(
            "ℹ️ *Yapay zeka şu anda kullanılamıyor.*\n\n"
            "Lütfen butonları kullanın veya canlı destek ile iletişime geçin.",
            reply_markup=get_main_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # "Düşünüyorum" mesajı
    thinking_msg = await update.message.reply_text("⏳ *Cevap hazırlanıyor...*", parse_mode=ParseMode.MARKDOWN)
    
    try:
        # Groq'dan cevap al
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "Sen Starzbet'in resmi asistanısın. Bahis, casino, bonuslar hakkında yardımcı ol. Kısa ve net cevaplar ver."
                },
                {"role": "user", "content": user_message}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        # Mesajı sil
        await thinking_msg.delete()
        
        # Cevabı gönder
        response = completion.choices[0].message.content
        await update.message.reply_text(
            f"🤖 *Asistan:*\n{response}",
            reply_markup=get_main_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
        
    except Exception as e:
        logging.error(f"AI hatası: {e}")
        await thinking_msg.delete()
        await update.message.reply_text(
            "❌ *Üzgünüm, bir hata oluştu.*\n\n"
            "Lütfen daha sonra tekrar deneyin veya canlı destek butonunu kullanın.",
            reply_markup=get_main_menu(),
            parse_mode=ParseMode.MARKDOWN
        )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "bonus":
        text = "🎁 *BONUS KAMPANYALARI*\n\n• İlk yatırım %100 bonus\n• Slot oyunları %100 bonus\n• Spor bahisleri %100 bonus\n• Kayıplarınıza %35 iade\n\nDetaylar: https://starzbet422.com/tr-tr/info/promos"
    elif data == "mobile":
        text = "📱 *MOBİL UYGULAMA*\n\nMobil uygulamamız yakında yayında olacak!"
    else:
        text = "Lütfen bir seçenek belirleyin."
    
    await query.message.edit_text(
        text,
        reply_markup=get_main_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

# --- ANA PROGRAM ---
def main():
    # Log ayarı
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    
    print("🚀 Bot başlatılıyor...")
    
    # Application oluştur
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Handler'ları ekle
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ Bot aktif! /start komutunu bekliyor...")
    
    # Polling başlat
    app.run_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES
    )

if __name__ == "__main__":
    main()

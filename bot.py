import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
from groq import Groq

# 1. ÖNCE TOKEN KONTROLÜ
TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

print("=" * 50)
print("🤖 STARZBET BOT - YENİ KURULUM")
print("=" * 50)
print(f"Token: {'✅ VAR' if TOKEN else '❌ YOK'}")
print(f"Groq Key: {'✅ VAR' if GROQ_API_KEY else '❌ YOK'}")

if not TOKEN:
    print("HATA: TELEGRAM_TOKEN yok!")
    exit(1)

# 2. GROQ CLIENT (AI için)
client = None
if GROQ_API_KEY:
    try:
        client = Groq(api_key=GROQ_API_KEY)
        print("✅ Groq bağlantısı başarılı")
    except:
        print("⚠️ Groq bağlantı hatası")
        client = None

# 3. MENÜ
def get_menu():
    keyboard = [
        [InlineKeyboardButton("🎰 MİNİ APP", web_app=WebAppInfo(url="https://telegram-mini-app-umber-chi.vercel.app"))],
        [InlineKeyboardButton("💳 DİNAMİK PAY", callback_data="bonus")],
        [InlineKeyboardButton("🎰 SLOT %100", callback_data="bonus")],
        [InlineKeyboardButton("⚽ SPOR %100", callback_data="bonus")],
        [InlineKeyboardButton("✨ %35 KAYIP", callback_data="bonus")],
        [InlineKeyboardButton("📱 MOBİL UYGULAMA", callback_data="mobile")],
        [InlineKeyboardButton("🎧 CANLI DESTEK", url="https://service.3kanumaigc.com/chatwindow.aspx?siteId=90005302&planId=1b050682-cde5-4176-8236-3bb94c891197#")],
        [InlineKeyboardButton("🔗 GÜNCEL GİRİŞ", url="https://cutt.ly/drVOi2EN")]
    ]
    return InlineKeyboardMarkup(keyboard)

# 4. /start KOMUTU
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌟 *Starzbet Asistanına Hoş Geldiniz!*\n\n"
        "Size nasıl yardımcı olabilirim?",
        reply_markup=get_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

# 5. BUTON TIKLAMA
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "bonus":
        text = "🎁 *BONUS KAMPANYALARI*\n\n• İlk yatırım %100 bonus\n• Slot %100 bonus\n• Spor %100 bonus\n• %35 kayıp iadesi\n\n🔗 https://starzbet422.com/tr-tr/info/promos"
    elif query.data == "mobile":
        text = "📱 *MOBİL UYGULAMA*\n\nYakında App Store ve Google Play'de!"
    else:
        text = "Lütfen bir seçenek belirleyin."
    
    await query.edit_message_text(
        text=text,
        reply_markup=get_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

# 6. AI MESAJ İŞLEME
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    
    # Eğer AI aktif değilse
    if not client:
        await update.message.reply_text(
            "🤖 *AI Asistan şu anda kullanılamıyor.*\n\n"
            "Lütfen butonları kullanın veya canlı desteğe başvurun.",
            reply_markup=get_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # "Düşünüyorum" mesajı
    thinking = await update.message.reply_text("🤔 *Düşünüyorum...*", parse_mode=ParseMode.MARKDOWN)
    
    try:
        # Groq AI'ya sor
        completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system", 
                    "content": "Sen Starzbet bahis sitesinin resmi asistanısın. Kullanıcılara bahis, casino, bonuslar, ödemeler konusunda yardım et. Kısa ve net cevaplar ver. Emin değilsen canlı desteğe yönlendir."
                },
                {"role": "user", "content": user_message}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=300
        )
        
        # Düşünüyorum mesajını sil
        await thinking.delete()
        
        # AI cevabını gönder
        ai_response = completion.choices[0].message.content
        await update.message.reply_text(
            f"🤖 *Asistan:*\n{ai_response}",
            reply_markup=get_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
        
    except Exception as e:
        logging.error(f"AI hatası: {e}")
        await thinking.delete()
        await update.message.reply_text(
            "❌ *Üzgünüm, bir hata oluştu.*\n\n"
            "Lütfen daha sonra tekrar deneyin.",
            reply_markup=get_menu(),
            parse_mode=ParseMode.MARKDOWN
        )

# 7. ANA PROGRAM
def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    
    print("🚀 Bot başlatılıyor...")
    
    try:
        # Application oluştur (YENİ YÖNTEM)
        app = Application.builder().token(TOKEN).build()
        
        # Handler'ları ekle
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(button_click))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        print("✅ Bot başarıyla kuruldu!")
        print("📱 Telegram'da /start yaz")
        
        # Başlat
        app.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        exit(1)

if __name__ == "__main__":
    main()

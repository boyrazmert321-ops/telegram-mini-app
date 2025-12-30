import os
import sys
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

print("=" * 60)
print("🤖 STARZBET BOT + AI - RAILWAY")
print("=" * 60)

# 1. TOKEN ve API KEY'ler
TOKEN = os.environ.get("TELEGRAM_TOKEN", "8031564377:AAHjJXBQ-b6f0BnKdbf6T7iwUjs1fCA7dW0")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")

print(f"🔑 Telegram Token: {'✅' if TOKEN else '❌'}")
print(f"🧠 Groq API Key: {'✅' if GROQ_API_KEY else '❌'}")

if not TOKEN:
    print("❌ HATA: TELEGRAM_TOKEN yok!")
    print("✅ Railway → Settings → Variables → TELEGRAM_TOKEN ekle")
    sys.exit(1)

# 2. AI Client (Groq)
client = None
if GROQ_API_KEY:
    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        print("✅ Groq AI bağlantısı başarılı")
    except Exception as e:
        print(f"⚠️ Groq hatası: {e}")
        client = None
else:
    print("⚠️ GROQ_API_KEY yok, AI devre dışı")

# 3. MENÜ
def ana_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎰 STARZBET MİNİ APP", web_app=WebAppInfo(url="https://telegram-mini-app-umber-chi.vercel.app"))],
        [InlineKeyboardButton("💳 DİNAMİK PAY", callback_data="bonus"), 
         InlineKeyboardButton("🎰 SLOT %100", callback_data="bonus")],
        [InlineKeyboardButton("⚽ SPOR %100", callback_data="bonus"),
         InlineKeyboardButton("✨ %35 KAYIP", callback_data="bonus")],
        [InlineKeyboardButton("📱 MOBİL UYGULAMA", callback_data="mobile"),
         InlineKeyboardButton("🎧 CANLI DESTEK", url="https://service.3kanumaigc.com/chatwindow.aspx?siteId=90005302&planId=1b050682-cde5-4176-8236-3bb94c891197#")],
        [InlineKeyboardButton("🔗 GÜNCEL GİRİŞ", url="https://cutt.ly/drVOi2EN")]
    ])

# 4. /start KOMUTU
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ai_status = "✅ Aktif" if client else "❌ Devre Dışı"
    
    await update.message.reply_text(
        f"🌟 *Starzbet AI Asistanına Hoş Geldiniz!*\n\n"
        f"🤖 *AI Durumu:* {ai_status}\n\n"
        "Bana soru sorabilir veya aşağıdaki butonları kullanabilirsiniz!",
        reply_markup=ana_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

# 5. BUTON TIKLAMA
async def buton_tikla(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "bonus":
        text = """🎁 *BONUS KAMPANYALARI:*

• 💳 **Dinamik Pay:** İlk yatırımınıza %100 bonus
• 🎰 **Slot %100:** Slot oyunlarında %100 bonus  
• ⚽ **Spor %100:** Spor bahislerinde %100 bonus
• ✨ **%35 Kayıp İadesi:** Kayıplarınızın %35'i iade

🔗 *Detaylar:* https://starzbet422.com/tr-tr/info/promos"""
    
    elif query.data == "mobile":
        text = "📱 *MOBİL UYGULAMA*\n\niOS ve Android uygulamamız yakında yayında!"
    
    else:
        text = "Lütfen bir seçenek belirleyin."
    
    await query.edit_message_text(
        text=text,
        reply_markup=ana_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

# 6. AI MESAJ İŞLEME
async def ai_cevap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    
    # AI aktif değilse
    if not client:
        await update.message.reply_text(
            "🤖 *AI şu anda kullanılamıyor.*\n\n"
            "Lütfen butonları kullanın veya canlı desteğe başvurun.",
            reply_markup=ana_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # "Düşünüyorum" mesajı
    thinking_msg = await update.message.reply_text(
        "⏳ *Cevap hazırlanıyor...*",
        parse_mode=ParseMode.MARKDOWN
    )
    
    try:
        # Groq AI'ya sor
        completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": """Sen Starzbet'in resmi AI asistanısın. 
                    Kullanıcılara bahis, casino, spor bahisleri, bonuslar, ödemeler, 
                    para yatırma/çekme işlemleri hakkında yardımcı ol.
                    
                    KURALLAR:
                    1. Sadece Starzbet ile ilgili konularda yardım et
                    2. Yasaklı konularda (kumar yaşı, yasal sorunlar) "Bu konuda yardımcı olamam" de
                    3. Kısa, net ve profesyonel cevaplar ver
                    4. Emin değilsen canlı desteğe yönlendir
                    5. Dostane ve yardımsever bir dil kullan
                    
                    Starzbet bilgileri:
                    • Site: starzbet422.com
                    • Bonuslar: starzbet422.com/tr-tr/info/promos
                    • Destek: Canlı destek butonu"""
                },
                {
                    "role": "user", 
                    "content": user_message
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=500
        )
        
        # "Düşünüyorum" mesajını sil
        await thinking_msg.delete()
        
        # AI cevabını gönder
        ai_response = completion.choices[0].message.content
        
        await update.message.reply_text(
            f"🤖 *Starzbet AI Asistanı:*\n\n{ai_response}",
            reply_markup=ana_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
        
    except Exception as e:
        logging.error(f"AI hatası: {e}")
        
        # "Düşünüyorum" mesajını sil
        try:
            await thinking_msg.delete()
        except:
            pass
        
        await update.message.reply_text(
            "❌ *Üzgünüm, bir hata oluştu.*\n\n"
            "Lütfen daha sonra tekrar deneyin veya canlı desteği kullanın.",
            reply_markup=ana_menu(),
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
        # Bot oluştur
        app = Application.builder().token(TOKEN).build()
        
        # Handler ekle
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(buton_tikla))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_cevap))
        
        print("✅ Bot hazır!")
        print("🧠 AI Durumu:", "Aktif" if client else "Devre Dışı")
        print("📱 Telegram'da /start yaz")
        
        # Botu başlat
        app.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        print(f"❌ Hata: {type(e).__name__}")
        print(f"📝 Detay: {str(e)[:200]}")
        sys.exit(1)

if __name__ == "__main__":
    main()

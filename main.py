import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
from groq import Groq
import asyncio

# --- AYARLAR (Render'da Environment Variables olarak ekleyeceksin) ---
TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

# Groq client'ı oluştur
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# --- MENÜ ---
def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("🎰 STARZBET MİNİ APP", web_app=WebAppInfo(url="https://telegram-mini-app-umber-chi.vercel.app"))],
        [InlineKeyboardButton("💳 DİNAMİK PAY", callback_data="bonus_info"),
         InlineKeyboardButton("🎰 SLOT %100", callback_data="bonus_info")],
        [InlineKeyboardButton("⚽ SPOR %100", callback_data="bonus_info"),
         InlineKeyboardButton("✨ %35 KAYIP", callback_data="bonus_info")],
        [InlineKeyboardButton("📱 MOBİL UYGULAMA", callback_data="mobile_info"),
         InlineKeyboardButton("🎧 CANLI DESTEK", url="https://service.3kanumaigc.com/chatwindow.aspx?siteId=90005302&planId=1b050682-cde5-4176-8236-3bb94c891197#")],
        [InlineKeyboardButton("🔗 GÜNCEL GİRİŞ", url="https://cutt.ly/drVOi2EN")]
    ]
    return InlineKeyboardMarkup(keyboard)

# --- HANDLER'LAR ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start komutu"""
    welcome_text = """
<b>🌟 Starzbet'e Hoş Geldiniz!</b>

En iyi bahis deneyimi için buradayız.
Aşağıdaki butonlardan istediğiniz seçeneği seçebilir
veya bana soru sorabilirsiniz!
"""
    await update.message.reply_text(
        welcome_text,
        reply_markup=get_main_menu(),
        parse_mode=ParseMode.HTML
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kullanıcı mesajlarını işle"""
    user_message = update.message.text
    
    # Eğer Groq API anahtarı yoksa
    if not client:
        await update.message.reply_text(
            "⚠️ AI servisi şu anda kullanılamıyor. Lütfen butonları kullanın.",
            reply_markup=get_main_menu()
        )
        return
    
    # Kullanıcıya "düşünüyorum" mesajı göster
    thinking_msg = await update.message.reply_text("🤔 Düşünüyorum...")
    
    try:
        # Groq API'ye sorgu gönder
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": """Sen Starzbet'in resmi yardım asistanısın. 
                    Kullanıcılara bahis, casino, bonuslar, ödemeler ve genel soruları hakkında yardımcı ol.
                    Cevapların kısa, net ve yardımsever olsun.
                    Eğer bir konuda emin değilsen, canlı desteğe yönlendir."""
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        # Düşünüyorum mesajını sil
        await thinking_msg.delete()
        
        # AI cevabını gönder
        ai_response = completion.choices[0].message.content
        await update.message.reply_text(
            ai_response,
            reply_markup=get_main_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
        
    except Exception as e:
        logging.error(f"AI Hatası: {e}")
        # Düşünüyorum mesajını sil
        await thinking_msg.delete()
        
        await update.message.reply_text(
            "❌ Üzgünüm, bir hata oluştu. Lütfen daha sonra tekrar deneyin veya canlı destek butonunu kullanın.",
            reply_markup=get_main_menu()
        )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Buton tıklamalarını işle"""
    query = update.callback_query
    await query.answer()
    
    button_data = query.data
    
    if button_data == "bonus_info":
        response = """
🎁 <b>BONUS KAMPANYALARI</b>

• <b>Hoş Geldin Bonusu:</b> İlk yatırımınıza %100 bonus
• <b>Slot Bonusu:</b> Slot oyunlarında %100 bonus
• <b>Spor Bonusu:</b> Spor bahislerinde %100 bonus
• <b>Kayıp Bonusu:</b> Kayıplarınızın %35'i iade

Detaylar için: https://starzbet422.com/tr-tr/info/promos
"""
    elif button_data == "mobile_info":
        response = "📱 <b>MOBİL UYGULAMA</b>\n\nAndroid ve iOS için mobil uygulamamız yakında yayında!"
    else:
        response = "Lütfen aşağıdaki menüden bir seçenek belirleyin:"
    
    await query.message.edit_text(
        response,
        reply_markup=get_main_menu(),
        parse_mode=ParseMode.HTML
    )

# --- ANA FONKSİYON ---
def main():
    """Botu başlat"""
    # Log ayarı
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    
    # Token kontrolü
    if not TOKEN:
        logging.error("TELEGRAM_TOKEN ortam değişkeni ayarlanmamış!")
        return
    
    # Uygulamayı oluştur
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Handler'ları ekle
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🤖 Bot başlatılıyor...")
    
    # Botu başlat
    application.run_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES
    )

if __name__ == "__main__":
    main()

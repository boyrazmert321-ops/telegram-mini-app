import os
import logging
import asyncio
import threading
import http.server
import socketserver
from groq import Groq
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# --- 1. GÜVENLİ AYARLAR ---
# Önce .env dosyasından veya ortam değişkenlerinden yükle
load_dotenv()

TOKEN = os.environ.get("TELEGRAM_TOKEN")  # Render'da env variable olarak ekle
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")  # Render'da env variable olarak ekle

if not TOKEN or not GROQ_API_KEY:
    raise ValueError("TELEGRAM_TOKEN veya GROQ_API_KEY ortam değişkeni ayarlanmamış!")

client = Groq(api_key=GROQ_API_KEY)

# LİNKLER
LINK_GIRIS = "https://cutt.ly/drVOi2EN"
LINK_BONUSLAR = "https://starzbet422.com/tr-tr/info/promos"
LINK_CANLI_DESTEK = "https://service.3kanumaigc.com/chatwindow.aspx?siteId=90005302&planId=1b050682-cde5-4176-8236-3bb94c891197#"
LINK_MINI_APP = "https://telegram-mini-app-umber-chi.vercel.app"

# --- 2. FONKSİYONLAR ---
def ana_menu_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎰 STARZBET MİNİ APP", web_app=WebAppInfo(url=LINK_MINI_APP))],
        [InlineKeyboardButton("💳 DİNAMİK PAY", callback_data="btn_info"), InlineKeyboardButton("🎰 SLOT %100", callback_data="btn_info")],
        [InlineKeyboardButton("⚽ SPOR %100", callback_data="btn_info"), InlineKeyboardButton("✨ %35 KAYIP", callback_data="btn_info")],
        [InlineKeyboardButton("📱 MOBİL UYGULAMA", callback_data="btn_info"), InlineKeyboardButton("🎧 DESTEK", url=LINK_CANLI_DESTEK)],
        [InlineKeyboardButton("🔗 GÜNCEL GİRİŞ ADRESİ", url=LINK_GIRIS)]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "<b>Starzbet Asistanına Hoş Geldiniz.</b>\nSize nasıl yardımcı olabilirim?",
        reply_markup=ana_menu_kb(),
        parse_mode=ParseMode.HTML
    )

async def ai_asistan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    
    user_message = update.message.text.strip()
    
    # Kısa mesajları kontrol et
    if len(user_message) < 3:
        await update.message.reply_text("Lütfen daha detaylı bir soru sorun.", reply_markup=ana_menu_kb())
        return
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Sen Starzbet resmi asistanısın. Bahis, casino, spor bahisleri, bonuslar ve ödemeler hakkında yardımcı ol. Profesyonel ve dostane bir dil kullan."},
                {"role": "user", "content": user_message}
            ],
            model="llama-3.3-70b-versatile",
            max_tokens=500,
            temperature=0.7
        )
        
        ai_response = chat_completion.choices[0].message.content
        await update.message.reply_text(ai_response, reply_markup=ana_menu_kb())
        
    except Exception as e:
        logging.error(f"AI Hatası: {e}")
        await update.message.reply_text(
            "Şu anda teknik bir sorun yaşıyoruz. Lütfen daha sonra tekrar deneyin veya canlı desteğe başvurun.",
            reply_markup=ana_menu_kb()
        )

async def buton_tiklama(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Buton türüne göre özel mesajlar
    if query.data == "btn_info":
        await query.message.reply_text(
            "🎁 **Tüm kampanyalarımız ve güncel bonuslar için:**\n\n"
            f"🌐 {LINK_BONUSLAR}\n\n"
            "Detaylı bilgi almak için lütfen sitemizi ziyaret edin.",
            reply_markup=ana_menu_kb(),
            parse_mode=ParseMode.MARKDOWN
        )

# --- 3. RENDER İÇİN PORT VE BAŞLATICI ---
def run_server():
    """Render için basit HTTP sunucusu"""
    port = int(os.environ.get("PORT", 8080))
    handler = http.server.SimpleHTTPRequestHandler
    
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"🚀 HTTP Sunucusu {port} portunda başlatıldı")
        httpd.serve_forever()

if __name__ == '__main__':
    # Log ayarları
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    
    # Render için HTTP sunucusu (opsiyonel)
    threading.Thread(target=run_server, daemon=True).start()
    
    # Bot başlatma
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Handler'ları ekle
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buton_tiklama))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_asistan))
    
    print("🤖 Starzbet Botu Aktif!")
    
    # Botu başlat
    app.run_polling(
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES
    )

import os
import sys
import logging
import random
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

print("=" * 80)
print("🚀 STARZBET ULTRA BOT - SORUNSUZ VERSİYON")
print("=" * 80)

# TOKEN ve API KEY'ler
TOKEN = os.environ.get("TELEGRAM_TOKEN", "8031564377:AAHjJXBQ-b6f0BnKdbf6T7iwUjs1fCA7dW0")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")

# AI CLIENT
client = None
if GROQ_API_KEY:
    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        print("✅ Groq AI bağlantısı başarılı")
    except:
        print("⚠️ Groq bağlantı hatası")
        client = None

# GÜNCEL VERİLER
GUNCEL_VERILER = {
    "site_baslik": "Starzbet - En Güvenilir Bahis Sitesi",
    "bonuslar": [
        "🎁 HOŞGELDİN BONUSU: İlk yatırımınıza %100 bonus (max 5.000₺)",
        "🎰 SLOT BONUSU: Slot oyunlarında %100 bonus",
        "⚽ SPOR BONUSU: Spor bahislerinde %100 bonus",
        "✨ KAYIP İADESİ: Kayıplarınızın %35'i iade",
        "🔥 TEKRAR YATIRIM: Her yatırımda %25 ekstra bonus"
    ],
    "son_guncelleme": datetime.now().strftime("%d.%m.%Y %H:%M")
}

# LİNKLER
LINKLER = {
    "dinamikpay": "https://cutt.ly/dynamicpay-starzbet",
    "giris": "https://cutt.ly/drVOi2EN",
    "bonus": "https://starzbet422.com/tr-tr/info/promos",
    "telegram_kanal": "https://t.me/Starzbetgir",
    "canli_destek": "https://service.3kanumaigc.com/chatwindow.aspx?siteId=90005302&planId=1b050682-cde5-4176-8236-3bb94c891197#",
    "mini_app": "https://telegram-mini-app-umber-chi.vercel.app",
    "casino": "https://starzbet422.com/casino",
    "spor": "https://starzbet422.com/sports",
    "mobile_apk": "https://starzbet422.com/apk"
}

# MENÜLER
def ana_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⚡ DİNAMİKPAY YATIR", callback_data="dinamikpay_yatir")],
        [InlineKeyboardButton("💰 GÜNCEL BONUSLAR", callback_data="guncel_bonuslar")],
        [InlineKeyboardButton("🎮 CASİNO", callback_data="casino"),
         InlineKeyboardButton("⚽ SPOR BAHİS", callback_data="spor_bahis")],
        [InlineKeyboardButton("📱 MOBİL UYGULAMA", callback_data="mobile"),
         InlineKeyboardButton("🎰 MİNİ APP", web_app=WebAppInfo(url=LINKLER["mini_app"]))],
        [InlineKeyboardButton("🎧 CANLI DESTEK", url=LINKLER["canli_destek"]),
         InlineKeyboardButton("🔗 GÜNCEL GİRİŞ", url=LINKLER["giris"])]
    ])

# /start KOMUTU
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ai_status = "✅ Aktif" if client else "❌ Devre Dışı"
    
    mesaj = f"""🌟 *Starzbet'e Hoş Geldiniz!* 🌟

🤖 *AI Asistan:* {ai_status}
🕒 *Son Güncelleme:* {GUNCEL_VERILER['son_guncelleme']}

⚡ *DİNAMİKPAY AVANTAJLARI:*
• %150 İlk Yatırım Bonusu
• Sıfır Komisyon
• Anında Hesaba Geçiş

🎯 *Hemen Başlayın:*
1. DİNAMİKPAY ile yatırım yap
2. %150 bonusunuzu alın
3. Bahis/Casino'da kazanmaya başlayın

🔗 *Özel Link:* {LINKLER['dinamikpay']}"""
    
    await update.message.reply_text(
        mesaj,
        reply_markup=ana_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

# GÜNCEL BONUSLAR
async def guncel_bonuslar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    bonus_mesaji = "🎁 *GÜNCEL BONUSLAR* 🎁\n\n"
    for bonus in GUNCEL_VERILER["bonuslar"]:
        bonus_mesaji += f"• {bonus}\n"
    
    bonus_mesaji += f"\n🔗 Tüm bonuslar: {LINKLER['bonus']}"
    
    await query.message.reply_text(
        bonus_mesaji,
        reply_markup=ana_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

# DİNAMİKPAY
async def dinamikpay_yatir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    mesaj = f"""⚡ *DİNAMİKPAY SİSTEMİ* ⚡

💰 *ÖDEME YÖNTEMLERİ:*
• Papara: %0 komisyon, Anında
• Jeton: %0 komisyon, Anında
• Cepbank: %0 komisyon, Anında
• Kredi Kartı: %0 komisyon, 2-5 dk
• Bitcoin: %0 komisyon, 10-30 dk

🎁 *AVANTAJLAR:*
• %150 İlk Yatırım Bonusu
• Sıfır Komisyon
• Anında Onay
• 7/24 Aktif

🔗 *Hemen Yatırım Yap:* {LINKLER['dinamikpay']}"""
    
    await query.message.reply_text(
        mesaj,
        reply_markup=ana_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

# SPOR BAHİS
async def spor_bahis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    mesaj = f"""⚽ *SPOR BAHİSLERİ* ⚽

🎯 *BAHİS TİPLERİ:*
• Maç sonucu
• Canlı bahis
• Toplam gol
• Handikap

💰 *BAHİS YAPMAK İÇİN:*
1. Önce DİNAMİKPAY ile yatırım yap
2. Bonusunuzu alın
3. Bahis yapmaya başlayın

📊 *Güncel oranlar:* {LINKLER['telegram_kanal']}
🔗 *Bahis yap:* {LINKLER['spor']}"""
    
    await query.message.reply_text(
        mesaj,
        reply_markup=ana_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

# CASİNO
async def casino(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    mesaj = f"""🎮 *CANLI CASİNO* 🎮

✨ *OYUNLAR:*
• Canlı Blackjack
• Rulet
• Slot Makineleri
• Baccarat
• Poker

🎁 *CASİNO BONUSU:* %200
🔗 *Casino'ya git:* {LINKLER['casino']}"""
    
    await query.message.reply_text(
        mesaj,
        reply_markup=ana_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

# MOBİL
async def mobile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    mesaj = f"""📱 *MOBİL UYGULAMA* 📱

📲 *İNDİRME LİNKLERİ:*
• Android APK: {LINKLER['mobile_apk']}
• iOS: Yakında App Store'da

🌟 *MOBİL AVANTAJLAR:*
• %25 ekstra bonus
• Canlı bildirimler
• DİNAMİKPAY entegrasyonu"""
    
    await query.message.reply_text(
        mesaj,
        reply_markup=ana_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

# AI CEVAP
async def ai_cevap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.lower()
    
    if "bonus" in user_message:
        await guncel_bonuslar_ai(update)
    elif "yatırım" in user_message or "para yatır" in user_message:
        await yatirim_ai(update)
    elif "bahis" in user_message:
        await bahis_ai(update)
    elif "casino" in user_message:
        await casino_ai(update)
    elif any(k in user_message for k in ["merhaba", "selam", "hi"]):
        await selam_ai(update)
    elif any(k in user_message for k in ["giriş", "link"]):
        await link_ai(update)
    else:
        await genel_ai_cevap(update, user_message)

async def guncel_bonuslar_ai(update: Update):
    await update.message.reply_text(
        f"🎁 *BONUSLAR:*\n\n{GUNCEL_VERILER['bonuslar'][0]}\n{LINKLER['bonus']}",
        parse_mode=ParseMode.MARKDOWN
    )

async def yatirim_ai(update: Update):
    await update.message.reply_text(
        f"⚡ *DİNAMİKPAY İLE YATIRIM:*\n\n{LINKLER['dinamikpay']}",
        parse_mode=ParseMode.MARKDOWN
    )

async def bahis_ai(update: Update):
    await update.message.reply_text(
        f"⚽ *BAHİS:*\n\n{LINKLER['spor']}\n📊 Oranlar: {LINKLER['telegram_kanal']}",
        parse_mode=ParseMode.MARKDOWN
    )

async def casino_ai(update: Update):
    await update.message.reply_text(
        f"🎮 *CASİNO:*\n\n{LINKLER['casino']}",
        parse_mode=ParseMode.MARKDOWN
    )

async def selam_ai(update: Update):
    await update.message.reply_text(
        "🌟 *Merhaba!* Starzbet'e hoş geldiniz! 🎰",
        parse_mode=ParseMode.MARKDOWN
    )

async def link_ai(update: Update):
    await update.message.reply_text(
        f"🔗 *LİNKLER:*\n\n• Giriş: {LINKLER['giris']}\n• DİNAMİKPAY: {LINKLER['dinamikpay']}",
        parse_mode=ParseMode.MARKDOWN
    )

async def genel_ai_cevap(update: Update, user_message):
    if not client:
        await update.message.reply_text(
            "🤖 AI şu anda kullanılamıyor. Lütfen butonları kullanın.",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    try:
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Sen Starzbet asistanısın. Kısa cevaplar ver."},
                {"role": "user", "content": user_message}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=200
        )
        
        ai_response = completion.choices[0].message.content
        await update.message.reply_text(
            f"🤖 *Starzbet AI:*\n\n{ai_response}",
            parse_mode=ParseMode.MARKDOWN
        )
    except:
        await update.message.reply_text(
            "❌ AI yanıt hatası. Lütfen butonları kullanın.",
            parse_mode=ParseMode.MARKDOWN
        )

# BUTON HANDLER
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "guncel_bonuslar":
        await guncel_bonuslar(update, context)
    elif data == "dinamikpay_yatir":
        await dinamikpay_yatir(update, context)
    elif data == "spor_bahis":
        await spor_bahis(update, context)
    elif data == "casino":
        await casino(update, context)
    elif data == "mobile":
        await mobile(update, context)

# ANA PROGRAM
def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    
    print("🚀 Bot başlatılıyor...")
    
    try:
        app = Application.builder().token(TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(button_handler))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_cevap))
        
        print("✅ Bot hazır!")
        print("📱 Telegram'da /start yazın")
        
        app.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

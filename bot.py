import os
import sys
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
import requests
import json
import re

print("=" * 80)
print("🚀 STARZBET AI BOT - GROQ AI DESTEKLİ")
print("=" * 80)

# TOKEN ve API KEY'ler
TOKEN = os.environ.get("TELEGRAM_TOKEN", "8031564377:AAHjJXBQ-b6f0BnKdbf6T7iwUjs1fCA7dW0")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

# Gerçek API anahtarınız buraya gelecek
# GROQ_API_KEY = "37c3DtkmCFAv3Yu9YFO7PIApNHJ_3xbtXtxwFaKxJXGrUNoUE"

# STARZBET BİLGİLERİ
STARZBET_BILGILERI = {
    "resmi_site": "https://starzbet422.com",
    "bonus_sayfasi": "https://starzbet422.com/tr-tr/info/promos",
    "spor_bahis": "https://starzbet422.com/sports",
    "canli_casino": "https://starzbet422.com/live-casino",
    "casino": "https://starzbet422.com/casino",
    "mobile_apk": "https://starzbet422.com/apk",
    "telegram": "https://t.me/Starzbetgir",
    "canli_destek": "https://service.3kanumaigc.com/chatwindow.aspx?siteId=90005302&planId=1b050682-cde5-4176-8236-3bb94c891197#",
    "giris_problem": "https://starzbet422.com/tr-tr/info/access",
    "kayit": "https://starzbet422.com/tr-tr/register"
}

# AI SİSTEM PROMPT'İ
GROQ_SYSTEM_PROMPT = """Sen Starzbet422.com'un resmi asistanısın. Kullanıcılara profesyonel ve yardımcı yanıtlar ver.

KURALLAR:
1. SADECE starzbet422.com hakkında konuş
2. Kısa ve net cevaplar ver (en fazla 3 cümle)
3. Linkleri her zaman paylaş
4. Türkçe dışında dil kullanma
5. Profesyonel dil kullan

BİLGİLER:
- Site: https://starzbet422.com
- Kayıt: https://starzbet422.com/tr-tr/register
- Bonuslar: https://starzbet422.com/tr-tr/info/promos
- Spor: https://starzbet422.com/sports
- Casino: https://starzbet422.com/live-casino
- Destek: https://service.3kanumaigc.com/chatwindow.aspx?siteId=90005302&planId=1b050682-cde5-4176-8236-3bb94c891197#

Cevap verirken direkt ve açıklayıcı ol."""

# Mesaj kontrolü
last_message_time = {}
MESSAGE_COOLDOWN = 2

# MENÜ
def ana_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🌐 RESMİ SİTE", url=STARZBET_BILGILERI["resmi_site"])],
        [InlineKeyboardButton("💰 BONUSLAR", callback_data="bonuslar"),
         InlineKeyboardButton("⚽ SPOR", callback_data="spor_bahis")],
        [InlineKeyboardButton("🎮 CASİNO", callback_data="casino"),
         InlineKeyboardButton("📱 APK", callback_data="apk")],
        [InlineKeyboardButton("🎧 CANLI DESTEK", url=STARZBET_BILGILERI["canli_destek"])],
        [InlineKeyboardButton("💬 AI İLE KONUŞ", callback_data="ai_chat"),
         InlineKeyboardButton("📢 TELEGRAM", url=STARZBET_BILGILERI["telegram"])]
    ])

def chat_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 BONUS SOR", callback_data="soru_bonus"),
         InlineKeyboardButton("⚽ BAHİS SOR", callback_data="soru_bahis")],
        [InlineKeyboardButton("🎮 CASİNO SOR", callback_data="soru_casino"),
         InlineKeyboardButton("💳 YATIRIM SOR", callback_data="soru_yatirim")],
        [InlineKeyboardButton("🔗 LİNK İSTE", callback_data="soru_link"),
         InlineKeyboardButton("📝 KAYIT OL", url=STARZBET_BILGILERI["kayit"])],
        [InlineKeyboardButton("🎧 CANLI DESTEK", url=STARZBET_BILGILERI["canli_destek"]),
         InlineKeyboardButton("🔙 ANA MENÜ", callback_data="ana_menu")]
    ])

# Mesaj kontrol fonksiyonu
def check_message_cooldown(user_id):
    current_time = datetime.now().timestamp()
    if user_id in last_message_time:
        time_diff = current_time - last_message_time[user_id]
        if time_diff < MESSAGE_COOLDOWN:
            return False
    last_message_time[user_id] = current_time
    return True

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not check_message_cooldown(user_id):
        return
    
    # API kontrolü
    ai_durum = "✅ Aktif" if GROQ_API_KEY and len(GROQ_API_KEY) > 30 else "⚠️ Manuel Mod"
    
    mesaj = f"""🌟 **STARZBET AI ASİSTANI** 🌟

🤖 **Sistem Durumu:** {ai_durum}
🕒 **Güncel:** {datetime.now().strftime("%d.%m.%Y %H:%M")}

**NASIL KULLANILIR:**
1. Butonlara tıklayarak hızlı bilgi alın
2. Doğrudan soru sorun
3. Menülerden istediğiniz bölüme gidin

**HIZLI ERİŞİM:**
• Bonuslar: /bonus
• Linkler: /linkler  
• Destek: /destek

🔗 **Site:** {STARZBET_BILGILERI['resmi_site']}"""
    
    await update.message.reply_text(
        mesaj,
        reply_markup=ana_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

# Groq AI Cevap Fonksiyonu (Düzenlenmiş)
async def groq_ai_cevap(kullanici_sorusu):
    """Groq AI ile cevap ver"""
    
    # API anahtarı kontrolü
    if not GROQ_API_KEY or len(GROQ_API_KEY) < 30:
        # Manuel cevaplar - API yoksa
        soru_lower = kullanici_sorusu.lower()
        
        if any(word in soru_lower for word in ['bonus', 'kampanya', 'promosyon']):
            return f"🎁 **Bonuslar:** Starzbet'te çeşitli bonuslar mevcuttur.\n🔗 Detaylar: {STARZBET_BILGILERI['bonus_sayfasi']}"
        
        elif any(word in soru_lower for word in ['bahis', 'spor', 'iddaa', 'oran']):
            return f"⚽ **Spor Bahisleri:** Futbol, basketbol, tenis ve daha fazlası.\n🔗 Bahis yap: {STARZBET_BILGILERI['spor_bahis']}"
        
        elif any(word in soru_lower for word in ['casino', 'rulet', 'slot', 'blackjack']):
            return f"🎮 **Casino:** Canlı casino ve slot oyunları.\n🔗 Oyna: {STARZBET_BILGILERI['canli_casino']}"
        
        elif any(word in soru_lower for word in ['yatırım', 'para', 'ödeme', 'çekim']):
            return f"💳 **Para İşlemleri:** Kredi kartı, banka havalesi, cepbank.\n🔗 Detaylar için canlı destek: {STARZBET_BILGILERI['canli_destek']}"
        
        elif any(word in soru_lower for word in ['kayıt', 'üye', 'register']):
            return f"📝 **Kayıt:** Ücretsiz ve hızlı kayıt olun.\n🔗 Kayıt: {STARZBET_BILGILERI['kayit']}"
        
        elif any(word in soru_lower for word in ['apk', 'mobil', 'indir']):
            return f"📱 **Mobil Uygulama:** Android için APK dosyası.\n🔗 İndir: {STARZBET_BILGILERI['mobile_apk']}"
        
        elif any(word in soru_lower for word in ['link', 'url', 'site', 'adres']):
            return f"🔗 **Ana Linkler:**\n• Site: {STARZBET_BILGILERI['resmi_site']}\n• Kayıt: {STARZBET_BILGILERI['kayit']}\n• Destek: {STARZBET_BILGILERI['canli_destek']}"
        
        else:
            return f"🤖 Size nasıl yardımcı olabilirim?\n\nButonları kullanarak hızlı bilgi alabilir veya doğrudan sorunuzu sorabilirsiniz.\n🔗 Site: {STARZBET_BILGILERI['resmi_site']}"
    
    try:
        # Groq API çağrısı
        url = "https://api.groq.com/openai/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": GROQ_SYSTEM_PROMPT},
                {"role": "user", "content": kullanici_sorusu}
            ],
            "temperature": 0.7,
            "max_tokens": 200,
            "top_p": 0.9
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=20)
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            # API hatası durumunda manuel cevap
            return f"🌟 **Starzbet422.com**\n\nSorunuz için en güncel bilgileri sitemizde bulabilirsiniz:\n🔗 {STARZBET_BILGILERI['resmi_site']}\n\nVeya canlı destek: {STARZBET_BILGILERI['canli_destek']}"
            
    except Exception as e:
        print(f"AI Hatası: {e}")
        return f"🤖 **Starzbet Bilgilendirmesi**\n\nDetaylı bilgi için:\n🔗 Site: {STARZBET_BILGILERI['resmi_site']}\n📞 Destek: {STARZBET_BILGILERI['canli_destek']}"

# Mesaj Handler
async def mesaj_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Çift mesaj kontrolü
    if not check_message_cooldown(user_id):
        return
    
    user_message = update.message.text
    
    # Çok kısa mesaj kontrolü
    if len(user_message.strip()) < 2:
        await update.message.reply_text(
            "Lütfen daha açıklayıcı bir soru sorun.",
            reply_markup=chat_menu()
        )
        return
    
    # Typing göster
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    # Cevap al
    ai_response = await groq_ai_cevap(user_message)
    
    # Cevabı kısalt (gerekiyorsa)
    if len(ai_response) > 1000:
        ai_response = ai_response[:1000] + "..."
    
    await update.message.reply_text(
        ai_response,
        reply_markup=chat_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

# Buton Handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "bonuslar":
        await query.edit_message_text(
            f"💰 **STARZBET BONUSLARI**\n\n"
            f"🎁 **Hoşgeldin Bonusu** - Yeni üyelere özel\n"
            f"⚽ **Spor Bonusları** - Bahisler için ekstra\n"
            f"🎰 **Casino Bonusu** - Slot ve masa oyunları\n"
            f"🔄 **Yenileme Bonusu** - Düzenli oyunculara\n\n"
            f"🔗 Tüm detaylar: {STARZBET_BILGILERI['bonus_sayfasi']}\n\n"
            f"*Şartlar ve koşullar sitede mevcuttur.*",
            reply_markup=ana_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    elif data == "spor_bahis":
        await query.edit_message_text(
            f"⚽ **SPOR BAHİSLERİ**\n\n"
            f"• Futbol (Tüm ligler)\n"
            f"• Basketbol\n"
            f"• Tenis\n"
            f"• Canlı bahis\n"
            f"• Yüksek oranlar\n\n"
            f"🔗 Hemen başla: {STARZBET_BILGILERI['spor_bahis']}",
            reply_markup=ana_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    elif data == "casino":
        await query.edit_message_text(
            f"🎮 **CASİNO OYUNLARI**\n\n"
            f"• Canlı Rulet\n"
            f"• Blackjack\n"
            f"• Slot Makineleri\n"
            f"• Poker\n"
            f"• Bakara\n\n"
            f"🔗 Oyna: {STARZBET_BILGILERI['canli_casino']}",
            reply_markup=ana_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    elif data == "apk":
        await query.edit_message_text(
            f"📱 **MOBİL UYGULAMA**\n\n"
            f"• Android APK indir\n"
            f"• Hızlı kurulum\n"
            f"• Tüm özellikler\n"
            f"• Güvenli erişim\n\n"
            f"🔗 İndir: {STARZBET_BILGILERI['mobile_apk']}",
            reply_markup=ana_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    elif data == "ai_chat":
        await query.edit_message_text(
            "💬 **SORU SORMA MODU**\n\n"
            "Starzbet ile ilgili sorularınızı buraya yazın.\n\n"
            "**Örnek sorular:**\n"
            "• Bonuslar nelerdir?\n"
            "• Nasıl para yatırabilirim?\n"
            "• Casino oyunları hangileri?\n"
            "• Çekim işlemi ne kadar sürer?\n\n"
            "*Sadece Starzbet konularında yardımcı olabilirim.*",
            reply_markup=chat_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    elif data == "ana_menu":
        await query.edit_message_text(
            "🏠 **Ana Menü**\n\n"
            "Size nasıl yardımcı olabilirim?",
            reply_markup=ana_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    elif data.startswith("soru_"):
        soru_tipi = data.replace("soru_", "")
        
        sorular = {
            "bonus": "Starzbet bonusları nelerdir?",
            "bahis": "Spor bahisleri nasıl oynanır?",
            "casino": "Casino oyunları neler?",
            "yatirim": "Para yatırma yöntemleri neler?",
            "link": "Starzbet linklerini verir misiniz?"
        }
        
        if soru_tipi in sorular:
            ai_response = await groq_ai_cevap(sorular[soru_tipi])
            await query.edit_message_text(
                text=ai_response,
                reply_markup=chat_menu(),
                parse_mode=ParseMode.MARKDOWN
            )

# Komutlar
async def komut_reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔄 **Sohbet sıfırlandı.**\n\n"
        "Yeni bir konuşmaya başlayabilirsiniz.",
        reply_markup=ana_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

async def komut_destek(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🎧 **CANLI DESTEK**\n\n"
        f"7/24 canlı destek hattımız:\n"
        f"{STARZBET_BILGILERI['canli_destek']}\n\n"
        f"• Teknik sorunlar\n"
        f"• Para işlemleri\n"
        f"• Hesap problemleri\n"
        f"• Genel sorular",
        reply_markup=ana_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

async def komut_linkler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🔗 **STARZBET LİNKLERİ**\n\n"
        f"• 🌐 Site: {STARZBET_BILGILERI['resmi_site']}\n"
        f"• 📝 Kayıt: {STARZBET_BILGILERI['kayit']}\n"
        f"• 🎁 Bonuslar: {STARZBET_BILGILERI['bonus_sayfasi']}\n"
        f"• ⚽ Spor: {STARZBET_BILGILERI['spor_bahis']}\n"
        f"• 🎮 Casino: {STARZBET_BILGILERI['canli_casino']}\n"
        f"• 📱 APK: {STARZBET_BILGILERI['mobile_apk']}\n"
        f"• 📢 Telegram: {STARZBET_BILGILERI['telegram']}",
        reply_markup=ana_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

async def komut_bonus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"💰 **BONUS BİLGİLERİ**\n\n"
        f"Tüm bonus detayları için:\n"
        f"{STARZBET_BILGILERI['bonus_sayfasi']}\n\n"
        f"*Bonus şartları sitede belirtilmiştir.*",
        reply_markup=ana_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

# Ana Program
def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    
    print("🚀 STARZBET BOT BAŞLATILIYOR...")
    print(f"🔗 Site: {STARZBET_BILGILERI['resmi_site']}")
    
    # API anahtar kontrolü
    if GROQ_API_KEY and len(GROQ_API_KEY) > 30:
        print("🤖 Groq AI: AKTİF")
    else:
        print("🤖 Groq AI: MANUEL MOD (API anahtarı gerekli)")
        print("ℹ️ Manuel modda çalışıyor - anahtar eklenirse AI aktif olacak")
    
    print("✅ Bot hazır!")
    
    try:
        app = Application.builder().token(TOKEN).build()
        
        # Handler'lar
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("reset", komut_reset))
        app.add_handler(CommandHandler("destek", komut_destek))
        app.add_handler(CommandHandler("linkler", komut_linkler))
        app.add_handler(CommandHandler("bonus", komut_bonus))
        app.add_handler(CallbackQueryHandler(button_handler))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mesaj_handler))
        
        app.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        print(f"❌ HATA: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

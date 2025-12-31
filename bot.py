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
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")

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

# GROQ AI SİSTEM PROMPT'İ (GÜNCELLENMİŞ)
GROQ_SYSTEM_PROMPT = """Sen Starzbet422.com'un resmi AI asistanısın. Kullanıcılara profesyonel, net ve yardımcı bir şekilde yanıt ver.

🚨 **KURALLAR:**
1. SADECE starzbet422.com hakkında konuş
2. Asla başka site veya platform önerme
3. Tüm bilgiler starzbet422.com'a yönlendirsin
4. Kısa ve öz cevaplar ver (maksimum 2-3 cümle)
5. Türkçe dışında dil kullanma
6. Samimi hitap (kanka, dostum) kullanma, profesyonel kal

📌 **TEMEL BİLGİLER:**
- Resmi site: https://starzbet422.com
- Kayıt: https://starzbet422.com/tr-tr/register
- Bonuslar: https://starzbet422.com/tr-tr/info/promos
- Spor bahis: https://starzbet422.com/sports
- Canlı casino: https://starzbet422.com/live-casino
- Telegram: https://t.me/Starzbetgir
- Canlı destek: https://service.3kanumaigc.com/chatwindow.aspx?siteId=90005302&planId=1b050682-cde5-4176-8236-3bb94c891197#
- Giriş sorunu: https://starzbet422.com/tr-tr/info/access
- APK: https://starzbet422.com/apk

💬 **KONUŞMA TARZI:**
- Profesyonel ve resmi dil kullan
- Kısa, net ve öz cevaplar (maksimum 100 kelime)
- Sadece gerekli emojiler kullan
- Linkleri her zaman paylaş
- Yardımsever ve bilgilendirici ol

❌ **YAPMA:**
- Uzun paragraflar yazma
- Tekrar eden bilgiler verme
- Türkçe dışında kelime kullanma
- Samimi hitap (kanka, dostum) kullanma
- Gereksiz detay verme

⚠️ **SINIRLAR:**
Eğer kullanıcı starzbet dışında bir site sorarsa:
"Starzbet422.com dışındaki platformlar hakkında bilgi veremem."

Eğer yasa dışı veya uygunsuz bir şey sorarsa:
"Bu konuda yardımcı olamıyorum. Lütfen Starzbet ile ilgili sorularınızı sorun."

Cevap formatı: Kısa ve öz, direkt soruya odaklı."""

# Mesaj geçmişi kontrolü için kullanıcı ID'leri
last_message_time = {}
MESSAGE_COOLDOWN = 2  # saniye

# MENÜ
def ana_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🌐 RESMİ SİTE", url=STARZBET_BILGILERI["resmi_site"])],
        [InlineKeyboardButton("💰 BONUSLAR", callback_data="bonuslar"),
         InlineKeyboardButton("⚽ SPOR BAHİS", callback_data="spor_bahis")],
        [InlineKeyboardButton("🎮 CASİNO", callback_data="casino"),
         InlineKeyboardButton("📱 MOBİL UYGULAMA", callback_data="apk")],
        [InlineKeyboardButton("🎧 CANLI DESTEK", url=STARZBET_BILGILERI["canli_destek"]),
         InlineKeyboardButton("📢 TELEGRAM", url=STARZBET_BILGILERI["telegram"])],
        [InlineKeyboardButton("💬 SORU SOR", callback_data="ai_chat")]
    ])

def chat_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 BONUSLAR", callback_data="soru_bonus"),
         InlineKeyboardButton("⚽ SPOR BAHİS", callback_data="soru_bahis")],
        [InlineKeyboardButton("🎮 CASİNO", callback_data="soru_casino"),
         InlineKeyboardButton("💳 PARA İŞLEMLERİ", callback_data="soru_yatirim")],
        [InlineKeyboardButton("🔗 ÖNEMLİ LİNKLER", callback_data="soru_link"),
         InlineKeyboardButton("📝 HEMEN KAYIT OL", url=STARZBET_BILGILERI["kayit"])],
        [InlineKeyboardButton("🎧 CANLI DESTEK", url=STARZBET_BILGILERI["canli_destek"]),
         InlineKeyboardButton("🏠 ANA MENÜ", callback_data="ana_menu")]
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

# Metin temizleme fonksiyonu
def clean_text(text):
    """Uzun metinleri kısalt ve temizle"""
    if len(text) > 1000:
        # Metni kısalt
        text = text[:1000] + "...\n\n*Devamını canlı destekten öğrenebilirsiniz.*"
    
    # Türkçe olmayan karakterleri kontrol et (basit)
    # Gereksiz tekrarları temizle
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        if line.strip() and len(line.strip()) > 3:
            cleaned_lines.append(line.strip())
    
    return '\n'.join(cleaned_lines[:10])  # Maksimum 10 satır

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not check_message_cooldown(user_id):
        return
    
    ai_durum = "✅ Aktif" if GROQ_API_KEY and GROQ_API_KEY != "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" else "⏸️ Demo Modu"
    
    mesaj = f"""🌟 **STARZBET AI ASİSTANI** 🌟

🤖 **AI Durumu:** {ai_durum}
🕒 **Son Güncelleme:** {datetime.now().strftime("%d.%m.%Y %H:%M")}

**HİZMETLERİMİZ:**
• Starzbet platform bilgilendirmesi
• Bonus ve kampanya detayları
• Spor bahis ve casino rehberliği
• Teknik destek yönlendirmesi

**HIZLI ERİŞİM:**
• Bonuslar için: /bonus
• Linkler için: /linkler
• Destek için: /destek
• Sıfırlama için: /reset

🔗 **Resmi Site:** {STARZBET_BILGILERI['resmi_site']}"""
    
    await update.message.reply_text(
        mesaj,
        reply_markup=ana_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

# GROQ AI CEVAP FONKSİYONU - GÜNCELLENMİŞ
async def groq_ai_cevap(kullanici_sorusu, user_id=None):
    """Groq AI ile kısa ve net cevap ver"""
    
    if not GROQ_API_KEY or GROQ_API_KEY == "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":
        return "🤖 AI hizmeti şu anda demo modunda çalışıyor. Detaylı bilgi için lütfen canlı desteğe başvurun."
    
    try:
        # Soruyu temizle
        kullanici_sorusu = kullanici_sorusu.strip()[:500]  # Maksimum 500 karakter
        
        url = "https://api.groq.com/openai/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": GROQ_SYSTEM_PROMPT},
                {"role": "user", "content": f"Lütfen kısa ve net cevap ver: {kullanici_sorusu}"}
            ],
            "temperature": 0.5,  # Daha az yaratıcı, daha tutarlı
            "max_tokens": 150,   # Daha kısa cevaplar
            "top_p": 0.8,
            "frequency_penalty": 0.5,  # Tekrarı azalt
            "presence_penalty": 0.3    # Konu sapmasını azalt
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result["choices"][0]["message"]["content"]
            
            # Cevabı temizle ve kısalt
            ai_response = clean_text(ai_response)
            
            # Türkçe kontrolü (basit) - Eğer Türkçe karakter azsa
            turkish_chars = set('abcçdefgğhıijklmnoöprsştuüvyzABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZ')
            char_count = sum(1 for char in ai_response[:100] if char in turkish_chars or char.isspace() or char in ',.!?;:')
            
            if char_count < 50:  # Eğer Türkçe karakter azsa standart cevap ver
                return "🌟 **Starzbet Hakkında:**\n\nDetaylı bilgi için lütfen resmi sitemizi ziyaret edin: https://starzbet422.com\n\nVeya canlı destekle iletişime geçin."
            
            return ai_response
            
        elif response.status_code == 401:
            return "🔐 API anahtarında sorun oluştu. Lütfen canlı desteğe başvurun."
        elif response.status_code == 429:
            return "⏳ Sistem yoğun, lütfen kısa süre sonra tekrar deneyin."
        else:
            return f"⚠️ Teknik bir sorun oluştu. Lütfen canlı desteğe başvurun: {STARZBET_BILGILERI['canli_destek']}"
            
    except requests.exceptions.Timeout:
        return "⏰ Yanıt süresi aşıldı. Lütfen tekrar deneyin."
    except requests.exceptions.ConnectionError:
        return "🔌 Bağlantı hatası. Lütfen internet bağlantınızı kontrol edin."
    except Exception as e:
        logging.error(f"Groq AI Hatası: {e}")
        return f"🤖 Teknik bir sorun oluştu. Canlı destek: {STARZBET_BILGILERI['canli_destek']}"

# MESAJ HANDLER - GÜNCELLENMİŞ
async def mesaj_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Çift mesaj göndermeyi engelle
    if not check_message_cooldown(user_id):
        return
    
    user_message = update.message.text
    
    # Mesaj çok kısa veya spam kontrolü
    if len(user_message.strip()) < 2:
        await update.message.reply_text(
            "Lütfen daha açıklayıcı bir soru sorun.",
            reply_markup=chat_menu()
        )
        return
    
    # "typing" göster
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    # AI'ya sor
    ai_response = await groq_ai_cevap(user_message, user_id)
    
    # Kısa ve net cevap kontrolü
    if len(ai_response.split()) > 150:
        ai_response = ' '.join(ai_response.split()[:150]) + "...\n\n*Devamı için canlı destekle iletişime geçebilirsiniz.*"
    
    await update.message.reply_text(
        ai_response,
        reply_markup=chat_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

# HIZLI SORULAR İÇİN - GÜNCELLENMİŞ
async def hizli_soru(update: Update, context: ContextTypes.DEFAULT_TYPE, soru_tipi):
    query = update.callback_query
    await query.answer()
    
    # Mesaj ID'sini kaydet (çift mesaj önleme)
    user_id = query.from_user.id
    if not check_message_cooldown(user_id):
        return
    
    sorular = {
        "bonus": "Starzbet bonusları nelerdir? Hoşgeldin bonusu var mı?",
        "bahis": "Spor bahisleri nasıl oynanır? Hangi ligler mevcut?",
        "casino": "Casino oyunları nelerdir? Canlı casino nasıl çalışır?",
        "yatirim": "Para yatırma yöntemleri neler? Minimum tutar ne kadar?",
        "link": "Starzbet resmi linklerini paylaşır mısınız?"
    }
    
    if soru_tipi in sorular:
        ai_response = await groq_ai_cevap(sorular[soru_tipi], user_id)
        await query.edit_message_text(
            text=ai_response,
            reply_markup=chat_menu(),
            parse_mode=ParseMode.MARKDOWN
        )

# BUTON HANDLER - GÜNCELLENMİŞ
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = query.from_user.id
    
    if not check_message_cooldown(user_id):
        return
    
    if data == "bonuslar":
        await query.edit_message_text(
            f"💰 **STARZBET BONUSLARI**\n\n"
            f"🎁 **Hoşgeldin Bonusu:** Yeni üyelere özel\n"
            f"⚽ **Spor Bonusları:** Bahisler için ek kazanç\n"
            f"🎰 **Casino Bonusu:** Slot ve masa oyunları\n"
            f"🔄 **Yenileme Bonusu:** Düzenli oyunculara\n\n"
            f"🔗 Detaylar: {STARZBET_BILGILERI['bonus_sayfasi']}\n\n"
            f"*Bonus kuralları sitede mevcuttur.*",
            reply_markup=ana_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    elif data == "spor_bahis":
        await query.edit_message_text(
            f"⚽ **SPOR BAHİSLERİ**\n\n"
            f"• Futbol, basketbol, tenis\n"
            f"• Canlı bahis seçenekleri\n"
            f"• Yüksek oran garantisi\n"
            f"• Hızlı sonuçlandırma\n\n"
            f"🔗 Hemen başla: {STARZBET_BILGILERI['spor_bahis']}",
            reply_markup=ana_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    elif data == "casino":
        await query.edit_message_text(
            f"🎮 **CASİNO OYUNLARI**\n\n"
            f"• Canlı rulet ve blackjack\n"
            f"• Slot makineleri\n"
            f"• Poker ve bakara\n"
            f"• Türkçe destekli\n\n"
            f"🔗 Oyna: {STARZBET_BILGILERI['canli_casino']}",
            reply_markup=ana_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    elif data == "apk":
        await query.edit_message_text(
            f"📱 **MOBİL UYGULAMA**\n\n"
            f"• Android APK indirme\n"
            f"• iOS uyumluluğu\n"
            f"• Hızlı ve güvenli\n"
            f"• Tüm özellikler mevcut\n\n"
            f"🔗 İndir: {STARZBET_BILGILERI['mobile_apk']}",
            reply_markup=ana_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    elif data == "ai_chat":
        await query.edit_message_text(
            "💬 **SORU SORMA MODU**\n\n"
            "Starzbet ile ilgili sorularınızı buradan sorabilirsiniz.\n\n"
            "**Örnek sorular:**\n"
            "• Para yatırma yöntemleri neler?\n"
            "• Nasıl kayıt olabilirim?\n"
            "• Çekim süresi ne kadar?\n"
            "• Hangi oyunlar mevcut?\n\n"
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
        await hizli_soru(update, context, soru_tipi)

# KOMUTLAR
async def komut_reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sohbeti sıfırla"""
    user_id = update.effective_user.id
    if check_message_cooldown(user_id):
        await update.message.reply_text(
            "🔄 **Sohbet sıfırlandı.**\n\n"
            "Yeni bir konuşmaya başlayabilirsiniz.",
            reply_markup=ana_menu(),
            parse_mode=ParseMode.MARKDOWN
        )

async def komut_destek(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Canlı destek"""
    user_id = update.effective_user.id
    if check_message_cooldown(user_id):
        await update.message.reply_text(
            f"🎧 **CANLI DESTEK**\n\n"
            f"İnsan temsilcimizle görüşmek için:\n"
            f"{STARZBET_BILGILERI['canli_destek']}\n\n"
            f"⏰ **7/24 Hizmet**\n"
            f"💬 **Türkçe Destek**\n"
            f"🔧 **Teknik Sorunlar**\n"
            f"💰 **Finansal İşlemler**",
            reply_markup=ana_menu(),
            parse_mode=ParseMode.MARKDOWN
        )

async def komut_linkler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tüm linkler"""
    user_id = update.effective_user.id
    if check_message_cooldown(user_id):
        await update.message.reply_text(
            f"🔗 **STARZBET LİNKLERİ**\n\n"
            f"• 🌐 **Site:** {STARZBET_BILGILERI['resmi_site']}\n"
            f"• 📝 **Kayıt:** {STARZBET_BILGILERI['kayit']}\n"
            f"• 🎁 **Bonuslar:** {STARZBET_BILGILERI['bonus_sayfasi']}\n"
            f"• ⚽ **Spor:** {STARZBET_BILGILERI['spor_bahis']}\n"
            f"• 🎮 **Casino:** {STARZBET_BILGILERI['canli_casino']}\n"
            f"• 📱 **APK:** {STARZBET_BILGILERI['mobile_apk']}\n"
            f"• 📢 **Telegram:** {STARZBET_BILGILERI['telegram']}\n"
            f"• 🎧 **Destek:** {STARZBET_BILGILERI['canli_destek']}",
            reply_markup=ana_menu(),
            parse_mode=ParseMode.MARKDOWN
        )

async def komut_bonus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bonus komutu"""
    user_id = update.effective_user.id
    if check_message_cooldown(user_id):
        await update.message.reply_text(
            f"💰 **BONUS BİLGİLERİ**\n\n"
            f"Tüm bonus detayları için:\n"
            f"{STARZBET_BILGILERI['bonus_sayfasi']}\n\n"
            f"*Bonus kuralları ve şartları sitede belirtilmiştir.*",
            reply_markup=ana_menu(),
            parse_mode=ParseMode.MARKDOWN
        )

# ANA PROGRAM
def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO,
        handlers=[
            logging.FileHandler('starzbet_bot.log'),
            logging.StreamHandler()
        ]
    )
    
    print("🚀 STARZBET AI BOT BAŞLATILIYOR...")
    print(f"🔗 Resmi Site: {STARZBET_BILGILERI['resmi_site']}")
    print(f"🤖 Groq AI: {'AKTİF' if GROQ_API_KEY and GROQ_API_KEY != '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' else 'DEMO'}")
    print("⚡ Optimizasyonlar: Aktif")
    print("🔒 Çift Mesaj Koruması: Aktif")
    print("📏 Kısa Cevap Modu: Aktif")
    
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
        
        print("✅ Bot hazır ve çalışıyor!")
        print("📱 Komutlar aktif: /start, /bonus, /linkler, /destek, /reset")
        print("💬 AI optimize edildi - kısa ve net cevaplar")
        
        app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logging.error(f"CRITICAL HATA: {e}")
        print(f"❌ Bot başlatılamadı: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

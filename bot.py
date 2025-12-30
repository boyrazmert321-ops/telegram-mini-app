import os
import sys
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
import requests
import json

print("=" * 80)
print("🚀 STARZBET AI BOT - KONTROLLÜ VERSİYON")
print("=" * 80)

# TOKEN ve AI ANAHTARI
TOKEN = os.environ.get("TELEGRAM_TOKEN", "8031564377:AAHjJXBQ-b6f0BnKdbf6T7iwUjs1fCA7dW0")
OPENAI_KEY = os.environ.get("OPENAI_KEY", "")  # Kendi OpenAI keyini koy

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
    "giris_problem": "https://starzbet422.com/tr-tr/info/access"
}

# AI SİSTEM PROMPT'İ (ÇOK ÖNEMLİ!)
AI_SYSTEM_PROMPT = """Sen Starzbet422.com'un resmi AI asistanısın. SADECE aşağıdaki konularda yardımcı olabilirsin:

🚨 **KURALLAR:**
1. SADECE starzbet422.com hakkında konuş
2. BAŞKA site önerme, link verme
3. Bonus, bahis, casino, yatırım/çekim, giriş konularında yardım et
4. Bilmediğin bir şey sorulursa "Canlı destekle iletişime geçin" de

📌 **VERİLECEK LİNKLER (SADECE BUNLAR):**
- Resmi site: https://starzbet422.com
- Bonuslar: https://starzbet422.com/tr-tr/info/promos
- Spor bahis: https://starzbet422.com/sports
- Canlı casino: https://starzbet422.com/live-casino
- Telegram: https://t.me/Starzbetgir
- Canlı destek: https://service.3kanumaigc.com/chatwindow.aspx?siteId=90005302&planId=1b050682-cde5-4176-8236-3bb94c891197#
- Giriş sorunu: https://starzbet422.com/tr-tr/info/access
- APK: https://starzbet422.com/apk

💬 **KONUŞMA TARZI:**
- Kanka, dostum gibi samimi ama profesyonel konuş
- Kısa ve net cevaplar ver
- Emoji kullan (🎰, ⚽, 🎁, 🔗)
- Linkleri her zaman ver

❌ **YAPMA:**
- Starzbet dışında site önerme
- Hayali bonus uydurma
- Yanlış bilgi verme
- Politik/uyuşturucu konulara girme"""

# MENÜ
def ana_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 RESMİ SİTE", url=STARZBET_BILGILERI["resmi_site"])],
        [InlineKeyboardButton("💰 BONUSLAR", callback_data="bonuslar"),
         InlineKeyboardButton("⚽ SPOR", url=STARZBET_BILGILERI["spor_bahis"])],
        [InlineKeyboardButton("🎮 CASİNO", url=STARZBET_BILGILERI["canli_casino"]),
         InlineKeyboardButton("📱 APK", url=STARZBET_BILGILERI["mobile_apk"])],
        [InlineKeyboardButton("🎧 CANLI DESTEK", url=STARZBET_BILGILERI["canli_destek"]),
         InlineKeyboardButton("📢 TELEGRAM", url=STARZBET_BILGILERI["telegram"])],
        [InlineKeyboardButton("🤖 AI İLE KONUŞ", callback_data="ai_chat")]
    ])

def chat_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 BONUS SOR", callback_data="soru_bonus"),
         InlineKeyboardButton("⚽ BAHİS SOR", callback_data="soru_bahis")],
        [InlineKeyboardButton("🎮 CASİNO SOR", callback_data="soru_casino"),
         InlineKeyboardButton("💳 YATIRIM SOR", callback_data="soru_yatirim")],
        [InlineKeyboardButton("🔗 LİNK İSTE", callback_data="soru_link"),
         InlineKeyboardButton("🎧 CANLI DESTEK", url=STARZBET_BILGILERI["canli_destek"])],
        [InlineKeyboardButton("🔙 ANA MENÜ", callback_data="ana_menu")]
    ])

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ai_durum = "✅ Aktif" if OPENAI_KEY else "❌ Devre Dışı"
    
    mesaj = f"""🌟 *STARZBET422.COM AI ASİSTANI* 🌟

🤖 *AI Durumu:* {ai_durum}
🕒 *Son Güncelleme:* {datetime.now().strftime("%d.%m.%Y %H:%M")}

🎯 *NELER YAPABİLİRİM:*
• Starzbet bonuslarını anlatırım
• Bahis ve casino konularında yardım ederim
• Gerekli linkleri veririm
• Samimi sohbet ederim

🚫 *NELER YAPMAM:*
• Başka site önermem
• Yanlış bilgi vermem
• Starzbet dışında konuşmam

💬 *AI ile konuşmak için:* "AI İLE KONUŞ" butonuna bas
🎧 *Canlı insan için:* Canlı Destek butonu

🔗 *Resmi Site:* {STARZBET_BILGILERI['resmi_site']}"""
    
    await update.message.reply_text(
        mesaj,
        reply_markup=ana_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

# AI CHAT FONKSİYONU
async def ai_cevap_ver(kullanici_sorusu, chat_history=None):
    """OpenAI ile kontrollü cevap ver"""
    
    if not OPENAI_KEY:
        return "🤖 AI şu anda aktif değil. Lütfen butonları kullanın veya canlı desteğe başvurun."
    
    try:
        # Chat history oluştur
        messages = [
            {"role": "system", "content": AI_SYSTEM_PROMPT}
        ]
        
        # Eski konuşmaları ekle
        if chat_history:
            messages.extend(chat_history[-6:])  # Son 6 mesajı al
        
        # Kullanıcı sorusunu ekle
        messages.append({"role": "user", "content": kullanici_sorusu})
        
        # OpenAI API çağrısı
        headers = {
            "Authorization": f"Bearer {OPENAI_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 300
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result["choices"][0]["message"]["content"]
            return ai_response
        else:
            return f"⚠️ AI yanıt vermedi. Lütfen canlı desteğe başvurun: {STARZBET_BILGILERI['canli_destek']}"
            
    except Exception as e:
        print(f"AI Hatası: {e}")
        return f"🤖 Teknik sorun. Canlı destek: {STARZBET_BILGILERI['canli_destek']}"

# MESAJ HANDLER
async def mesaj_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text
    
    # Kullanıcının chat geçmişini al veya oluştur
    if 'chat_history' not in context.user_data:
        context.user_data['chat_history'] = []
    
    # AI ile cevap ver
    ai_response = await ai_cevap_ver(user_message, context.user_data['chat_history'])
    
    # Geçmişe ekle
    context.user_data['chat_history'].append({"role": "user", "content": user_message})
    context.user_data['chat_history'].append({"role": "assistant", "content": ai_response})
    
    # Geçmişi sınırla (max 10 mesaj)
    if len(context.user_data['chat_history']) > 10:
        context.user_data['chat_history'] = context.user_data['chat_history'][-10:]
    
    await update.message.reply_text(
        ai_response,
        reply_markup=chat_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

# HIZLI SORULAR İÇİN
async def hizli_soru(update: Update, context: ContextTypes.DEFAULT_TYPE, soru_tipi):
    query = update.callback_query
    await query.answer()
    
    sorular = {
        "bonus": "Starzbet'te şu anki bonuslar neler? Hoşgeldin bonusu var mı?",
        "bahis": "Spor bahislerinde özel oran nasıl alınır? Canlı bahis var mı?",
        "casino": "Canlı casino oyunları neler? Rulet ve blackjack bonusu var mı?",
        "yatirim": "Para yatırma yöntemleri neler? Komisyon alınıyor mu?",
        "link": "Starzbet giriş linki, APK indirme ve Telegram kanalı linklerini verir misin?"
    }
    
    if soru_tipi in sorular:
        ai_response = await ai_cevap_ver(sorular[soru_tipi])
        await query.message.reply_text(
            ai_response,
            reply_markup=chat_menu(),
            parse_mode=ParseMode.MARKDOWN
        )

# BUTON HANDLER
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "bonuslar":
        await query.message.reply_text(
            f"🎁 *STARZBET BONUSLARI* 🎁\n\n"
            f"🔗 Tüm bonuslar: {STARZBET_BILGILERI['bonus_sayfasi']}\n\n"
            f"💬 Bonus detayları için AI ile konuşabilir veya canlı desteğe başvurabilirsin.",
            reply_markup=ana_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    elif data == "ai_chat":
        await query.message.reply_text(
            "💬 *AI İLE KONUŞMA MODU* 💬\n\n"
            "🤖 Şimdi bana Starzbet ile ilgili ne sormak istersin?\n\n"
            "🎯 *Örnek sorular:*\n"
            "• Bonuslar neler?\n"
            "• Nasıl para yatırabilirim?\n"
            "• Casino oyunları neler?\n"
            "• Bahis oranları nasıl?\n\n"
            "🚫 *Dikkat:* Sadece Starzbet konularında yardımcı olabilirim.",
            reply_markup=chat_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    elif data == "ana_menu":
        await query.message.reply_text(
            "🔙 *Ana Menüye Döndünüz* 🔙\n\n"
            "Yardıma ihtiyacın olan bir şey var mı kanka?",
            reply_markup=ana_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    elif data.startswith("soru_"):
        soru_tipi = data.replace("soru_", "")
        await hizli_soru(update, context, soru_tipi)

# KOMUTLAR
async def komut_reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Chat geçmişini temizle"""
    if 'chat_history' in context.user_data:
        context.user_data['chat_history'] = []
    
    await update.message.reply_text(
        "🔄 *Chat geçmişi temizlendi!*\n\n"
        "Yeni bir konuşmaya başlayabiliriz kanka!",
        reply_markup=ana_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

async def komut_destek(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Canlı destek bilgisi"""
    await update.message.reply_text(
        f"🎧 *CANLI DESTEK* 🎧\n\n"
        f"İnsan desteğine ihtiyacın varsa:\n"
        f"{STARZBET_BILGILERI['canli_destek']}\n\n"
        f"⏰ 7/24 hizmet\n"
        f"💬 Türkçe destek",
        reply_markup=ana_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

# ANA PROGRAM
def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    
    print("🚀 STARZBET AI BOT BAŞLATILIYOR...")
    print(f"🔗 Resmi Site: {STARZBET_BILGILERI['resmi_site']}")
    print(f"🤖 AI Durumu: {'AKTİF' if OPENAI_KEY else 'PASİF'}")
    print("✅ Kontrollü AI - Saçmalamayacak")
    
    try:
        app = Application.builder().token(TOKEN).build()
        
        # Handler'lar
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("reset", komut_reset))
        app.add_handler(CommandHandler("destek", komut_destek))
        app.add_handler(CallbackQueryHandler(button_handler))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mesaj_handler))
        
        print("✅ Bot hazır!")
        print("📱 /start komutunu bekliyor...")
        print("💬 AI aktif, kontrollü konuşacak")
        
        app.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        print(f"❌ CRITICAL HATA: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

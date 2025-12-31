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
print("🚀 STARZBET AI BOT - GROQ AI DESTEKLİ")
print("=" * 80)

# TOKEN ve API KEY'ler
TOKEN = os.environ.get("TELEGRAM_TOKEN", "8031564377:AAHjJXBQ-b6f0BnKdbf6T7iwUjs1fCA7dW0")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")

# STARZBET BİLGİLERİ
STARZBET_BILGILERI = {
    "resmi_site": "https://starzbet423.com",
    "bonus_sayfasi": "https://starzbet423.com/tr-tr/info/promos",
    "spor_bahis": "https://starzbet423.com/sports",
    "canli_casino": "https://starzbet423.com/live-casino",
    "casino": "https://starzbet423.com/casino",
    "mobile_apk": "https://starzbet423.com/apk",
    "telegram": "https://t.me/Starzbetgir",
    "canli_destek": "https://service.3kanumaigc.com/chatwindow.aspx?siteId=90005302&planId=1b050682-cde5-4176-8236-3bb94c891197#",
    "giris_problem": "https://starzbet423.com/tr-tr/info/access",
    "kayit": "https://starzbet423.com/tr-tr/register"
}

# GROQ AI SİSTEM PROMPT'İ
GROQ_SYSTEM_PROMPT = """Sen Starzbet422.com'un resmi AI asistanısın. Kullanıcılarla samimi (kanka, dostum diyerek) ve yardımcı bir şekilde konuş.

🚨 **KESİN KURALLAR:**
1. SADECE ve SADECE starzbet422.com hakkında konuş
2. Asla başka site, bahis şirketi veya platform önerme
3. Tüm bilgiler starzbet422.com'a yönlendirsin
4. Bilmediğin bir şey sorulursa "Canlı destekle iletişime geçin" de

📌 **STARZBET BİLGİLERİ:**
- Resmi site: https://starzbet422.com
- Kayıt: https://starzbet422.com/tr-tr/register
- Bonuslar: https://starzbet422.com/tr-tr/info/promos
- Spor bahis: https://starzbet422.com/sports
- Canlı casino: https://starzbet422.com/live-casino
- Telegram: https://t.me/Starzbetgir
- Canlı destek: https://service.3kanumaigc.com/chatwindow.aspx?siteId=90005302&planId=1b050682-cde5-4176-8236-3bb94c891197#
- Giriş sorunu: https://starzbet422.com/tr-tr/info/access
- APK: https://starzbet422.com/apk

🎯 **YARDIMCI OLACAĞIN KONULAR:**
• Bonuslar ve kampanyalar
• Para yatırma/çekme işlemleri
• Spor bahis oranları
• Casino oyunları
• Giriş/kayıt problemleri
• Mobil uygulama (APK)
• Özel oranlar (telegram kanalı)

💬 **KONUŞMA TARZI:**
- Samimi, arkadaş gibi konuş (kanka, dostum, abi)
- Kısa, net ve öz cevaplar ver
- Emoji kullan (🎰, ⚽, 🎁, 💰, 🔥)
- Linkleri her zaman paylaş
- Pozitif ve yardımsever ol

❌ **ASLA YAPMA:**
- Starzbet dışında site önerme
- Yanlış veya hayali bonus bilgisi verme
- Politik/dini konulara girme
- Uygunsuz dil kullanma
- Kullanıcıyı yanlış yönlendirme

⚠️ **TEHLİKELİ SORULARDA:**
Eğer kullanıcı starzbet dışında bir site sorarsa:
"Kusura bakma kanka, ben sadece starzbet422.com hakkında yardımcı olabilirim. Başka site bilemem."

Eğer yasa dışı bir şey sorarsa:
"Bu konuda yardımcı olamam. Lütfen starzbet422.com ile ilgili sorular sor."

Şimdi kullanıcının sorusuna uygun şekilde cevap ver."""

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
         InlineKeyboardButton("📝 KAYIT OL", url=STARZBET_BILGILERI["kayit"])],
        [InlineKeyboardButton("🎧 CANLI DESTEK", url=STARZBET_BILGILERI["canli_destek"]),
         InlineKeyboardButton("🔙 ANA MENÜ", callback_data="ana_menu")]
    ])

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ai_durum = "✅ Aktif" if GROQ_API_KEY else "❌ Devre Dışı"
    
    mesaj = f"""🌟 *STARZBET422.COM AI ASİSTANI* 🌟

🤖 *AI Durumu:* {ai_durum}
🕒 *Son Güncelleme:* {datetime.now().strftime("%d.%m.%Y %H:%M")}

🎯 *NELER YAPABİLİRİM:*
• Starzbet hakkında her şeyi anlatırım
• Bonus ve kampanyaları açıklarım
• Bahis/casino konularında yardım ederim
• Samimi sohbet ederim (kanka gibi)

🚫 *NELER YAPMAM:*
• Başka site önermem (sadece starzbet422.com)
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

# GROQ AI CEVAP FONKSİYONU
async def groq_ai_cevap(kullanici_sorusu):
    """Groq AI ile cevap ver"""
    
    if not GROQ_API_KEY:
        return "🤖 AI şu anda aktif değil. Lütfen butonları kullanın veya canlı desteğe başvurun."
    
    try:
        # Groq API endpoint
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
            "max_tokens": 500,
            "top_p": 0.9
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result["choices"][0]["message"]["content"]
            return ai_response
        elif response.status_code == 401:
            return "🔑 AI anahtar hatası. Lütfen canlı desteğe başvurun."
        elif response.status_code == 429:
            return "⏳ AI yoğun, lütfen biraz sonra tekrar deneyin."
        else:
            error_msg = f"⚠️ AI yanıt vermedi (Hata: {response.status_code}). Lütfen canlı desteğe başvurun: {STARZBET_BILGILERI['canli_destek']}"
            return error_msg
            
    except requests.exceptions.Timeout:
        return "⏰ AI yanıt vermedi (zaman aşımı). Lütfen tekrar deneyin."
    except requests.exceptions.ConnectionError:
        return "🔌 Bağlantı hatası. Lütfen internet bağlantınızı kontrol edin."
    except Exception as e:
        print(f"Groq AI Hatası: {e}")
        return f"🤖 Teknik sorun oluştu. Canlı destek: {STARZBET_BILGILERI['canli_destek']}"

# MESAJ HANDLER
async def mesaj_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    
    # Önce AI'ya sor
    ai_response = await groq_ai_cevap(user_message)
    
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
        "bonus": "Starzbet'te şu an aktif olan bonuslar neler? Hoşgeldin bonusu var mı? Casino bonusu nasıl?",
        "bahis": "Spor bahislerinde özel oran nasıl alınır? Canlı bahis var mı? Hangi sporlar var?",
        "casino": "Canlı casino oyunları neler? Rulet, blackjack, baccarat var mı? Slot makineleri nasıl?",
        "yatirim": "Para yatırma yöntemleri neler? Komisyon alınıyor mu? Minimum yatırım ne kadar?",
        "link": "Starzbet giriş linki, kayıt linki, APK indirme linki ve Telegram kanalı linklerini verir misin?"
    }
    
    if soru_tipi in sorular:
        ai_response = await groq_ai_cevap(sorular[soru_tipi])
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
            f"🔗 Tüm bonuslar: {STARZBET_BILGILERI['bonus_sayfasi']}\n"
            f"💸 Hoşgeldin bonusu mevcut\n"
            f"🎰 Casino bonusları aktif\n"
            f"⚽ Spor bahis bonusları\n\n"
            f"💬 Detaylı bilgi için AI ile konuşabilirsin!",
            reply_markup=ana_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    elif data == "ai_chat":
        await query.message.reply_text(
            "💬 *AI İLE KONUŞMA MODU* 💬\n\n"
            "🤖 Şimdi bana Starzbet ile ilgili ne sormak istersin?\n\n"
            "🎯 *Örnek sorular:*\n"
            "• Bonuslar nelerdir?\n"
            "• Nasıl para yatırabilirim?\n"
            "• Casino oyunları neler?\n"
            "• Özel oran nasıl alınır?\n"
            "• Mobil uygulamayı nasıl indirebilirim?\n\n"
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
    await update.message.reply_text(
        "🔄 *Sohbet sıfırlandı!*\n\n"
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
        f"💬 Türkçe destek\n"
        f"🔧 Teknik sorunlar\n"
        f"💰 Para işlemleri",
        reply_markup=ana_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

async def komut_linkler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tüm linkleri göster"""
    await update.message.reply_text(
        f"🔗 *STARZBET TÜM LİNKLERİ* 🔗\n\n"
        f"• 🌐 Resmi Site: {STARZBET_BILGILERI['resmi_site']}\n"
        f"• 📝 Kayıt Ol: {STARZBET_BILGILERI['kayit']}\n"
        f"• 🎁 Bonuslar: {STARZBET_BILGILERI['bonus_sayfasi']}\n"
        f"• ⚽ Spor Bahis: {STARZBET_BILGILERI['spor_bahis']}\n"
        f"• 🎮 Canlı Casino: {STARZBET_BILGILERI['canli_casino']}\n"
        f"• 📱 APK İndir: {STARZBET_BILGILERI['mobile_apk']}\n"
        f"• 📢 Telegram: {STARZBET_BILGILERI['telegram']}\n"
        f"• 🎧 Canlı Destek: {STARZBET_BILGILERI['canli_destek']}\n"
        f"• 🚨 Giriş Sorunu: {STARZBET_BILGILERI['giris_problem']}",
        reply_markup=ana_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

# ANA PROGRAM
def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    
    print("🚀 STARZBET GROQ AI BOT BAŞLATILIYOR...")
    print(f"🔗 Resmi Site: {STARZBET_BILGILERI['resmi_site']}")
    print(f"🤖 Groq AI Durumu: {'AKTİF' if GROQ_API_KEY else 'PASİF'}")
    print(f"🔑 API Key: {'Var' if GROQ_API_KEY else 'Yok'}")
    print("✅ Groq AI ile çalışacak - Llama 3.3 70B modeli")
    
    try:
        app = Application.builder().token(TOKEN).build()
        
        # Handler'lar
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("reset", komut_reset))
        app.add_handler(CommandHandler("destek", komut_destek))
        app.add_handler(CommandHandler("linkler", komut_linkler))
        app.add_handler(CallbackQueryHandler(button_handler))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mesaj_handler))
        
        print("✅ Bot hazır!")
        print("📱 /start komutunu bekliyor...")
        print("💬 Groq AI aktif, samimi sohbet edecek")
        
        app.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        print(f"❌ CRITICAL HATA: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

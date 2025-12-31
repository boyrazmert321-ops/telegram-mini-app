import os
import sys
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
import requests
import json

# Loglama
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

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

# KURUMSAL GROQ AI SİSTEM PROMPT'İ
GROQ_SYSTEM_PROMPT = """Siz STARZBET platformunun resmi kurumsal AI asistanısınız. 

🚨 **KURALLAR:**
1. Profesyonel, ciddi ve kurumsal bir dil kullanın. "Kanka, dostum, kanka" gibi samimi ifadeleri asla kullanmayın.
2. Kullanıcılara "Siz" diye hitap edin.
3. Cevaplar kısa, net ve bilgi odaklı olmalıdır.
4. "Starzbet422.com" yerine marka ismi olarak sadece "STARZBET" kullanın.
5. Sadece STARZBET hakkında bilgi verin. Başka platform önermeyin.
6. Bilmediğiniz bir konu olursa doğrudan "Canlı Destek" birimine yönlendirin.

🎯 **KONULAR:** Bonuslar, Finansal İşlemler, Kayıt, Mobil Uygulama ve Teknik Destek.
Cevaplarınızı emojilerle destekleyin ancak kurumsallığı bozmayın."""

# MENÜLER
def ana_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 STARZBET GİRİŞ", url=STARZBET_BILGILERI["resmi_site"])],
        [InlineKeyboardButton("💰 BONUSLAR", callback_data="bonuslar"),
         InlineKeyboardButton("⚽ SPOR", url=STARZBET_BILGILERI["spor_bahis"])],
        [InlineKeyboardButton("🎮 CASİNO", url=STARZBET_BILGILERI["canli_casino"]),
         InlineKeyboardButton("📱 APK", url=STARZBET_BILGILERI["mobile_apk"])],
        [InlineKeyboardButton("🎧 CANLI DESTEK", url=STARZBET_BILGILERI["canli_destek"]),
         InlineKeyboardButton("📢 TELEGRAM", url=STARZBET_BILGILERI["telegram"])],
        [InlineKeyboardButton("🤖 AI ASİSTAN İLE KONUŞ", callback_data="ai_chat")]
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
    mesaj = f"""🌟 *STARZBET'E HOŞGELDİNİZ* 🌟

Sizlere 7/24 hizmet veren resmi STARZBET AI asistanıyım. Platformumuzla ilgili tüm konularda size yardımcı olmaya hazırım.

🎯 *HİZMETLERİMİZ:*
• Güncel Bonus Bilgileri
• Finansal İşlem Rehberi
• Casino ve Spor Bahisleri
• Mobil Uygulama Desteği

Lütfen aşağıdaki menüyü kullanarak devam ediniz."""
    
    await update.message.reply_text(mesaj, reply_markup=ana_menu(), parse_mode=ParseMode.MARKDOWN)

# GROQ AI CEVAP FONKSİYONU
async def groq_ai_cevap(kullanici_sorusu):
    if not GROQ_API_KEY:
        return "Sistem şu anda güncellenmektedir. Lütfen Canlı Destek birimimize başvurunuz."
    
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": GROQ_SYSTEM_PROMPT},
                {"role": "user", "content": kullanici_sorusu}
            ],
            "temperature": 0.4, # Daha tutarlı cevaplar için
            "max_tokens": 400
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        return f"Şu anda yanıt veremiyorum. Lütfen buradan devam edin: {STARZBET_BILGILERI['canli_destek']}"
    except Exception:
        return "Bir teknik aksaklık yaşandı. Lütfen Canlı Destek hattına bağlanınız."

# MESAJ HANDLER
async def mesaj_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ai_response = await groq_ai_cevap(update.message.text)
    await update.message.reply_text(ai_response, reply_markup=chat_menu(), parse_mode=ParseMode.MARKDOWN)

# BUTON VE HIZLI SORU HANDLER
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "bonuslar":
        await query.edit_message_text(
            f"🎁 *STARZBET PROMOSYONLARI*\n\nGüncel bonus ve kampanyalarımızı aşağıdaki linkten inceleyebilirsiniz:\n\n🔗 {STARZBET_BILGILERI['bonus_sayfasi']}",
            reply_markup=ana_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    elif data == "ai_chat":
        await query.edit_message_text(
            "💬 *STARZBET AI DESTEK HATTI*\n\nSize nasıl yardımcı olabilirim? Sorularınızı aşağıdaki butonlardan seçebilir veya yazarak iletebilirsiniz.",
            reply_markup=chat_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    elif data == "ana_menu":
        await query.edit_message_text(
            "🌟 *STARZBET'E HOŞGELDİNİZ*\n\nAna menüden yapmak istediğiniz işlemi seçiniz.",
            reply_markup=ana_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    elif data.startswith("soru_"):
        soru_tipleri = {
            "bonus": "STARZBET güncel bonus kampanyaları nelerdir?",
            "bahis": "Spor bahisleri ve oranlar hakkında bilgi verir misiniz?",
            "casino": "Casino ve canlı casino oyunlarınız nelerdir?",
            "yatirim": "Para yatırma ve çekme yöntemleri nelerdir?",
            "link": "STARZBET resmi giriş ve sosyal medya linklerini paylaşır mısınız?"
        }
        soru = soru_tipleri.get(data.replace("soru_", ""))
        ai_response = await groq_ai_cevap(soru)
        # Soru cevaplarını yeni mesaj olarak atıyoruz ki önceki menü kaybolmasın
        await query.message.reply_text(ai_response, reply_markup=chat_menu(), parse_mode=ParseMode.MARKDOWN)

# ANA PROGRAM
def main():
    try:
        app = Application.builder().token(TOKEN).build()
        
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(button_handler))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mesaj_handler))
        
        print("✅ STARZBET Kurumsal AI Bot Yayında!")
        app.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        print(f"❌ HATA: {e}")

if __name__ == "__main__":
    main()

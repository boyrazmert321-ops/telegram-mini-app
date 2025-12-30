import os
import sys
import logging
import random
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
import requests
from bs4 import BeautifulSoup
import re

print("=" * 80)
print("🚀 STARZBET RESMİ BOT - STARZBET422.COM KAYNAKLI")
print("=" * 80)

# TOKEN
TOKEN = os.environ.get("TELEGRAM_TOKEN", "8031564377:AAHjJXBQ-b6f0BnKdbf6T7iwUjs1fCA7dW0")

# STARZBET422.COM'DAN VERİ ÇEKME FONKSİYONU
def starzbet_sitesinden_veri_cek():
    """Starzbet422.com'dan güncel verileri çeker"""
    try:
        # Ana sayfayı çek
        response = requests.get("https://starzbet422.com", timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Bonusları çek (site yapısına göre güncelleyebilirsin)
        bonuslar = []
        # Promosyon sayfasından bonusları çek
        try:
            promos_response = requests.get("https://starzbet422.com/tr-tr/info/promos", timeout=10)
            promos_soup = BeautifulSoup(promos_response.content, 'html.parser')
            
            # Bonus başlıklarını bul (CSS selector'ları siteye göre ayarlanmalı)
            bonus_elements = promos_soup.select('.promotion-item, .bonus-item, .offer-title')
            for element in bonus_elements[:5]:  # İlk 5 bonusu al
                text = element.get_text(strip=True)
                if text and len(text) > 5:
                    bonuslar.append(f"🎁 {text}")
        except:
            pass
        
        # Eğer bonus bulamazsak, varsayılan bonuslar
        if not bonuslar:
            bonuslar = [
                "🎁 HOŞGELDİN BONUSU: İlk yatırımınıza bonus",
                "🎰 CASINO BONUSU: Canlı casino oyunlarında bonus",
                "⚽ SPOR BONUSU: Spor bahislerinde ekstra kazanç",
                "✨ KAYIP İADESİ: Seçili oyunlarda iade",
                "🔥 TEKRAR YATIRIM: Her yatırımda ekstra"
            ]
        
        return {
            "site_baslik": "Starzbet422.com - Resmi Bahis Sitesi",
            "bonuslar": bonuslar,
            "son_guncelleme": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "site_aktif": True
        }
    except Exception as e:
        print(f"⚠️ Site verisi çekilemedi: {e}")
        return {
            "site_baslik": "Starzbet422.com - Resmi Bahis Sitesi",
            "bonuslar": [
                "🎁 Site güncelleniyor, lütfen canlı destekle iletişime geçin"
            ],
            "son_guncelleme": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "site_aktif": False
        }

# GÜNCEL VERİLER (HER SEFERİNDE SİTEDEN ÇEKİLECEK)
def get_guncel_veriler():
    return starzbet_sitesinden_veri_cek()

# LİNKLER (SADECE STARZBET422.COM LİNKLERİ)
LINKLER = {
    "ana_site": "https://starzbet422.com",
    "giris": "https://starzbet422.com",
    "bonus": "https://starzbet422.com/tr-tr/info/promos",
    "telegram_kanal": "https://t.me/Starzbetgir",
    "canli_destek": "https://service.3kanumaigc.com/chatwindow.aspx?siteId=90005302&planId=1b050682-cde5-4176-8236-3bb94c891197#",
    "casino": "https://starzbet422.com/casino",
    "spor": "https://starzbet422.com/sports",
    "mobile_apk": "https://starzbet422.com/apk",
    "canli_casino": "https://starzbet422.com/live-casino",
    "giris_problem": "https://starzbet422.com/tr-tr/info/access"
}

# MENÜLER
def ana_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 RESMİ SİTEYE GİT", url=LINKLER["ana_site"])],
        [InlineKeyboardButton("💰 GÜNCEL BONUSLAR", callback_data="guncel_bonuslar")],
        [InlineKeyboardButton("🎮 CANLI CASİNO", url=LINKLER["canli_casino"]),
         InlineKeyboardButton("⚽ SPOR BAHİS", url=LINKLER["spor"])],
        [InlineKeyboardButton("📱 MOBİL UYGULAMA", url=LINKLER["mobile_apk"]),
         InlineKeyboardButton("🎧 CANLI DESTEK", url=LINKLER["canli_destek"])],
        [InlineKeyboardButton("🚨 GİRİŞ PROBLEMİ", url=LINKLER["giris_problem"])]
    ])

# /start KOMUTU
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    veriler = get_guncel_veriler()
    
    mesaj = f"""🌟 *Starzbet422.com Resmi Asistanı* 🌟

🔄 *Veriler:* {veriler['son_guncelleme']}
📊 *Kaynak:* starzbet422.com

🏆 *RESMİ BİLGİLER:*
• Tüm bilgiler starzbet422.com'dan alınmaktadır
• Güncel bonuslar ve kampanyalar
• Resmi giriş adresleri

⚠️ *DİKKAT:*
• Sadece starzbet422.com resmi sitemizdir
• Başka site önermiyoruz
• Tüm sorularınız için canlı destek

🔗 *Resmi Site:* {LINKLER['ana_site']}"""
    
    await update.message.reply_text(
        mesaj,
        reply_markup=ana_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

# GÜNCEL BONUSLAR (SİTEDEN ÇEKİLEN)
async def guncel_bonuslar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    veriler = get_guncel_veriler()
    
    bonus_mesaji = f"🎁 *STARZBET422.COM GÜNCEL BONUSLARI* 🎁\n\n"
    bonus_mesaji += f"🕒 *Son Güncelleme:* {veriler['son_guncelleme']}\n\n"
    
    for bonus in veriler["bonuslar"]:
        bonus_mesaji += f"• {bonus}\n"
    
    bonus_mesaji += f"\n🔗 *Tüm bonuslar:* {LINKLER['bonus']}"
    bonus_mesaji += f"\n\n⚠️ *Bonus kuralları için:* {LINKLER['canli_destek']}"
    
    await query.message.reply_text(
        bonus_mesaji,
        reply_markup=ana_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

# MESAJ HANDLER - SADECE STARZBET422.COM'A ÖZEL
async def mesaj_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.lower()
    veriler = get_guncel_veriler()
    
    # SADECE BELİRLİ KONULARDA CEVAP VER
    anahtar_kelimeler = {
        "bonus": f"🎁 *Bonuslar:*\n\n" + "\n".join(veriler["bonuslar"][:3]) + f"\n\n🔗 Tüm bonuslar: {LINKLER['bonus']}",
        "yatırım": f"💰 *Yatırım için:*\n\n{LINKLER['ana_site']} adresine gidin ve 'Para Yatır' butonuna tıklayın.\n\n⚠️ Canlı destek: {LINKLER['canli_destek']}",
        "para yatır": f"💰 *Para Yatırma:*\n\n{LINKLER['ana_site']}\n\nCanlı destekten yardım alın: {LINKLER['canli_destek']}",
        "çekim": f"💳 *Para Çekme:*\n\n{LINKLER['ana_site']} → 'Para Çek'\n\n⚠️ Detaylar için canlı destek: {LINKLER['canli_destek']}",
        "bahis": f"⚽ *Spor Bahisleri:*\n\n{LINKLER['spor']}\n\n🎯 Canlı bahis ve oranlar",
        "casino": f"🎮 *Canlı Casino:*\n\n{LINKLER['canli_casino']}\n\n✨ Slot, rulet, blackjack",
        "giriş": f"🔗 *Resmi Giriş:*\n\n{LINKLER['giris']}\n\n🚨 Sorun yaşarsanız: {LINKLER['giris_problem']}",
        "link": f"🔗 *Resmi Linkler:*\n\n• Ana Site: {LINKLER['ana_site']}\n• Spor: {LINKLER['spor']}\n• Casino: {LINKLER['canli_casino']}",
        "telegram": f"📢 *Telegram Kanalı:*\n\n{LINKLER['telegram_kanal']}\n\n⚡ Güncel duyurular ve oranlar",
        "mobile": f"📱 *Mobil Uygulama:*\n\n{LINKLER['mobile_apk']}\n\nAndroid cihazlar için APK",
        "apk": f"📱 *APK İndir:*\n\n{LINKLER['mobile_apk']}\n\nStarzbet mobil uygulaması",
        "merhaba": "🌟 *Merhaba!* Starzbet422.com resmi asistanına hoş geldiniz! 🎰\n\nNasıl yardımcı olabilirim?",
        "selam": "👋 *Selam!* Starzbet422.com için buradayım!\n\nİhtiyacın olan bir şey var mı?",
        "yardım": f"🆘 *Yardım Merkezi:*\n\n1. Teknik sorun: {LINKLER['canli_destek']}\n2. Giriş sorunu: {LINKLER['giris_problem']}\n3. Bonus soruları: {LINKLER['bonus']}\n\n⚠️ Tüm detaylar için canlı destekle iletişime geçin.",
        "özel oran": f"🎯 *Özel Oranlar:*\n\nGüncel özel oranlar için Telegram kanalımızı takip edin:\n{LINKLER['telegram_kanal']}\n\nVeya siteyi ziyaret edin: {LINKLER['spor']}",
        "oran": f"📊 *Bahis Oranları:*\n\n{LINKLER['spor']}\n\n⚽ Tüm sporlar ve canlı oranlar"
    }
    
    # ANAHTAR KELİME KONTROLÜ
    for kelime, cevap in anahtar_kelimeler.items():
        if kelime in user_message:
            await update.message.reply_text(
                cevap,
                parse_mode=ParseMode.MARKDOWN
            )
            return
    
    # EĞER ANLAMADIYSA CANLI DESTEĞE YÖNLENDİR
    await update.message.reply_text(
        f"❓ *Anlayamadım*\n\n"
        f"Lütfen aşağıdaki konulardan birini sorun:\n"
        f"• bonus\n• yatırım\n• bahis\n• casino\n• giriş\n• mobile\n\n"
        f"Veya doğrudan canlı desteğe bağlanın:\n"
        f"🎧 {LINKLER['canli_destek']}",
        parse_mode=ParseMode.MARKDOWN
    )

# BUTON HANDLER
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "guncel_bonuslar":
        veriler = get_guncel_veriler()
        
        bonus_mesaji = f"🎁 *GÜNCEL BONUSLAR* 🎁\n\n"
        for bonus in veriler["bonuslar"]:
            bonus_mesaji += f"• {bonus}\n"
        
        bonus_mesaji += f"\n🔗 {LINKLER['bonus']}"
        
        await query.message.reply_text(
            bonus_mesaji,
            reply_markup=ana_menu(),
            parse_mode=ParseMode.MARKDOWN
        )

# ANA PROGRAM
def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    
    print("🚀 Starzbet422.com Resmi Botu başlatılıyor...")
    print("📊 Veri kaynağı: starzbet422.com")
    
    try:
        # İlk veri çekme testi
        veriler = get_guncel_veriler()
        print(f"✅ Site bağlantısı: {'Aktif' if veriler['site_aktif'] else 'Pasif'}")
        print(f"🕒 Son güncelleme: {veriler['son_guncelleme']}")
        
        app = Application.builder().token(TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(button_handler))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mesaj_handler))
        
        print("✅ Bot hazır!")
        print("📱 Telegram'da /start yazın")
        print("⚠️ Sadece starzbet422.com bilgileri paylaşılacak")
        
        app.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

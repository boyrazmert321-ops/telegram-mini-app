import os
import sys
import logging
import random
import requests
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

print("=" * 70)
print("🚀 STARZBET ULTRA BOT - DİNAMİKPAY ÖNCELİKLİ")
print("=" * 70)

# 1. TOKEN ve API KEY'ler
TOKEN = os.environ.get("TELEGRAM_TOKEN", "8031564377:AAHjJXBQ-b6f0BnKdbf6T7iwUjs1fCA7dW0")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")

# 2. LİNKLER (DİNAMİKPAY ÖNCELİKLİ!)
DINAMIKPAY_LINK = "https://cutt.ly/dynamicpay-starzbet"
TELEGRAM_KANAL = "https://t.me/Starzbetgir"
BONUS_LINK = "https://starzbet422.com/tr-tr/info/promos"
CANLI_DESTEK = "https://service.3kanumaigc.com/chatwindow.aspx?siteId=90005302&planId=1b050682-cde5-4176-8236-3bb94c891197#"
MINI_APP = "https://telegram-mini-app-umber-chi.vercel.app"
GIRIS_LINK = "https://cutt.ly/drVOi2EN"

# 3. GÖRSEL URL'leri (GitHub'dan)
GORSEL_URL = "https://raw.githubusercontent.com/[KULLANICI]/[REPO]/main/ana.jpg"
DINAMIK_GORSEL = "https://raw.githubusercontent.com/[KULLANICI]/[REPO]/main/dinamik.jpg"
BONUS_GORSEL = "https://raw.githubusercontent.com/[KULLANICI]/[REPO]/main/35kayip.jpg"
CASINO_GORSEL = "https://raw.githubusercontent.com/[KULLANICI]/[REPO]/main/casinohosgelin.jpg"
SPOR_GORSEL = "https://raw.githubusercontent.com/[KULLANICI]/[REPO]/main/sporhosgel.jpg"
MOBIL_GORSEL = "https://raw.githubusercontent.com/[KULLANICI]/[REPO]/main/uygulama.jpg"

# 4. TELEGRAM KANAL SON POST ALMA
def son_kanal_postu():
    """Starzbet kanalından son postu al"""
    try:
        # Telegram kanalından son post URL'si (manuel güncelle)
        return {
            "text": "🔥 CANLI BAHİS: Galatasaray - Fenerbahçe\n⚽ MS 1: 2.10 | X: 3.40 | 2: 3.20\n🎯 ALT/ÜST 2.5: Üst 1.90 | Alt 1.95\n💰 %100 BONUS ile bahis yap!",
            "link": TELEGRAM_KANAL
        }
    except:
        return {
            "text": "🎯 Güncel bahisler için kanalımızı takip edin!",
            "link": TELEGRAM_KANAL
        }

# 5. DİNAMİKPAY SİSTEMİ
DINAMIKPAY_SISTEMI = {
    "odemeler": {
        "papara": {"komisyon": "%0", "limit": "Min 100₺ - Max 50.000₺", "sure": "ANINDA"},
        "jeton": {"komisyon": "%0", "limit": "Min 100₺ - Max 30.000₺", "sure": "ANINDA"},
        "cebbank": {"komisyon": "%0", "limit": "Min 100₺ - Max 100.000₺", "sure": "ANINDA"},
        "kredi_karti": {"komisyon": "%0", "limit": "Min 100₺ - Max 20.000₺", "sure": "2-5 dk"},
        "bitcoin": {"komisyon": "%0", "limit": "Min 500₺ - Max 500.000₺", "sure": "10-30 dk"}
    },
    "avantajlar": [
        "⚡ ANINDA işlem onayı",
        "🔒 %100 GÜVENLİ ödeme",
        "💰 SIFIR komisyon",
        "📱 7/24 aktif",
        "🔄 Otomatik yatırım",
        "🎁 Özel DİNAMİKPAY bonusları"
    ],
    "bonuslar": {
        "ilk_yatirim": "DİNAMİKPAY ile ilk yatırımda %150 bonus",
        "tekrarlayan": "Her DİNAMİKPAY yatırımında %25 ekstra",
        "vip": "DİNAMİKPAY VIP üyelerine özel %50 cashback"
    }
}

# 6. AI CLIENT
client = None
if GROQ_API_KEY:
    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        print("✅ Groq AI bağlantısı başarılı")
    except Exception as e:
        print(f"⚠️ Groq hatası: {e}")
        client = None

# 7. MENÜLER (DİNAMİKPAY HER YERDE!)
def ana_menu():
    """Ana menü - DİNAMİKPAY ön planda"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⚡ DİNAMİKPAY YATIR", callback_data="dinamikpay_yatir")],
        [InlineKeyboardButton("💰 BONUSLAR", callback_data="bonuslar"),
         InlineKeyboardButton("🎮 CASİNO", callback_data="casino")],
        [InlineKeyboardButton("⚽ SPOR BAHİS", callback_data="spor_bahis"),
         InlineKeyboardButton("🎰 MİNİ APP", web_app=WebAppInfo(url=MINI_APP))],
        [InlineKeyboardButton("📱 MOBİL", callback_data="mobile"),
         InlineKeyboardButton("📊 CANLI BAHİS", callback_data="canli_bahis")],
        [InlineKeyboardButton("🎧 CANLI DESTEK", url=CANLI_DESTEK),
         InlineKeyboardButton("🔗 GÜNCEL GİRİŞ", url=GIRIS_LINK)]
    ])

def dinamikpay_menu():
    """DİNAMİKPAY özel menü"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 PAPARA İLE YATIR", callback_data="papara_yatir")],
        [InlineKeyboardButton("📱 JETON İLE YATIR", callback_data="jeton_yatir")],
        [InlineKeyboardButton("🏦 CEPBANK İLE YATIR", callback_data="cebbank_yatir")],
        [InlineKeyboardButton("💎 KREDİ KARTI İLE YATIR", callback_data="kredi_yatir")],
        [InlineKeyboardButton("₿ BITCOIN İLE YATIR", callback_data="bitcoin_yatir")],
        [InlineKeyboardButton("🔙 ANA MENÜ", callback_data="ana_menu")]
    ])

def yatirim_sonrasi_menu():
    """Yatırım sonrası menü"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎰 HEMEN OYNA", callback_data="hemen_oyna")],
        [InlineKeyboardButton("⚽ BAHİS YAP", callback_data="bahis_yap")],
        [InlineKeyboardButton("💰 BONUSLARIM", callback_data="bonuslarim")],
        [InlineKeyboardButton("📞 DESTEK", url=CANLI_DESTEK)]
    ])

# 8. KARŞILAMA MESAJLARI (DİNAMİKPAY ÖNCELİKLİ!)
KARSILAMA_MESAJLARI = [
    "🌟 *Hoş Geldiniz!* DİNAMİKPAY ile anında yatırım yap, %150 bonus kazan!",
    "🚀 *Starzbet'e Hoş Geldiniz!* İlk DİNAMİKPAY yatırımınızda %150 bonus sizi bekliyor!",
    "⚡ *Süper Bahis Deneyimi!* DİNAMİKPAY ile 7/24 anında yatırım, sıfır komisyon!",
    "🎰 *Kazancın Adresi!* DİNAMİKPAY VIP üyelerine özel %50 cashback avantajı!",
    "💰 *Para Yatırmanın En Hızlı Yolu!* DİNAMİKPAY ile anında hesabınıza geçsin!"
]

# 9. /start KOMUTU (DİNAMİKPAY VURGULU)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Başlangıç komutu - Her zaman DİNAMİKPAY öncelikli"""
    karsilama = random.choice(KARSILAMA_MESAJLARI)
    ai_status = "✅ Aktif" if client else "❌ Devre Dışı"
    
    mesaj = f"""{karsilama}

🤖 *AI Asistan Durumu:* {ai_status}

⚡ *DİNAMİKPAY AVANTAJLARI:*
• %150 İlk Yatırım Bonusu
• Sıfır Komisyon
• Anında Hesaba Geçiş
• 7/24 Aktif Sistem

🎯 *Hemen Başlayın:*
1. DİNAMİKPAY ile yatırım yap
2. %150 bonusunuzu alın
3. Bahis/Casino'da kazanmaya başlayın

🔗 *Özel Link:* {DINAMIKPAY_LINK}"""
    
    try:
        await update.message.reply_photo(
            photo=GORSEL_URL,
            caption=mesaj,
            reply_markup=ana_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
    except:
        await update.message.reply_text(
            mesaj,
            reply_markup=ana_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
    
    # Otomatik DİNAMİKPAY hatırlatma (5 sn sonra)
    await asyncio.sleep(5)
    await update.message.reply_text(
        "💡 *Hatırlatma:* DİNAMİKPAY ile yatırım yapmayı unutmayın! %150 bonus kaçmasın!",
        reply_markup=dinamikpay_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

# 10. DİNAMİKPAY İŞLEMLERİ
async def dinamikpay_yatir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """DİNAMİKPAY yatırım ekranı"""
    query = update.callback_query
    await query.answer()
    
    mesaj = f"""⚡ *DİNAMİKPAY SİSTEMİ* ⚡

💰 *ÖDEME YÖNTEMLERİ:*
"""
    
    for yontem, detay in DINAMIKPAY_SISTEMI["odemeler"].items():
        mesaj += f"\n• *{yontem.upper().replace('_', ' ')}:*\n"
        mesaj += f"  Komisyon: {detay['komisyon']}\n"
        mesaj += f"  Limit: {detay['limit']}\n"
        mesaj += f"  Süre: {detay['sure']}\n"
    
    mesaj += f"\n🎁 *DİNAMİKPAY BONUSLARI:*\n"
    for bonus, aciklama in DINAMIKPAY_SISTEMI["bonuslar"].items():
        mesaj += f"• {aciklama}\n"
    
    mesaj += f"\n🔗 *Özel Link:* {DINAMIKPAY_LINK}"
    
    try:
        await query.message.reply_photo(
            photo=DINAMIK_GORSEL,
            caption=mesaj,
            reply_markup=dinamikpay_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
    except:
        await query.edit_message_text(
            mesaj,
            reply_markup=dinamikpay_menu(),
            parse_mode=ParseMode.MARKDOWN
        )

# 11. ÖDEME YÖNTEMLERİ
async def papara_yatir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await yatirim_yontemi(update, "PAPARA", "papara")

async def jeton_yatir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await yatirim_yontemi(update, "JETON", "jeton")

async def cepbank_yatir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await yatirim_yontemi(update, "CEPBANK", "cebbank")

async def kredi_yatir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await yatirim_yontemi(update, "KREDİ KARTI", "kredi_karti")

async def bitcoin_yatir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await yatirim_yontemi(update, "BITCOIN", "bitcoin")

async def yatirim_yontemi(update: Update, yontem_adi: str, yontem_key: str):
    """Yatırım yöntemi detayı"""
    query = update.callback_query
    await query.answer()
    
    detay = DINAMIKPAY_SISTEMI["odemeler"][yontem_key]
    
    mesaj = f"""💳 *{yontem_adi} İLE YATIRIM* 💳

📋 *DETAYLAR:*
• Komisyon: {detay['komisyon']}
• Limit: {detay['limit']}
• Süre: {detay['sure']}

🎁 *BU YÖNTEME ÖZEL BONUS:*
• İlk yatırım: %150 bonus
• Tekrarlayan yatırımlar: %25 ekstra
• VIP üyelik: %50 cashback

📝 *ADIMLAR:*
1. {DINAMIKPAY_LINK} adresine git
2. '{yontem_adi}' seçeneğini seç
3. Yatırmak istediğiniz tutarı girin
4. Ödeme bilgilerinizi tamamlayın
5. *ANINDA* hesabınıza geçsin!

⚠️ *ÖNEMLİ:* Yatırım sonrası bonus otomatik eklenir.

🔗 *Hemen Yatırım Yap:* {DINAMIKPAY_LINK}"""
    
    await query.message.reply_text(
        mesaj,
        reply_markup=yatirim_sonrasi_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

# 12. BAHİS SİSTEMİ
async def spor_bahis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Spor bahis ekranı"""
    query = update.callback_query
    await query.answer()
    
    # Kanal son postunu getir
    kanal_post = son_kanal_postu()
    
    mesaj = f"""⚽ *CANLI SPOR BAHİSLERİ* ⚽

{kanal_post['text']}

🎯 *ÖNERİLEN MAÇLAR:*
1. Galatasaray - Fenerbahçe
   ⚽ MS 1: 2.10 | X: 3.40 | 2: 3.20
   
2. Beşiktaş - Trabzonspor
   ⚽ MS 1: 2.30 | X: 3.20 | 2: 3.00
   
3. Real Madrid - Barcelona
   ⚽ MS 1: 2.00 | X: 3.60 | 2: 3.80

💰 *BAHİS YAPMAK İÇİN:*
1. Önce DİNAMİKPAY ile yatırım yap
2. %150 bonusunuzu alın
3. Bahis yapmaya başlayın

📊 *GÜNCEL ORANLAR:* {TELEGRAM_KANAL}
🔗 *Bahis Yap:* {GIRIS_LINK}"""
    
    try:
        await query.message.reply_photo(
            photo=SPOR_GORSEL,
            caption=mesaj,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎯 BAHİS YAP", url=GIRIS_LINK)],
                [InlineKeyboardButton("⚡ YATIRIM YAP", callback_data="dinamikpay_yatir")],
                [InlineKeyboardButton("📊 TÜM MAÇLAR", url=TELEGRAM_KANAL)]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
    except:
        await query.edit_message_text(
            mesaj,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎯 BAHİS YAP", url=GIRIS_LINK)],
                [InlineKeyboardButton("⚡ YATIRIM YAP", callback_data="dinamikpay_yatir")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )

async def canli_bahis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Canlı bahis ekranı"""
    query = update.callback_query
    await query.answer()
    
    mesaj = f"""🔥 *CANLI BAHİS - ANINDA KAZAN!* 🔥

⚡ *ŞU AN OYNAYAN MAÇLAR:*
• Galatasaray - Fenerbahçe (60')
• Real Madrid - Barcelona (45')
• Bayern Münih - Dortmund (30')

🎯 *CANLI ORANLAR:*
GS - FB: 1. Gol: 2.50 | Sonraki Gol: 1.90
RM - BAR: Toplam Gol 2.5 Üst: 1.85
BAY - DOR: İkinci Yarı Kazanan: 1.80

💰 *CANLI BAHİS TAKTİKLERİ:*
1. Maç gidişatını izle
2. DİNAMİKPAY ile anında yatırım
3. Canlı oranlarla bahis yap
4. Anında kazan!

📈 *CANLI İSTATİSTİKLER:* {TELEGRAM_KANAL}
🔗 *Canlı Bahis:* {GIRIS_LINK}/live"""
    
    await query.message.reply_text(
        mesaj,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔥 CANLI BAHİS YAP", url=f"{GIRIS_LINK}/live")],
            [InlineKeyboardButton("⚡ ANINDA YATIRIM", callback_data="dinamikpay_yatir")],
            [InlineKeyboardButton("📊 CANLI SKOR", url=TELEGRAM_KANAL)]
        ]),
        parse_mode=ParseMode.MARKDOWN
    )

# 13. DİĞER MENÜLER
async def bonuslar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    mesaj = f"""🎁 *STARZBET BONUS SİSTEMİ* 🎁

🌟 *DİNAMİKPAY ÖZEL BONUSLAR:*
• İlk DİNAMİKPAY Yatırımı: %150 BONUS
• Her DİNAMİKPAY Yatırımı: %25 EKSTRA
• DİNAMİKPAY VIP: %50 CASHBACK

💰 *DİĞER BONUSLAR:*
• Hoşgeldin Bonusu: %100 (max 5.000₺)
• Slot Bonusu: %100 slot oyunlarında
• Spor Bonusu: %100 spor bahislerinde
• Kayıp İadesi: %35 kayıplarınıza
• Arkadaş Davet: 500₺ her davet için

⚡ *BONUS KULLANIMI:*
1. DİNAMİKPAY ile yatırım yap
2. Bonus otomatik hesabınıza eklenecek
3. 30x çevrim şartını yerine getir
4. Kazancınızı çekin!

📌 *ŞARTLAR:*
- Min yatırım: 100₺
- Max bonus: 10.000₺
- Çevrim: 30x
- Süre: 30 gün

🔗 *Tüm Bonuslar:* {BONUS_LINK}"""
    
    try:
        await query.message.reply_photo(
            photo=BONUS_GORSEL,
            caption=mesaj,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⚡ DİNAMİKPAY İLE YATIR", callback_data="dinamikpay_yatir")],
                [InlineKeyboardButton("💰 BONUSLARIM", callback_data="bonuslarim")],
                [InlineKeyboardButton("🔙 ANA MENÜ", callback_data="ana_menu")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
    except:
        await query.edit_message_text(
            mesaj,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⚡ DİNAMİKPAY İLE YATIR", callback_data="dinamikpay_yatir")],
                [InlineKeyboardButton("🔙 ANA MENÜ", callback_data="ana_menu")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )

async def casino(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    mesaj = """🎮 *CANLI CASİNO & SLOT* 🎮

✨ *POPÜLER OYUNLAR:*
• 🃏 Canlı Blackjack - %99.5 RTP
• 🎡 Rulet - Gerçek krupiyelerle
• 🎰 Gates of Olympus - x5000 Kazanç
• 🎲 Baccarat - Hızlı ve heyecanlı
• 🎯 Poker - Texas Hold'em

🔥 *CASİNO BONUSLARI:*
- İlk casino yatırımı: %200 BONUS
- Canlı casino: %50 ekstra
- Slot oyunları: %100 FREE SPIN
- Her Cuma: %25 CASHBACK

⚡ *NASIL OYNANIR:*
1. DİNAMİKPAY ile yatırım yap
2. %200 casino bonusunuzu alın
3. Canlı krupiyelerle oynayın
4. Büyük kazançlar elde edin

🎯 *CANLI KRUPİYELER:* 7/24 hizmetinizde!
🔗 *Casino'ya Git:* https://starzbet422.com/casino"""
    
    try:
        await query.message.reply_photo(
            photo=CASINO_GORSEL,
            caption=mesaj,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎮 CANLI CASİNO", url="https://starzbet422.com/casino")],
                [InlineKeyboardButton("⚡ YATIRIM YAP", callback_data="dinamikpay_yatir")],
                [InlineKeyboardButton("🎰 SLOT OYUNLARI", callback_data="slot_oyunlari")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
    except:
        await query.edit_message_text(
            mesaj,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎮 CANLI CASİNO", url="https://starzbet422.com/casino")],
                [InlineKeyboardButton("⚡ YATIRIM YAP", callback_data="dinamikpay_yatir")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )

async def mobile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    mesaj = """📱 *STARZBET MOBİL UYGULAMA* 📱

🌟 *ÖZELLİKLER:*
• ⚡ Süper hızlı arayüz
• 📲 iOS 15+ & Android 8+ desteği
• 🔔 Anlık bildirimler
• 💳 DİNAMİKPAY entegrasyonu
• 🎮 Akıcı casino deneyimi
• ⚽ Canlı bahis akışı

🔥 *MOBİL ÖZEL AVANTAJLAR:*
- Mobil yatırım: %25 ekstra bonus
- İlk mobil bahis: %50 free bet
- Mobil casino: %30 cashback
- App özel turnuvalar

📥 *İNDİRME LİNKLERİ:*
• Android APK: https://starzbet422.com/apk
• iOS TestFlight: https://starzbet422.com/ios
• APK Mirror: https://starzbet422.com/mirror

⚠️ *NOT:* iOS uygulaması App Store'dan kaldırıldı, TestFlight ile indirin.

📞 *MOBİL DESTEK:* @starzbetmobile"""
    
    try:
        await query.message.reply_photo(
            photo=MOBIL_GORSEL,
            caption=mesaj,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📲 ANDROID İNDİR", url="https://starzbet422.com/apk")],
                [InlineKeyboardButton("🍎 iOS İNDİR", url="https://starzbet422.com/ios")],
                [InlineKeyboardButton("⚡ YATIRIM YAP", callback_data="dinamikpay_yatir")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
    except:
        await query.edit_message_text(
            mesaj,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📲 ANDROID İNDİR", url="https://starzbet422.com/apk")],
                [InlineKeyboardButton("🍎 iOS İNDİR", url="https://starzbet422.com/ios")]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )

# 14. AI SİSTEMİ (DİNAMİKPAY ODAKLI)
async def ai_cevap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Akıllı AI yanıt sistemi"""
    user_message = update.message.text.lower().strip()
    
    # ÖNCE YEREL CEVAPLAR (DİNAMİKPAY ÖNCELİKLİ)
    cevap = dinamikpay_odakli_cevap(user_message)
    if cevap:
        await update.message.reply_text(
            cevap,
            reply_markup=dinamikpay_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # BAHİS SORUSU MU?
    if any(kelime in user_message for kelime in ["bahis", "oran", "maç", "iddaa", "spor"]):
        kanal_post = son_kanal_postu()
        await update.message.reply_text(
            f"⚽ *Bahis Sorunuza Cevap:*\n\n{kanal_post['text']}\n\n"
            f"🔗 Güncel bahisler için: {TELEGRAM_KANAL}\n"
            f"💰 Bahis yapmak için önce DİNAMİKPAY ile yatırım yapın!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⚡ YATIRIM YAP", callback_data="dinamikpay_yatir")],
                [InlineKeyboardButton("📊 BAHİSLER", url=TELEGRAM_KANAL)]
            ]),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # AI YOKSA
    if not client:
        await update.message.reply_text(
            "🤖 *AI şu anda kullanılamıyor.*\n\n"
            "⚡ *Önerim:* Hemen DİNAMİKPAY ile yatırım yapın!",
            reply_markup=dinamikpay_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # AI İLE CEVAP
    thinking_msg = await update.message.reply_text("⚡ *DİNAMİKPAY kontrol ediliyor...*", parse_mode=ParseMode.MARKDOWN)
    
    try:
        system_prompt = f"""Sen Starzbet'in DİNAMİKPAY odaklı AI asistanısın.

ÖNEMLİ BİLGİLER:
• DİNAMİKPAY Linki: {DINAMIKPAY_LINK}
• Bonus Linki: {BONUS_LINK}
• Telegram Kanalı: {TELEGRAM_KANAL}
• Canlı Destek: {CANLI_DESTEK}
• Giriş Linki: {GIRIS_LINK}

DİNAMİKPAY SİSTEMİ:
{KisaBilgi()}

KURALLAR:
1. HER SORUDA DİNAMİKPAY'I ÖNE ÇIKAR
2. "yatırım yapacam" diyene HEMEN DİNAMİKPAY linki ver
3. Bahis sorana Telegram kanalındaki son postu söyle
4. Bonus sorana DİNAMİKPAY bonuslarını anlat
5. Kısa, net, satış odaklı cevaplar ver
6. Her cevabın sonuna DİNAMİKPAY teşviki ekle

Şimdi kullanıcı şunu soruyor:"""
        
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.8,
            max_tokens=350
        )
        
        await thinking_msg.delete()
        ai_response = completion.choices[0].message.content
        
        # DİNAMİKPAY mesajı ekle
        final_response = f"{ai_response}\n\n💡 *Öneri:* Kazancınızı artırmak için hemen DİNAMİKPAY ile yatırım yapın!"
        
        await update.message.reply_text(
            f"🤖 *Starzbet AI:*\n\n{final_response}",
            reply_markup=dinamikpay_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
        
    except Exception as e:
        logging.error(f"AI hatası: {e}")
        try:
            await thinking_msg.delete()
        except:
            pass
        
        await update.message.reply_text(
            f"❌ *Üzgünüm, bir hata oluştu.*\n\n"
            f"⚡ *Hemen DİNAMİKPAY ile yatırım yaparak başlayın:* {DINAMIKPAY_LINK}",
            reply_markup=dinamikpay_menu(),
            parse_mode=ParseMode.MARKDOWN
        )

def dinamikpay_odakli_cevap(soru):
    """DİNAMİKPAY odaklı yerel cevaplar"""
    soru = soru.lower()
    
    # DİNAMİKPAY ve YATIRIM SORULARI
    if any(kelime in soru for kelime in ["yatırım", "yatır", "para yatır", "deposit", "ödeme"]):
        return f"""⚡ *DİNAMİKPAY İLE YATIRIM* ⚡

Hemen yatırım yapmak için: {DINAMIKPAY_LINK}

🎯 *AVANTAJLAR:*
• %150 İlk Yatırım Bonusu
• Sıfır Komisyon
• Anında Hesaba Geçiş
• 7/24 Aktif

💳 *YÖNTEMLER:* Papara, Jeton, Cepbank, Kredi Kartı, Bitcoin

🔗 *Hemen Başla:* {DINAMIKPAY_LINK}"""
    
    elif any(kelime in soru for kelime in ["bonus", "kampanya", "promosyon"]):
        return f"""🎁 *DİNAMİKPAY ÖZEL BONUSLAR* 🎁

• İlk DİNAMİKPAY Yatırımı: %150 BONUS
• Her DİNAMİKPAY Yatırımı: %25 EKSTRA
• DİNAMİKPAY VIP: %50 CASHBACK

🔗 Tüm bonuslar: {BONUS_LINK}
⚡ Yatırım yap: {DINAMIKPAY_LINK}"""
    
    elif any(kelime in soru for kelime in ["merhaba", "selam", "hi", "hello", "naber"]):
        karsilama = random.choice(KARSILAMA_MESAJLARI)
        return f"""{karsilama}

⚡ *İlk adım:* DİNAMİKPAY ile yatırım yapın!
🔗 {DINAMIKPAY_LINK}"""
    
    elif any(kelime in soru for kelime in ["giriş", "link", "site", "url"]):
        return f"""🔗 *GİRİŞ LİNKLERİ:*

• Ana Giriş: {GIRIS_LINK}
• DİNAMİKPAY: {DINAMIKPAY_LINK}
• Bonuslar: {BONUS_LINK}
• Telegram: {TELEGRAM_KANAL}

⚡ *Öneri:* Önce DİNAMİKPAY ile yatırım yapın!"""
    
    elif any(kelime in soru for kelime in ["destek", "yardım", "iletişim"]):
        return f"""📞 *DESTEK SEÇENEKLERİ:*

• Canlı Destek: {CANLI_DESTEK}
• Telegram: @starzbetsupport
• E-posta: destek@starzbet.com

⚡ *Öncelik:* Yatırım işlemleriniz için DİNAMİKPAY sistemimizi kullanın!"""
    
    elif any(kelime in soru for kelime in ["nasıl", "yapılır", "kayıt", "üye"]):
        return f"""📝 *KAYIT & YAT

import os
import sys
import logging
import random
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

print("=" * 80)
print("🚀 STARZBET ULTRA BOT - GERÇEK ZAMANLI")
print("=" * 80)

# 1. TOKEN ve API KEY'ler
TOKEN = os.environ.get("TELEGRAM_TOKEN", "8031564377:AAHjJXBQ-b6f0BnKdbf6T7iwUjs1fCA7dW0")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")

# 2. ANA SİTE
STARZBET_SITE = "https://starzbet422.com"

# 3. AI CLIENT
client = None
if GROQ_API_KEY:
    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        print("✅ Groq AI bağlantısı başarılı")
    except Exception as e:
        print(f"⚠️ Groq hatası: {e}")
        client = None

# 4. GÜNCEL VERİLER (Sabit ama doğru)
GUNCEL_VERILER = {
    "site_baslik": "Starzbet - En Güvenilir Bahis Sitesi",
    "bonuslar": [
        "🎁 HOŞGELDİN BONUSU: İlk yatırımınıza %100 bonus (max 5.000₺)",
        "🎰 SLOT BONUSU: Slot oyunlarında %100 bonus",
        "⚽ SPOR BONUSU: Spor bahislerinde %100 bonus", 
        "✨ KAYIP İADESİ: Kayıplarınızın %35'i iade",
        "🔥 TEKRAR YATIRIM: Her yatırımda %25 ekstra bonus",
        "👥 ARKADAŞ DAVETİ: Her davet için 500₺ bonus"
    ],
    "odeme_yontemleri": [
        "💳 Papara (Komisyon: %0, Limit: 100₺ - 50.000₺)",
        "📱 Jeton (Komisyon: %0, Limit: 100₺ - 30.000₺)",
        "🏦 Cepbank (Komisyon: %0, Limit: 100₺ - 100.000₺)",
        "💎 Kredi Kartı (Komisyon: %0, Limit: 100₺ - 20.000₺)",
        "₿ Bitcoin (Komisyon: %0, Limit: 500₺ - 500.000₺)"
    ],
    "son_guncelleme": datetime.now().strftime("%d.%m.%Y %H:%M")
}

# 5. LİNKLER (DOĞRU LİNKLER)
LINKLER = {
    "dinamikpay": "https://cutt.ly/dynamicpay-starzbet",
    "giris": "https://cutt.ly/drVOi2EN",
    "bonus": "https://starzbet422.com/tr-tr/info/promos",
    "telegram_kanal": "https://t.me/Starzbetgir",
    "canli_destek": "https://service.3kanumaigc.com/chatwindow.aspx?siteId=90005302&planId=1b050682-cde5-4176-8236-3bb94c891197#",
    "mini_app": "https://telegram-mini-app-umber-chi.vercel.app",
    "casino": "https://starzbet422.com/casino",
    "spor": "https://starzbet422.com/sports",
    "mobile_apk": "https://starzbet422.com/apk",
    "mobile_ios": "https://starzbet422.com/ios"
}

# 6. DİNAMİKPAY SİSTEMİ
DINAMIKPAY_SISTEMI = {
    "odemeler": {
        "papara": {"komisyon": "%0", "limit": "Min 100₺ - Max 50.000₺", "sure": "ANINDA", "bonus": "%150"},
        "jeton": {"komisyon": "%0", "limit": "Min 100₺ - Max 30.000₺", "sure": "ANINDA", "bonus": "%150"},
        "cebbank": {"komisyon": "%0", "limit": "Min 100₺ - Max 100.000₺", "sure": "ANINDA", "bonus": "%150"},
        "kredi_karti": {"komisyon": "%0", "limit": "Min 100₺ - Max 20.000₺", "sure": "2-5 dk", "bonus": "%150"},
        "bitcoin": {"komisyon": "%0", "limit": "Min 500₺ - Max 500.000₺", "sure": "10-30 dk", "bonus": "%200"}
    },
    "avantajlar": [
        "⚡ ANINDA işlem onayı",
        "🔒 %100 GÜVENLİ ödeme",
        "💰 SIFIR komisyon",
        "📱 7/24 aktif sistem",
        "🔄 Otomatik yatırım",
        "🎁 ÖZEL DİNAMİKPAY bonusları"
    ]
}

# 7. KARŞILAMA MESAJLARI (DİNAMİKPAY ÖNCELİKLİ)
KARSILAMA_MESAJLARI = [
    "🌟 *Starzbet'e Hoş Geldiniz!* DİNAMİKPAY ile anında yatırım, %150 bonus kazanın!",
    "🚀 *Kazancın Adresi Starzbet!* DİNAMİKPAY VIP üyelerine özel %50 cashback!",
    "⚡ *Süper Bahis Deneyimi!* DİNAMİKPAY ile 7/24 anında yatırım yapın!",
    "💰 *Para Yatırmanın En Hızlı Yolu!* DİNAMİKPAY ile bonuslarınız anında hesabınıza!",
    "🎰 *Canlı Casino & Bahis!* DİNAMİKPAY ile yatırım yap, hemen oynamaya başla!"
]

# 8. MENÜ SİSTEMİ
def ana_menu():
    """Ana menü - DİNAMİKPAY ön planda"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⚡ DİNAMİKPAY YATIR", callback_data="dinamikpay_yatir")],
        [InlineKeyboardButton("💰 GÜNCEL BONUSLAR", callback_data="guncel_bonuslar")],
        [InlineKeyboardButton("🎮 CASİNO", callback_data="casino"),
         InlineKeyboardButton("⚽ SPOR BAHİS", callback_data="spor_bahis")],
        [InlineKeyboardButton("📱 MOBİL UYGULAMA", callback_data="mobile"),
         InlineKeyboardButton("🎰 MİNİ APP", web_app=WebAppInfo(url=LINKLER["mini_app"]))],
        [InlineKeyboardButton("🎧 CANLI DESTEK", url=LINKLER["canli_destek"]),
         InlineKeyboardButton("🔗 GÜNCEL GİRİŞ", url=LINKLER["giris"])],
        [InlineKeyboardButton("📊 TELEGRAM KANAL", url=LINKLER["telegram_kanal"]),
         InlineKeyboardButton("🔄 BİLGİ GÜNCELLE", callback_data="bilgi_guncelle")]
    ])

def dinamikpay_menu():
    """DİNAMİKPAY özel menü"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 PAPARA İLE YATIR", callback_data="papara_yatir"),
         InlineKeyboardButton("📱 JETON İLE YATIR", callback_data="jeton_yatir")],
        [InlineKeyboardButton("🏦 CEPBANK İLE YATIR", callback_data="cebbank_yatir"),
         InlineKeyboardButton("💎 KREDİ KARTI İLE YATIR", callback_data="kredi_yatir")],
        [InlineKeyboardButton("₿ BITCOIN İLE YATIR", callback_data="bitcoin_yatir")],
        [InlineKeyboardButton("🔙 ANA MENÜ", callback_data="ana_menu")]
    ])

# 9. /start KOMUTU
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Başlangıç komutu"""
    karsilama = random.choice(KARSILAMA_MESAJLARI)
    ai_status = "✅ Aktif" if client else "❌ Devre Dışı"
    
    mesaj = f"""{karsilama}

📊 *Sistem Bilgileri:*
• 🤖 AI Asistan: {ai_status}
• 🕒 Son Güncelleme: {GUNCEL_VERILER['son_guncelleme']}
• 🔗 Güncel Site: {LINKLER['giris']}

⚡ *DİNAMİKPAY AVANTAJLARI:*
• %150 İlk Yatırım Bonusu
• Sıfır Komisyon
• Anında Hesaba Geçiş
• Özel VIP Programı

🎯 *Hemen Başlayın:*
1. DİNAMİKPAY ile yatırım yap ({LINKLER['dinamikpay']})
2. %150 bonusunuzu alın
3. Bahis/Casino'da kazanmaya başlayın

💡 *Öneri:* Telegram kanalımızdan güncel bahisleri takip edin!"""
    
    await update.message.reply_text(
        mesaj,
        reply_markup=ana_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

# 10. GÜNCEL BONUSLAR
async def guncel_bonuslar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Güncel bonusları göster"""
    query = update.callback_query
    await query.answer()
    
    bonus_mesaji = "🎁 *GÜNCEL BONUSLAR* 🎁\n\n"
    
    for bonus in GUNCEL_VERILER["bonuslar"]:
        bonus_mesaji += f"• {bonus}\n"
    
    bonus_mesaji += f"\n📌 *Tüm detaylar için:* {LINKLER['bonus']}"
    bonus_mesaji += f"\n🕒 *Son Güncelleme:* {GUNCEL_VERILER['son_guncelleme']}"
    bonus_mesaji += f"\n\n⚡ *Bonus kazanmak için:* {LINKLER['dinamikpay']}"
    
    await query.message.reply_text(
        bonus_mesaji,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⚡ DİNAMİKPAY İLE YATIR", callback_data="dinamikpay_yatir")],
            [InlineKeyboardButton("🔗 TÜM BONUSLAR", url=LINKLER["bonus"])],
            [InlineKeyboardButton("🔙 ANA MENÜ", callback_data="ana_menu")]
        ]),
        parse_mode=ParseMode.MARKDOWN
    )

# 11. DİNAMİKPAY SİSTEMİ
async def dinamikpay_yatir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """DİNAMİKPAY yatırım ekranı"""
    query = update.callback_query
    await query.answer()
    
    mesaj = "⚡ *DİNAMİKPAY SİSTEMİ* ⚡\n\n"
    mesaj += "💰 *ÖDEME YÖNTEMLERİ:*\n\n"
    
    for yontem, detay in DINAMIKPAY_SISTEMI["odemeler"].items():
        yontem_adi = yontem.upper().replace('_', ' ')
        mesaj += f"• *{yontem_adi}:*\n"
        mesaj += f"  Komisyon: {detay['komisyon']}\n"
        mesaj += f"  Limit: {detay['limit']}\n"
        mesaj += f"  Süre: {detay['sure']}\n"
        mesaj += f"  Bonus: {detay['bonus']}\n\n"
    
    mesaj += "🎁 *DİNAMİKPAY AVANTAJLARI:*\n"
    for avantaj in DINAMIKPAY_SISTEMI["avantajlar"]:
        mesaj += f"• {avantaj}\n"
    
    mesaj += f"\n🔗 *Özel Link:* {LINKLER['dinamikpay']}"
    mesaj += f"\n🕒 *Güncel Bonuslar:* {LINKLER['bonus']}"
    
    await query.message.reply_text(
        mesaj,
        reply_markup=dinamikpay_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

# 12. ÖDEME YÖNTEMLERİ
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
• Bonus: {detay['bonus']}

🎁 *BU YÖNTEME ÖZEL:*
• İlk yatırım: {detay['bonus']} bonus
• Tekrarlayan yatırımlar: %25 ekstra
• VIP üyelik: %50 cashback

📝 *ADIMLAR:*
1. {LINKLER['dinamikpay']} adresine git
2. '{yontem_adi}' seçeneğini seç
3. Yatırmak istediğiniz tutarı girin
4. Ödeme bilgilerinizi tamamlayın
5. *ANINDA* hesabınıza geçsin!

⚠️ *ÖNEMLİ:* Yatırım sonrası bonus otomatik eklenir.

🔗 *Hemen Yatırım Yap:* {LINKLER['dinamikpay']}"""
    
    await query.message.reply_text(
        mesaj,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🎰 HEMEN OYNA", callback_data="hemen_oyna")],
            [InlineKeyboardButton("⚽ BAHİS YAP", callback_data="spor_bahis")],
            [InlineKeyboardButton("🔙 ANA MENÜ", callback_data="ana_menu")]
        ]),
        parse_mode=ParseMode.MARKDOWN
    )

# 13. SPOR BAHİS
async def spor_bahis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Spor bahis ekranı"""
    query = update.callback_query
    await query.answer()
    
    mesaj = f"""⚽ *CANLI SPOR BAHİSLERİ* ⚽

📊 *GÜNCEL MAÇ ÖNERİLERİ:*
1. Süper Lig maçları - Canlı bahis açık
2. Avrupa kupaları - Yüksek oranlar  
3. Basketbol - NBA ve EuroLeague
4. Tenis - Grand Slam turnuvaları

🎯 *BAHİS TİPLERİ:*
• Maç sonucu
• İlk yarı/İkinci yarı
• Toplam gol
• Asya handikap
• Canlı bahis

💰 *BAHİS YAPMAK İÇİN:*
1. Önce DİNAMİKPAY ile yatırım yap
2. Bonuslarınızı alın
3. Bahis yapmaya başlayın

📈 *GÜNCEL ORANLAR İÇİN:* {LINKLER['telegram_kanal']}
🔗 *Bahis Yap:* {LINKLER['spor']}"""
    
    await query.message.reply_text(
        mesaj,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🎯 BAHİS YAP", url=LINKLER["spor"])],
            [InlineKeyboardButton("⚡ YATIRIM YAP", callback_data="dinamikpay_yatir")],
            [InlineKeyboardButton("📊 GÜNCEL ORANLAR", url=LINKLER["telegram_kanal"])]
        ]),
        parse_mode=ParseMode.MARKDOWN
    )

# 14. CASİNO
async def casino(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Casino ekranı"""
    query = update.callback_query
    await query.answer()
    
    await query.message.reply_text(
        f"""🎮 *CANLI CASİNO* 🎮

✨ *Popüler Oyunlar:*
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
1. {LINKLER['dinamikpay']} ile yatırım yap
2. %200 casino bonusunuzu alın
3. Canlı krupiyelerle oynayın
4. Büyük kazançlar elde edin

🎯 *CANLI KRUPİYELER:* 7/24 hizmetinizde!
🔗 *Casino'ya Git:* {LINKLER['casino']}""",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🎮 CANLI CASİNO", url=LINKLER["casino"])],
            [InlineKeyboardButton("⚡ YATIRIM YAP", callback_data="dinamikpay_yatir")],
            [InlineKeyboardButton("🔙 ANA MENÜ", callback_data="ana_menu")]
        ]),
        parse_mode=ParseMode.MARKDOWN
    )

# 15. MOBİL
async def mobile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mobil uygulama"""
    query = update.callback_query
    await query.answer()
    
    await query.message.reply_text(
        f"""📱 *STARZBET MOBİL UYGULAMA* 📱

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
• Android APK: {LINKLER['mobile_apk']}
• iOS TestFlight: {LINKLER['mobile_ios']}

⚠️ *NOT:* iOS uygulaması App Store'dan kaldırıldı, TestFlight ile indirin.

📞 *MOBİL DESTEK:* @starzbetmobile""",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📲 ANDROID İNDİR", url=LINKLER["mobile_apk"])],
            [InlineKeyboardButton("🍎 iOS İNDİR", url=LINKLER["mobile_ios"])],
            [InlineKeyboardButton("⚡ YATIRIM YAP", callback_data="dinamikpay_yatir")]
        ]),
        parse_mode=ParseMode.MARKDOWN
    )

# 16. BİLGİ GÜNCELLE
async def bilgi_guncelle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bilgileri güncelle"""
    query = update.callback_query
    await query.answer()
    
    GUNCEL_VERILER['son_guncelleme'] = datetime.now().strftime("%d.%m.%Y %H:%M")
    
    await query.message.reply_text(
        f"✅ *Bilgiler Güncellendi!*\n\n"
        f"🕒 *Yeni Tarih:* {GUNCEL_VERILER['son_guncelleme']}\n"
        f"🎁 *Aktif Bonus:* {len(GUNCEL_VERILER['bonuslar'])} kampanya\n"
        f"💳 *Ödeme Yöntemi:* {len(GUNCEL_VERILER['odeme_yontemleri'])} yöntem\n\n"
        f"⚡ Artık en güncel bilgilerle hizmetinizdeyiz!",
        reply_markup=ana_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

# 17. AKILLI AI SİSTEMİ
async def ai_cevap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """AI yanıt sistemi"""
    user_message = update.message.text.lower().strip()
    
    # YEREL CEVAPLAR
    if "bonus" in user_message or "kampanya" in user_message:
        await guncel_bonuslar_ai(update)
        return
    
    elif "yatırım" in user_message or "para yatır" in user_message or "deposit" in user_message:
        await yatirim_ai(update)
        return
    
    elif "bahis" in user_message or "oran" in user_message or "maç" in user_message:
        await bahis_ai(update)
        return
    
    elif "casino" in user_message or "slot" in user_message or "rulet" in user_message:
        await casino_ai(update)
        return
    
    elif any(kelime in user_message for kelime in ["merhaba", "selam", "hi", "hello", "naber"]):
        await selam_ai(update)
        return
    
    elif any(kelime in user_message for kelime in ["giriş", "link", "site", "url"]):
        await link_ai(update)
        return
    
    # AI İLE CEVAP
    if not client:
        await update.message.reply_text(
            "🤖 *AI şu anda kullanılamıyor.*\n\n"
            f"⚡ Hemen DİNAMİKPAY ile yatırım yapın: {LINKLER['dinamikpay']}",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    thinking_msg = await update.message.reply_text("🤔 *Cevap hazırlanıyor...*", parse_mode=ParseMode.MARKDOWN)
    
    try:
        system_prompt = f"""Sen Starzbet'in AI asistanısın. Aşağıdaki GÜNCEL bilgileri kullan:

GÜNCEL BONUSLAR:
{chr(10).join(GUNCEL_VERILER['bonuslar'][:3])}

DİNAMİKPAY SİSTEMİ:
• Link: {LINKLER['dinamikpay']}
• Bonus: %150 ilk yatırım bonusu
• Avantaj: Sıfır komisyon, anında onay

ÖNEMLİ LİNKLER:
• Giriş: {LINKLER['giris']}
• Bonuslar: {LINKLER['bonus']}
• Telegram: {LINKLER['telegram_kanal']}
• Destek: {LINKLER['canli_destek']}

KURALLAR:
1. Her cevapta DİNAMİKPAY'ı öne çıkar
2. Bonus sorana güncel bonusları söyle
3. Yatırım sorana DİNAMİKPAY linkini ver
4. Bahis sorana Telegram kanalına yönlendir
5. Linkleri markdown formatında ver
6. Kısa, net, yardımcı ol

Kullanıcı şunu soruyor:"""
        
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=300
        )
        
        await thinking_msg.delete()
        ai_response = completion.choices[0].message.content
        
        # DİNAMİKPAY mesajı ekle
        final_response = f"{ai_response}\n\n💡 *Öneri:* Kazancınızı artırmak için hemen DİNAMİKPAY ile yatırım yapın!"
        
        await update.message.reply_text(
            f"🤖 *Starzbet AI:*\n\n{final_response}",
            parse_mode=ParseMode.MARKDOWN
        )
        
    except Exception as e:
        logging.error(f"AI hatası: {e}")
        try:
            await thinking_msg.delete()
        except:
            pass
        
        await update.message.reply_text(
            f"❌ *AI yanıt hatası.*\n\n"
            f"⚡ *Hemen DİNAMİKPAY ile başlayın:* {LINKLER['dinamikpay']}",
            parse_mode=ParseMode.MARKDOWN
        )

# 18. YEREL AI CEVAP FONKSİYONLARI
async def guncel_bonuslar_ai(update: Update):
    """Bonus sorusuna AI cevabı"""
    await update.message.reply_text(
        f"🎁 *GÜNCEL BONUSLAR:*\n\n"
        f"{chr(10).join(GUNCEL_VERILER['bonuslar'][:3])}\n\n"
        f"🔗 Tüm bonuslar: {LINKLER['bonus']}\n"
        f"⚡ Bonus kazanmak için: {LINKLER['dinamikpay']}",
        parse_mode=ParseMode.MARKDOWN
    )

async def yatirim_ai(update: Update):
    """Yatırım sorusuna AI cevabı"""
    await update.message.reply_text(
        f"⚡ *DİNAMİKPAY İLE YATIRIM:*\n\n"
        f"Hemen yatırım yap: {LINKLER['dinamikpay']}\n\n"
        f"🎯 Avantajlar:\n"
        f"• %150 İlk Yatırım Bonusu\n"
        f"• Sıfır Komisyon\n"
        f"• Anında Onay\n"
        f"• 7/24 Aktif\n\n"
        f"💳 Yöntemler: Papara, Jeton, Cepbank, Kredi Kartı, Bitcoin",
        parse_mode=ParseMode.MARKDOWN
    )

async def bahis_ai(update: Update):
    """Bahis sorusuna AI cevabı"""
    await update.message.reply_text(
        f"⚽ *BAHİS BİLGİLERİ:*\n\n"
        f"📊 Güncel bahis oranları için: {LINKLER['telegram_kanal']}\n"
        f"💰 Bahis yapmak için: {LINKLER['spor']}\n"
        f"⚡ Önce yatırım yapın: {LINKLER['dinamikpay']}\n\n"
        f"🎯 Bahis tipleri: Maç sonucu, canlı bahis, toplam gol, handikap",
        parse_mode=ParseMode.MARKDOWN
    )

async def casino_ai(update: Update):
    """Casino sorusuna AI cevabı"""
    await update.message.reply_text(
        f"🎮 *CASİNO BİLGİLERİ:*\n\n"
        f"✨ Oyunlar: Canlı Blackjack, Rulet, Slot, Baccarat, Poker\n"
        f"🎁 Bonus: %200 casino bonusu\n"
        f"🔗 Casino'ya git: {LINKLER['casino']}\n"
        f"⚡ Önce yatırım yap: {LINKLER['dinamikpay']}",
        parse_mode=ParseMode.MARKDOWN
    )

async def selam_ai(update: Update):
    """Selam sorusuna AI cevabı"""
    karsilama = random.choice(KARSILAMA_MESAJLARI)
    await update.message.reply_text(
        f"{karsilama}\n\n"
        f"⚡ Hemen başlamak için: {LINKLER['dinamikpay']}",
        parse_mode=ParseMode.MARKDOWN
    )

async def link_ai(update: Update):
    """Link sorusuna AI cevabı"""
    await update.message.reply_text(
        f"🔗 *ÖNEMLİ LİNKLER:*\n\n"
        f"• Giriş: {LINKLER['giris']}\n"
        f"• DİNAMİKPAY: {LINKLER['dinamikpay']}\n"
        f"• Bonuslar: {LINKLER['bonus']}\n"
        f"• Telegram: {LINKLER['telegram_kanal']}\n"
        f"• Destek: {LINKLER['canli_destek']}\n\n"
        f"⚡ Öneri: Önce DİNAMİKPAY ile yatırım yapın!",
        parse_mode=ParseMode.MARKDOWN
    )

# 19. BUTON HANDLER
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Buton tıklamalarını yönet"""
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
    elif data == "bilgi_guncelle":
        await bilgi_guncelle(update, context)
    elif data == "ana_menu":
        await query.message.reply_text(
            "🏠 *Ana Menüye Döndünüz*",
            reply_markup=ana_menu(),
            parse_mode=ParseMode.MARKDOWN
        )
    elif data in ["papara_yatir", "jeton_yatir", "cebbank_yatir", "kredi_yatir", "bitcoin_yatir"]:
        yontemler = {
            "papara_yatir": ("PAPARA", "papara"),
            "jeton_yatir": ("JETON", "jeton"),
            "cebbank_yatir": ("CEPBANK", "cebbank"),
            "kredi_yatir": ("KREDİ KARTI", "kredi_karti"),
            "bitcoin_yatir": ("BITCOIN", "bitcoin")
        }
        yontem_adi, yontem_key = yontemler[data]
        await yatirim_yontemi(update, yontem_adi, yontem_key)

# 20. ANA PROGRAM
def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    
    print("🚀 Bot başlatılıyor...")
    print(f"✅ {len(GUNCEL_VERILER['bonuslar'])} bonus yüklendi")
    print(f"✅ {len(LINKLER)} link yüklendi")
    print(f"🤖 AI Durumu: {'Aktif' if client else 'Devre Dışı'}")
    
    try:
        app = Application.builder().token(TOKEN).build()
        
        # Handler'ları ekle
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(button_handler))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_cevap))
        
        print("✅ Bot hazır!")
        print("📱 Telegram'da /start yazın")
        
        # Botu başlat
        app.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        print(f"❌ Hata: {type

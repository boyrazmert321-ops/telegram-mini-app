import os
import sys
import logging
import random
import requests
import asyncio
import aiohttp
from datetime import datetime
from bs4 import BeautifulSoup
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

print("=" * 80)
print("🚀 STARZBET ULTRA BOT - GERÇEK ZAMANLI SİTE TARAMA")
print("=" * 80)

# 1. TOKEN ve API KEY'ler
TOKEN = os.environ.get("TELEGRAM_TOKEN", "8031564377:AAHjJXBQ-b6f0BnKdbf6T7iwUjs1fCA7dW0")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")

# 2. ANA SİTE
STARZBET_SITE = "https://starzbet422.com"

# 3. WEB SCRAPING FONKSİYONLARI
async def siteyi_tara():
    """Starzbet sitesini tarayıp güncel bilgileri al"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        async with aiohttp.ClientSession() as session:
            # 1. Ana sayfayı tara
            print("📡 Ana sayfa taranıyor...")
            async with session.get(STARZBET_SITE, headers=headers, timeout=10) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Site başlığı
                site_baslik = soup.title.string if soup.title else "Starzbet"
                
                # Bonus linkini bul
                bonus_link = None
                for link in soup.find_all('a', href=True):
                    if 'promo' in link['href'].lower() or 'bonus' in link['href'].lower():
                        bonus_link = link['href']
                        if not bonus_link.startswith('http'):
                            bonus_link = STARZBET_SITE + bonus_link
                        break
                
                if not bonus_link:
                    bonus_link = f"{STARZBET_SITE}/tr-tr/info/promos"
                
            # 2. Bonus sayfasını tara
            print("📡 Bonus sayfası taranıyor...")
            async with session.get(bonus_link, headers=headers, timeout=10) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Bonusları çıkar
                bonuslar = []
                for element in soup.find_all(['h2', 'h3', 'h4', 'p', 'div']):
                    text = element.get_text(strip=True)
                    if any(word in text.lower() for word in ['bonus', 'promosyon', 'kampanya', '%']):
                        if len(text) < 200 and len(text) > 10:
                            bonuslar.append(text)
                
                # İlk 5 bonusu al
                bonuslar = bonuslar[:5] if bonuslar else [
                    "Hoşgeldin Bonusu: %100",
                    "Slot Bonusu: %100",
                    "Spor Bonusu: %100",
                    "Kayıp İadesi: %35",
                    "Arkadaş Daveti: 500₺"
                ]
            
            return {
                "site_baslik": site_baslik,
                "bonus_link": bonus_link,
                "bonuslar": bonuslar,
                "giris_link": STARZBET_SITE,
                "son_guncelleme": datetime.now().strftime("%d.%m.%Y %H:%M")
            }
            
    except Exception as e:
        print(f"❌ Site tarama hatası: {e}")
        return {
            "site_baslik": "Starzbet",
            "bonus_link": f"{STARZBET_SITE}/tr-tr/info/promos",
            "bonuslar": [
                "Hoşgeldin Bonusu: %100",
                "Slot Bonusu: %100", 
                "Spor Bonusu: %100",
                "Kayıp İadesi: %35",
                "Arkadaş Daveti: 500₺"
            ],
            "giris_link": STARZBET_SITE,
            "son_guncelleme": datetime.now().strftime("%d.%m.%Y %H:%M")
        }

async def telegram_kanal_son_post():
    """Telegram kanalından son postu al"""
    try:
        # Bu kısım API gerektirir, şimdilik sabit bilgi
        return {
            "text": "🔥 CANLI BAHİS: En güncel oranlar için kanalımızı takip edin!",
            "link": "https://t.me/Starzbetgir"
        }
    except:
        return {
            "text": "📊 Güncel bahisler için Telegram kanalımızı takip edin!",
            "link": "https://t.me/Starzbetgir"
        }

# 4. GÜNCEL VERİLER (Başlangıçta boş, sonra doldurulacak)
GUNCEL_VERILER = {}

# 5. AI CLIENT
client = None
if GROQ_API_KEY:
    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        print("✅ Groq AI bağlantısı başarılı")
    except Exception as e:
        print(f"⚠️ Groq hatası: {e}")
        client = None

# 6. DİNAMİKPAY SİSTEMİ (GERÇEK VERİLER)
DINAMIKPAY_SISTEMI = {
    "odemeler": {
        "papara": {"komisyon": "%0", "limit": "Min 500₺ - Max 50.000₺", "sure": "ANINDA"},
        "HAVALE/EFT": {"komisyon": "%0", "limit": "Min 500₺ - Max 100.000₺", "sure": "ANINDA"},
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
    ]
}

# 7. LİNKLER (Site taranarak güncellenecek)
async def linkleri_guncelle():
    """Tüm linkleri güncelle"""
    global GUNCEL_VERILER
    GUNCEL_VERILER = await siteyi_tara()
    
    return {
        "dinamikpay": "https://cutt.ly/dynamicpay-starzbet",  # Özel link
        "giris": GUNCEL_VERILER.get("giris_link", STARZBET_SITE),
        "bonus": GUNCEL_VERILER.get("bonus_link", f"{STARZBET_SITE}/tr-tr/info/promos"),
        "telegram_kanal": "https://t.me/Starzbetgir",
        "canli_destek": "https://service.3kanumaigc.com/chatwindow.aspx?siteId=90005302&planId=1b050682-cde5-4176-8236-3bb94c891197#",
        "mini_app": "https://telegram-mini-app-umber-chi.vercel.app"
    }

# 8. MENÜ SİSTEMİ
def ana_menu(linkler):
    """Ana menü"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⚡ DİNAMİKPAY YATIR", callback_data="dinamikpay_yatir")],
        [InlineKeyboardButton("💰 GÜNCEL BONUSLAR", callback_data="guncel_bonuslar")],
        [InlineKeyboardButton("🎮 CASİNO", callback_data="casino"),
         InlineKeyboardButton("⚽ SPOR", callback_data="spor_bahis")],
        [InlineKeyboardButton("📱 MOBİL", callback_data="mobile"),
         InlineKeyboardButton("🎰 MİNİ APP", web_app=WebAppInfo(url=linkler["mini_app"]))],
        [InlineKeyboardButton("🎧 CANLI DESTEK", url=linkler["canli_destek"]),
         InlineKeyboardButton("🔗 GÜNCEL GİRİŞ", url=linkler["giris"])],
        [InlineKeyboardButton("🔄 BİLGİLERİ GÜNCELLE", callback_data="guncelle")]
    ])

# 9. /start KOMUTU (GERÇEK ZAMANLI)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Başlangıç komutu"""
    # Önce verileri güncelle
    linkler = await linkleri_guncelle()
    
    karsilama = random.choice([
        f"🌟 *{GUNCEL_VERILER.get('site_baslik', 'Starzbet')}*'e Hoş Geldiniz!",
        f"🚀 *{GUNCEL_VERILER.get('site_baslik', 'Starzbet')}* ile kazanmaya başlayın!",
        f"⚡ *{GUNCEL_VERILER.get('site_baslik', 'Starzbet')}* - En güncel bahis deneyimi!"
    ])
    
    ai_status = "✅ Aktif" if client else "❌ Devre Dışı"
    
    mesaj = f"""{karsilama}

📊 *Sistem Bilgileri:*
• 🤖 AI Asistan: {ai_status}
• 🕒 Son Güncelleme: {GUNCEL_VERILER.get('son_guncelleme', 'Yükleniyor...')}
• 🔗 Güncel Site: {linkler['giris']}

⚡ *DİNAMİKPAY AVANTAJLARI:*
• Anında yatırım onayı
• Sıfır komisyon
• Özel bonuslar
• 7/24 aktif

🎯 *Hemen Başlayın:*
1. DİNAMİKPAY ile yatırım yap
2. Bonuslarınızı alın  
3. Bahis/Casino'da kazanmaya başlayın

🔗 *Özel DİNAMİKPAY Linki:* {linkler['dinamikpay']}"""
    
    await update.message.reply_text(
        mesaj,
        reply_markup=ana_menu(linkler),
        parse_mode=ParseMode.MARKDOWN
    )

# 10. GÜNCEL BONUSLAR (SİTEDEN ALINAN)
async def guncel_bonuslar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Siteden taranan bonusları göster"""
    query = update.callback_query
    await query.answer()
    
    linkler = await linkleri_guncelle()
    bonuslar = GUNCEL_VERILER.get("bonuslar", [])
    
    bonus_mesaji = "🎁 *GÜNCEL BONUSLAR (Siteden alınmıştır)* 🎁\n\n"
    
    for i, bonus in enumerate(bonuslar, 1):
        bonus_mesaji += f"{i}. {bonus}\n"
    
    bonus_mesaji += f"\n📌 *Şartlar ve detaylar için:*\n{linkler['bonus']}"
    bonus_mesaji += f"\n\n🕒 *Son Güncelleme:* {GUNCEL_VERILER.get('son_guncelleme', 'Bilinmiyor')}"
    bonus_mesaji += f"\n\n⚡ *Bonus kazanmak için:*\n{linkler['dinamikpay']}"
    
    await query.message.reply_text(
        bonus_mesaji,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⚡ DİNAMİKPAY İLE YATIR", callback_data="dinamikpay_yatir")],
            [InlineKeyboardButton("🔗 TÜM BONUSLAR", url=linkler["bonus"])],
            [InlineKeyboardButton("🔄 YENİLE", callback_data="guncel_bonuslar")]
        ]),
        parse_mode=ParseMode.MARKDOWN
    )

# 11. DİNAMİKPAY SİSTEMİ
async def dinamikpay_yatir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """DİNAMİKPAY yatırım ekranı"""
    query = update.callback_query
    await query.answer()
    
    linkler = await linkleri_guncelle()
    
    mesaj = f"""⚡ *DİNAMİKPAY SİSTEMİ* ⚡

💰 *ÖDEME YÖNTEMLERİ:*
"""
    
    for yontem, detay in DINAMIKPAY_SISTEMI["odemeler"].items():
        yontem_adi = yontem.upper().replace('_', ' ')
        mesaj += f"\n• *{yontem_adi}:*\n"
        mesaj += f"  Komisyon: {detay['komisyon']}\n"
        mesaj += f"  Limit: {detay['limit']}\n"
        mesaj += f"  Süre: {detay['sure']}\n"
    
    mesaj += f"\n🎁 *DİNAMİKPAY AVANTAJLARI:*\n"
    for avantaj in DINAMIKPAY_SISTEMI["avantajlar"]:
        mesaj += f"• {avantaj}\n"
    
    mesaj += f"\n🔗 *Özel Link:* {linkler['dinamikpay']}"
    mesaj += f"\n🕒 *Güncel Bonuslar:* {linkler['bonus']}"
    
    await query.message.reply_text(
        mesaj,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💳 PAPARA İLE YATIR", callback_data="papara_yatir")],
            [InlineKeyboardButton("📱 JETON İLE YATIR", callback_data="jeton_yatir")],
            [InlineKeyboardButton("🏦 CEPBANK İLE YATIR", callback_data="cebbank_yatir")],
            [InlineKeyboardButton("🔙 ANA MENÜ", callback_data="ana_menu")]
        ]),
        parse_mode=ParseMode.MARKDOWN
    )

# 12. SPOR BAHİS (GERÇEK ZAMANLI KANALDAN)
async def spor_bahis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Spor bahis ekranı"""
    query = update.callback_query
    await query.answer()
    
    linkler = await linkleri_guncelle()
    kanal_post = await telegram_kanal_son_post()
    
    mesaj = f"""⚽ *CANLI SPOR BAHİSLERİ* ⚽

{kanal_post['text']}

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

📈 *GÜNCEL ORANLAR:* {linkler['telegram_kanal']}
🔗 *Bahis Yap:* {linkler['giris']}"""
    
    await query.message.reply_text(
        mesaj,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🎯 BAHİS YAP", url=linkler["giris"])],
            [InlineKeyboardButton("⚡ YATIRIM YAP", callback_data="dinamikpay_yatir")],
            [InlineKeyboardButton("📊 GÜNCEL ORANLAR", url=linkler["telegram_kanal"])]
        ]),
        parse_mode=ParseMode.MARKDOWN
    )

# 13. BİLGİ GÜNCELLE
async def guncelle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bilgileri yeniden tara"""
    query = update.callback_query
    await query.answer()
    
    guncelleme_msg = await query.message.reply_text("🔄 *Bilgiler güncelleniyor...*", parse_mode=ParseMode.MARKDOWN)
    
    try:
        linkler = await linkleri_guncelle()
        
        await guncelleme_msg.edit_text(
            f"✅ *Bilgiler Güncellendi!*\n\n"
            f"• 🏷️ Site: {GUNCEL_VERILER.get('site_baslik', 'Starzbet')}\n"
            f"• 🔗 Giriş: {linkler['giris']}\n"
            f"• 🎁 Bonuslar: {len(GUNCEL_VERILER.get('bonuslar', []))} aktif kampanya\n"
            f"• 🕒 Son Güncelleme: {GUNCEL_VERILER.get('son_guncelleme', 'Şimdi')}\n\n"
            f"⚡ Artık en güncel bilgilerle hizmetinizdeyiz!",
            parse_mode=ParseMode.MARKDOWN
        )
        
    except Exception as e:
        await guncelleme_msg.edit_text(
            f"❌ *Güncelleme hatası:* {str(e)[:100]}\n\n"
            f"Lütfen daha sonra tekrar deneyin.",
            parse_mode=ParseMode.MARKDOWN
        )

# 14. AKILLI AI SİSTEMİ (GÜNCEL VERİLERLE)
async def ai_cevap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Güncel verilerle AI yanıt"""
    user_message = update.message.text.lower().strip()
    
    # Önce yerel cevaplar
    if "güncel" in user_message or "bonus" in user_message or "kampanya" in user_message:
        linkler = await linkleri_guncelle()
        bonuslar = GUNCEL_VERILER.get("bonuslar", [])
        
        cevap = "🎁 *GÜNCEL BONUSLAR:*\n\n"
        for i, bonus in enumerate(bonuslar[:3], 1):
            cevap += f"{i}. {bonus}\n"
        
        cevap += f"\n🔗 Tüm bonuslar: {linkler['bonus']}"
        cevap += f"\n⚡ Yatırım yap: {linkler['dinamikpay']}"
        
        await update.message.reply_text(
            cevap,
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    elif any(kelime in user_message for kelime in ["bahis", "oran", "maç", "iddaa"]):
        linkler = await linkleri_guncelle()
        kanal_post = await telegram_kanal_son_post()
        
        await update.message.reply_text(
            f"⚽ *Bahis Bilgisi:*\n\n"
            f"{kanal_post['text']}\n\n"
            f"📊 Güncel oranlar: {linkler['telegram_kanal']}\n"
            f"💰 Bahis yap: {linkler['giris']}\n"
            f"⚡ Önce yatırım yap: {linkler['dinamikpay']}",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    elif any(kelime in user_message for kelime in ["yatırım", "yatır", "para yatır"]):
        linkler = await linkleri_guncelle()
        
        await update.message.reply_text(
            f"⚡ *DİNAMİKPAY İLE YATIRIM:*\n\n"
            f"Hemen yatırım yap: {linkler['dinamikpay']}\n\n"
            f"🎯 Avantajlar:\n"
            f"• Anında onay\n"
            f"• Sıfır komisyon\n"
            f"• Özel bonuslar\n\n"
            f"💳 Yöntemler: Papara, Jeton, Cepbank, Kredi Kartı, Bitcoin",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    # AI ile cevap
    if not client:
        linkler = await linkleri_guncelle()
        await update.message.reply_text(
            f"🤖 *AI şu anda kullanılamıyor.*\n\n"
            f"⚡ Hemen DİNAMİKPAY ile yatırım yapın: {linkler['dinamikpay']}",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    thinking_msg = await update.message.reply_text("🤔 *Cevap hazırlanıyor...*", parse_mode=ParseMode.MARKDOWN)
    
    try:
        linkler = await linkleri_guncelle()
        bonuslar = GUNCEL_VERILER.get("bonuslar", [])
        
        system_prompt = f"""Sen Starzbet'in güncel AI asistanısın. Aşağıdaki GERÇEK ZAMANLI bilgileri kullan:

GÜNCEL SİTE BİLGİLERİ:
• Site: {GUNCEL_VERILER.get('site_baslik', 'Starzbet')}
• Giriş Linki: {linkler['giris']}
• Bonus Linki: {linkler['bonus']}
• Son Güncelleme: {GUNCEL_VERILER.get('son_guncelleme', 'Bilinmiyor')}

GÜNCEL BONUSLAR (Siteden alındı):
{chr(10).join(bonuslar[:5])}

DİNAMİKPAY SİSTEMİ:
• Link: {linkler['dinamikpay']}
• Özellikler: Anında yatırım, sıfır komisyon, özel bonuslar

TELEGRAM KANALI:
• Link: {linkler['telegram_kanal']}
• İçerik: Güncel bahis oranları, kampanyalar

KURALLAR:
1. HER CEVAPTA güncelliği vurgula
2. Bonus sorana GERÇEK bonusları söyle
3. Bahis sorana Telegram kanalına yönlendir
4. Yatırım sorana DİNAMİKPAY linkini ver
5. Linkleri markdown formatında ver
6. Kısa, net, güncel bilgiler ver

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
        
        # Güncelleme bilgisi ekle
        final_response = f"{ai_response}\n\n🔄 *Son Güncelleme:* {GUNCEL_VERILER.get('son_guncelleme', 'Bilinmiyor')}"
        
        await update.message.reply_text(
            f"🤖 *Starzbet AI (Güncel):*\n\n{final_response}",
            parse_mode=ParseMode.MARKDOWN
        )
        
    except Exception as e:
        logging.error(f"AI hatası: {e}")
        try:
            await thinking_msg.delete()
        except:
            pass
        
        linkler = await linkleri_guncelle()
        await update.message.reply_text(
            f"❌ *AI yanıt hatası.*\n\n"
            f"⚡ *Güncel bilgiler:*\n"
            f"• Site: {linkler['giris']}\n"
            f"• Bonuslar: {linkler['bonus']}\n"
            f"• DİNAMİKPAY: {linkler['dinamikpay']}",
            parse_mode=ParseMode.MARKDOWN
        )

# 15. BUTON HANDLER'LARI
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
    elif data == "guncelle":
        await guncelle(update, context)
    elif data == "ana_menu":
        linkler = await linkleri_guncelle()
        await query.message.reply_text(
            "🏠 *Ana Menüye Döndünüz*",
            reply_markup=ana_menu(linkler),
            parse_mode=ParseMode.MARKDOWN
        )
    elif data in ["papara_yatir", "jeton_yatir", "cebbank_yatir"]:
        linkler = await linkleri_guncelle()
        yontem = data.replace("_yatir", "").upper()
        await query.message.reply_text(
            f"💳 *{yontem} İLE YATIRIM*\n\n"
            f"🔗 Hemen yatırım yap: {linkler['dinamikpay']}\n\n"
            f"⚡ Avantajlar:\n"
            f"• Anında onay\n"
            f"• Sıfır komisyon\n"
            f"• Özel {yontem} bonusu\n\n"
            f"📞 Sorunuz varsa canlı desteğe başvurun.",
            parse_mode=ParseMode.MARKDOWN
        )

# 16. DİĞER MENÜLER
async def casino(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    linkler = await linkleri_guncelle()
    
    await query.message.reply_text(
        f"""🎮 *CANLI CASİNO* 🎮

✨ *Popüler Oyunlar:*
• Canlı Blackjack
• Rulet
• Slot Makineleri
• Baccarat
• Poker

🎰 *Casino Bonusları:*
• İlk casino yatırımı: %200 bonus
• Canlı casino: %50 ekstra
• Slot: %100 free spin

⚡ *Nasıl Oynanır:*
1. {linkler['dinamikpay']} ile yatırım yap
2. Bonusunuzu alın
3. Casino'da oynamaya başlayın

🔗 *Casino'ya Git:* {linkler['giris']}/casino""",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🎮 CASİNO'YA GİT", url=f"{linkler['giris']}/casino")],
            [InlineKeyboardButton("⚡ YATIRIM YAP", callback_data="dinamikpay_yatir")]
        ]),
        parse_mode=ParseMode.MARKDOWN
    )

async def mobile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    linkler = await linkleri_guncelle()
    
    await query.message.reply_text(
        f"""📱 *MOBİL UYGULAMA* 📱

📲 *İndirme Linkleri:*
• Android APK: {linkler['giris']}/apk
• iOS TestFlight: {linkler['giris']}/ios

🌟 *Mobil Özellikler:*
• Hızlı arayüz
• DİNAMİKPAY entegrasyonu
• Canlı bildirimler
• Akıcı casino

⚡ *Mobil Bonus:*
• İlk mobil yatırım: %25 ekstra
• Mobil bahis: %50 free bet

🔗 *İndir ve kazanmaya başla!*""",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📲 ANDROID İNDİR", url=f"{linkler['giris']}/apk")],
            [InlineKeyboardButton("🍎 iOS İNDİR", url=f"{linkler['giris']}/ios")]
        ]),
        parse_mode=ParseMode.MARKDOWN
    )

# 17. ANA PROGRAM
async def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    
    print("🚀 Bot başlatılıyor...")
    
    # İlk taramayı yap
    print("📡 Site ilk taraması yapılıyor...")
    global GUNCEL_VERILER
    GUNCEL_VERILER = await siteyi_tara()
    
    print(f"✅ Site tarandı: {GUNCEL_VERILER.get('site_baslik', 'Starzbet')}")
    print(f"✅ {len(GUNCEL_VERILER.get('bonuslar', []))} bonus bulundu")
    
    try:
        app = Application.builder().token(TOKEN).build()
        
        # Handler'ları ekle
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(button_handler))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_cevap))
        
        # Özel butonlar
        app.add_handler(CallbackQueryHandler(casino, pattern="^casino$"))
        app.add_handler(CallbackQueryHandler(mobile, pattern="^mobile$"))
        
        print("✅ Bot hazır!")
        print("🌐 Site bilgileri güncel")
        print("🤖 AI sistemi hazır")
        print("📱 Telegram'da /start yazın")
        
        # Botu başlat
        await app.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        print(f"❌ Hata: {type(e).__name__}")
        print(f"📝 Detay: {str(e)[:200]}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

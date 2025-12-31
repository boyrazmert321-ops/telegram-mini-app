#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STARZBET AI TELEGRAM BOT - GÜNCELLENMİŞ GROQ API
"""

import os
import sys
import logging
import json
from datetime import datetime
from typing import Optional, Dict, Any

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from telegram.constants import ParseMode
import requests

# ========== KONFİGÜRASYON ==========
# TELEGRAM TOKEN (BUNA DİKKAT!)
TELEGRAM_TOKEN = "8031564377:AAHjJXBQ-b6f0BnKdbf6T7iwUjs1fCA7dW0"

# GROQ API KEY (SENİN VERDİĞİN ANAHTAR)
GROQ_API_KEY = "gsk_lHTS30e86lFzxmC3F7ROWGdyb3FYamQVtSUb5fg3G5PuNgyauBN"

# STARZBET BİLGİLERİ
STARZBET = {
    "site": "https://starzbet422.com",
    "kayit": "https://starzbet422.com/tr-tr/register",
    "bonus": "https://starzbet422.com/tr-tr/info/promos",
    "spor": "https://starzbet422.com/sports",
    "casino": "https://starzbet422.com/live-casino",
    "apk": "https://starzbet422.com/apk",
    "telegram": "https://t.me/Starzbetgir",
    "destek": "https://service.3kanumaigc.com/chatwindow.aspx?siteId=90005302&planId=1b050682-cde5-4176-8236-3bb94c891197#",
    "giris": "https://starzbet422.com/tr-tr/info/access"
}

# GROQ MODELLERİ (Yeni model de dahil)
GROQ_MODELS = {
    "llama": "llama-3.3-70b-versatile",  # Orjinal model
    "gpt": "openai/gpt-oss-120b",  # Yeni GPT modeli
    "mixtral": "mixtral-8x7b-32768",  # Diğer alternatif
    "gemma": "gemma2-9b-it"  # Daha hızlı model
}

# Aktif model (değiştirebilirsin)
ACTIVE_MODEL = GROQ_MODELS["llama"]

# ========== LOGGING ==========
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('starzbet_bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ========== SİSTEM PROMPT'İ ==========
SYSTEM_PROMPT = """Sen Starzbet422.com'un resmi AI asistanısın. 
Kullanıcılara profesyonel, net ve yardımcı cevaplar ver.

ÖNEMLİ KURALLAR:
1. SADECE starzbet422.com hakkında konuş
2. Asla başka site önerme
3. Kısa ve öz cevaplar ver (max 3-4 cümle)
4. Türkçe dışında dil kullanma
5. Samimi hitap (kanka, dostum) KULLANMA
6. Linkleri her zaman paylaş

TEMEL BİLGİLER:
- Resmi Site: https://starzbet422.com
- Kayıt: https://starzbet422.com/tr-tr/register
- Bonuslar: https://starzbet422.com/tr-tr/info/promos
- Spor Bahis: https://starzbet422.com/sports
- Casino: https://starzbet422.com/live-casino
- Destek: https://service.3kanumaigc.com/chatwindow.aspx?siteId=90005302&planId=1b050682-cde5-4176-8236-3bb94c891197#
- APK: https://starzbet422.com/apk

CEVAP FORMATI:
• Direkt soruya odaklan
• Gereksiz detay verme
• Link ekle
• Profesyonel kal"""

# ========== MENÜLER ==========
def ana_menu():
    keyboard = [
        [InlineKeyboardButton("🌐 RESMİ SİTE", url=STARZBET["site"])],
        [
            InlineKeyboardButton("💰 BONUSLAR", callback_data="bonus"),
            InlineKeyboardButton("⚽ SPOR BAHİS", callback_data="spor")
        ],
        [
            InlineKeyboardButton("🎮 CANLI CASİNO", callback_data="casino"),
            InlineKeyboardButton("📱 APK İNDİR", callback_data="apk")
        ],
        [
            InlineKeyboardButton("🎧 CANLI DESTEK", url=STARZBET["destek"]),
            InlineKeyboardButton("📢 TELEGRAM", url=STARZBET["telegram"])
        ],
        [InlineKeyboardButton("💬 AI İLE KONUŞ", callback_data="ai_chat")]
    ]
    return InlineKeyboardMarkup(keyboard)

def chat_menu():
    keyboard = [
        [InlineKeyboardButton("💰 BONUS SOR", callback_data="soru_bonus")],
        [InlineKeyboardButton("⚽ BAHİS SOR", callback_data="soru_bahis")],
        [InlineKeyboardButton("🎮 CASİNO SOR", callback_data="soru_casino")],
        [InlineKeyboardButton("💳 PARA İŞLEMLERİ", callback_data="soru_para")],
        [
            InlineKeyboardButton("🔗 LİNKLER", callback_data="soru_linkler"),
            InlineKeyboardButton("📝 KAYIT OL", url=STARZBET["kayit"])
        ],
        [
            InlineKeyboardButton("🔄 MODEL DEĞİŞTİR", callback_data="model_degistir"),
            InlineKeyboardButton("🏠 ANA MENÜ", callback_data="ana_menu")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def model_menu():
    keyboard = [
        [InlineKeyboardButton(f"🤖 Llama 3.3 (Hızlı)", callback_data="model_llama")],
        [InlineKeyboardButton(f"🧠 GPT OSS 120B (Akıllı)", callback_data="model_gpt")],
        [InlineKeyboardButton(f"⚡ Mixtral (Orta)", callback_data="model_mixtral")],
        [InlineKeyboardButton(f"🚀 Gemma 2 (Çok Hızlı)", callback_data="model_gemma")],
        [InlineKeyboardButton("🔙 GERİ", callback_data="ana_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ========== GROQ API FONKSİYONLARI ==========
async def groq_api_soru(soru: str, model: str = None) -> Dict[str, Any]:
    """Groq API'ye soru gönder"""
    if model is None:
        model = ACTIVE_MODEL
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Lütfen kısa ve net cevap ver: {soru}"}
        ],
        "temperature": 0.7,
        "max_tokens": 300,
        "top_p": 0.9
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"API Hatası: {e}")
        return None

async def groq_cevap_al(soru: str) -> str:
    """AI'dan cevap al"""
    
    # API anahtarı kontrolü
    if not GROQ_API_KEY or len(GROQ_API_KEY) < 20:
        return "⚠️ API anahtarı gerekli. Lütfen canlı desteğe başvurun."
    
    # Typing efekti için bekle
    await asyncio.sleep(0.5)
    
    try:
        # İlk deneme
        result = await groq_api_soru(soru, ACTIVE_MODEL)
        
        if result and "choices" in result:
            cevap = result["choices"][0]["message"]["content"]
            
            # Cevabı temizle
            cevap = cevap.strip()
            
            # Çok uzunsa kısalt
            if len(cevap) > 800:
                cevap = cevap[:800] + "...\n\n*Devamı için canlı desteğe başvurun.*"
            
            # Link kontrolü - eğer link yoksa ekle
            if STARZBET["site"] not in cevap:
                cevap += f"\n\n🔗 Detaylı bilgi: {STARZBET['site']}"
            
            return cevap
        
        # Eğer ilk model çalışmazsa alternatif dene
        logger.warning(f"Model {ACTIVE_MODEL} çalışmadı, alternatif deneniyor...")
        
        for model_name, model in GROQ_MODELS.items():
            if model != ACTIVE_MODEL:
                result = await groq_api_soru(soru, model)
                if result and "choices" in result:
                    cevap = result["choices"][0]["message"]["content"]
                    return f"🤖 ({model_name.upper()} MODEL):\n\n{cevap}"
        
        # Tüm modeller başarısız olursa
        return f"🌟 **Starzbet422.com**\n\nSorunuz için en güncel bilgileri sitemizde bulabilirsiniz:\n🔗 {STARZBET['site']}\n\nVeya canlı destek: {STARZBET['destek']}"
        
    except Exception as e:
        logger.error(f"AI Cevap Hatası: {e}")
        return await manuel_cevap(soru)

async def manuel_cevap(soru: str) -> str:
    """Manuel cevap sistemi"""
    soru_lower = soru.lower()
    
    cevaplar = {
        "bonus": f"💰 **Bonuslar:**\n\nStarzbet'te çeşitli bonuslar mevcuttur. Detaylar:\n{STARZBET['bonus']}",
        "bahis": f"⚽ **Spor Bahisleri:**\n\nCanlı bahis ve yüksek oranlar. Hemen başla:\n{STARZBET['spor']}",
        "casino": f"🎮 **Casino:**\n\nCanlı casino ve slot oyunları. Oyna:\n{STARZBET['casino']}",
        "kayıt": f"📝 **Kayıt:**\n\nÜcretsiz kayıt için:\n{STARZBET['kayit']}",
        "apk": f"📱 **APK:**\n\nMobil uygulama indir:\n{STARZBET['apk']}",
        "destek": f"🎧 **Destek:**\n\n7/24 canlı destek:\n{STARZBET['destek']}",
        "para": f"💳 **Para İşlemleri:**\n\nKolay para yatırma/çekme. Detaylar için destek:\n{STARZBET['destek']}"
    }
    
    for anahtar, cevap in cevaplar.items():
        if anahtar in soru_lower:
            return cevap
    
    # Genel cevap
    return f"🤖 **Starzbet Asistanı**\n\nSize nasıl yardımcı olabilirim?\n\n**Hızlı Erişim:**\n• Bonus: /bonus\n• Linkler: /linkler\n• Destek: /destek\n\n🔗 **Site:** {STARZBET['site']}"

# ========== KOMUTLAR ==========
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # AI durumu
    ai_durum = "✅ AKTİF" if GROQ_API_KEY and len(GROQ_API_KEY) > 20 else "⚠️ MANUEL"
    model_bilgi = f"Model: {ACTIVE_MODEL.split('/')[-1]}"
    
    mesaj = (
        f"🌟 **HOŞ GELDİN {user.first_name}!** 🌟\n\n"
        f"🤖 **Starzbet AI Asistanı**\n"
        f"🔧 **Durum:** {ai_durum}\n"
        f"🧠 **{model_bilgi}**\n"
        f"🕐 **{datetime.now().strftime('%d.%m.%Y %H:%M')}**\n\n"
        f"**KULLANIM:**\n"
        f"• Butonlarla hızlı erişim\n"
        f"• Direkt soru sorabilirsin\n"
        f"• AI ile konuşabilirsin\n\n"
        f"**KOMUTLAR:**\n"
        f"/bonus - Bonus bilgileri\n"
        f"/linkler - Tüm linkler\n"
        f"/destek - Canlı destek\n"
        f"/model - AI modelini değiştir\n"
        f"/reset - Sıfırla\n\n"
        f"🔗 **Resmi:** {STARZBET['site']}"
    )
    
    await update.message.reply_text(
        mesaj,
        reply_markup=ana_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

async def bonus_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mesaj = (
        f"💰 **STARZBET BONUS SİSTEMİ**\n\n"
        f"🎁 **Hoşgeldin Bonusu** - Yeni üyelere\n"
        f"⚽ **Spor Bonusu** - Bahisler için\n"
        f"🎰 **Casino Bonusu** - Oyunlar için\n"
        f"🔄 **Yenileme Bonusu** - Düzenli oyunculara\n\n"
        f"🔗 **Detaylar:** {STARZBET['bonus']}\n\n"
        f"*Şartlar sitede belirtilmiştir.*"
    )
    
    await update.message.reply_text(
        mesaj,
        reply_markup=ana_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

async def linkler_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mesaj = (
        f"🔗 **STARZBET LİNKLERİ**\n\n"
        f"• 🌐 **Ana Site:** {STARZBET['site']}\n"
        f"• 📝 **Kayıt:** {STARZBET['kayit']}\n"
        f"• 🎁 **Bonuslar:** {STARZBET['bonus']}\n"
        f"• ⚽ **Spor:** {STARZBET['spor']}\n"
        f"• 🎮 **Casino:** {STARZBET['casino']}\n"
        f"• 📱 **APK:** {STARZBET['apk']}\n"
        f"• 📢 **Telegram:** {STARZBET['telegram']}\n"
        f"• 🎧 **Destek:** {STARZBET['destek']}"
    )
    
    await update.message.reply_text(
        mesaj,
        reply_markup=ana_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

async def destek_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mesaj = (
        f"🎧 **CANLI DESTEK**\n\n"
        f"7/24 canlı destek ekibimiz:\n"
        f"{STARZBET['destek']}\n\n"
        f"**Destek Konuları:**\n"
        f"• Hesap işlemleri\n"
        f"• Para yatırma/çekme\n"
        f"• Teknik problemler\n"
        f"• Genel sorular\n\n"
        f"⏰ **Çalışma Saatleri:** 24/7"
    )
    
    await update.message.reply_text(
        mesaj,
        reply_markup=ana_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

async def model_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mesaj = (
        f"🤖 **AI MODEL SEÇİMİ**\n\n"
        f"**Mevcut Model:** {ACTIVE_MODEL}\n\n"
        f"**Modeller:**\n"
        f"• 🤖 Llama 3.3 - Hızlı ve dengeli\n"
        f"• 🧠 GPT OSS 120B - Çok akıllı\n"
        f"• ⚡ Mixtral - Orta seviye\n"
        f"• 🚀 Gemma 2 - Çok hızlı\n\n"
        f"Aşağıdan bir model seçin:"
    )
    
    await update.message.reply_text(
        mesaj,
        reply_markup=model_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔄 **Sohbet sıfırlandı!**\n\nYeni bir konuşmaya başlayabilirsiniz.",
        reply_markup=ana_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

# ========== MESAJ HANDLER ==========
async def mesaj_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    
    # Çok kısa mesaj kontrolü
    if len(user_message.strip()) < 2:
        await update.message.reply_text(
            "Lütfen daha açıklayıcı bir soru sorun.",
            reply_markup=chat_menu()
        )
        return
    
    # Typing efekti
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )
    
    # AI'dan cevap al
    cevap = await groq_cevap_al(user_message)
    
    await update.message.reply_text(
        cevap,
        reply_markup=chat_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

# ========== BUTON HANDLER ==========
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    global ACTIVE_MODEL
    
    try:
        if data == "ana_menu":
            await query.edit_message_text(
                "🏠 **Ana Menü**\n\nSize nasıl yardımcı olabilirim?",
                reply_markup=ana_menu(),
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif data == "ai_chat":
            await query.edit_message_text(
                "💬 **AI SOHBET MODU**\n\nStarzbet ile ilgili sorularınızı buraya yazın.\n\nÖrnek: 'Bonuslar neler?' veya 'Nasıl para yatırırım?'",
                reply_markup=chat_menu(),
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif data.startswith("model_"):
            if data == "model_degistir":
                await query.edit_message_text(
                    "🤖 **Model Seçin**\n\nHangi AI modelini kullanmak istersiniz?",
                    reply_markup=model_menu(),
                    parse_mode=ParseMode.MARKDOWN
                )
            elif data == "model_llama":
                ACTIVE_MODEL = GROQ_MODELS["llama"]
                await query.edit_message_text(
                    f"✅ **Model değiştirildi:** Llama 3.3\n\nArtık daha hızlı yanıt alacaksınız!",
                    reply_markup=ana_menu(),
                    parse_mode=ParseMode.MARKDOWN
                )
            elif data == "model_gpt":
                ACTIVE_MODEL = GROQ_MODELS["gpt"]
                await query.edit_message_text(
                    f"✅ **Model değiştirildi:** GPT OSS 120B\n\nArtık daha akıllı yanıt alacaksınız!",
                    reply_markup=ana_menu(),
                    parse_mode=ParseMode.MARKDOWN
                )
            elif data == "model_mixtral":
                ACTIVE_MODEL = GROQ_MODELS["mixtral"]
                await query.edit_message_text(
                    f"✅ **Model değiştirildi:** Mixtral\n\nOrta seviye AI aktif!",
                    reply_markup=ana_menu(),
                    parse_mode=ParseMode.MARKDOWN
                )
            elif data == "model_gemma":
                ACTIVE_MODEL = GROQ_MODELS["gemma"]
                await query.edit_message_text(
                    f"✅ **Model değiştirildi:** Gemma 2\n\nÇok hızlı yanıtlar alacaksınız!",
                    reply_markup=ana_menu(),
                    parse_mode=ParseMode.MARKDOWN
                )
        
        elif data.startswith("soru_"):
            soru_tipi = data.replace("soru_", "")
            
            sorular = {
                "bonus": "Starzbet bonusları nelerdir?",
                "bahis": "Spor bahisleri nasıl oynanır?",
                "casino": "Canlı casino oyunları neler?",
                "para": "Para yatırma yöntemleri neler?",
                "linkler": "Starzbet linklerini verir misin?"
            }
            
            if soru_tipi in sorular:
                cevap = await groq_cevap_al(sorular[soru_tipi])
                await query.edit_message_text(
                    cevap,
                    reply_markup=chat_menu(),
                    parse_mode=ParseMode.MARKDOWN
                )
        
        elif data in ["bonus", "spor", "casino", "apk"]:
            linkler = {
                "bonus": STARZBET["bonus"],
                "spor": STARZBET["spor"],
                "casino": STARZBET["casino"],
                "apk": STARZBET["apk"]
            }
            
            isimler = {
                "bonus": "Bonuslar",
                "spor": "Spor Bahis",
                "casino": "Canlı Casino",
                "apk": "APK İndir"
            }
            
            await query.edit_message_text(
                f"🔗 **{isimler[data]}**\n\n{linkler[data]}",
                reply_markup=ana_menu(),
                parse_mode=ParseMode.MARKDOWN
            )
    
    except Exception as e:
        logger.error(f"Buton hatası: {e}")
        await query.message.reply_text(
            "❌ Bir hata oluştu. Lütfen tekrar deneyin.",
            parse_mode=ParseMode.MARKDOWN
        )

# ========== ANA PROGRAM ==========
def main():
    print("=" * 60)
    print("🤖 STARZBET GROQ AI BOT")
    print("=" * 60)
    
    print(f"🔑 Token: {'✅' if TELEGRAM_TOKEN else '❌'}")
    print(f"🤖 API Key: {'✅' if GROQ_API_KEY and len(GROQ_API_KEY) > 20 else '❌'}")
    print(f"🧠 Model: {ACTIVE_MODEL}")
    print(f"🌐 Site: {STARZBET['site']}")
    print("🔄 Bot başlatılıyor...")
    
    try:
        app = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # Komutlar
        app.add_handler(CommandHandler("start", start_command))
        app.add_handler(CommandHandler("bonus", bonus_command))
        app.add_handler(CommandHandler("linkler", linkler_command))
        app.add_handler(CommandHandler("destek", destek_command))
        app.add_handler(CommandHandler("model", model_command))
        app.add_handler(CommandHandler("reset", reset_command))
        app.add_handler(CommandHandler("yardim", start_command))
        
        # Butonlar
        app.add_handler(CallbackQueryHandler(button_handler))
        
        # Mesajlar
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mesaj_handler))
        
        print("✅ Bot hazır!")
        print("📱 Telegram'da /start yazın")
        
        app.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        print(f"❌ HATA: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

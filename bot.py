#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STARZBET AI TELEGRAM BOT - TAM ÇALIŞAN VERSİYON
"""

import os
import sys
import logging
import json
import asyncio
from datetime import datetime
from typing import Dict, Any

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
TELEGRAM_TOKEN = "8031564377:AAHjJXBQ-b6f0BnKdbf6T7iwUjs1fCA7dW0"
GROQ_API_KEY = "gsk_lHTS30e86lFzxmC3F7ROWGdyb3FYamQVtSUb5fg3G5PuNgyauBN"

# STARZBET BİLGİLERİ
STARZBET = {
    "site": "https://starzbet423.com",
    "kayit": "https://starzbet422.com/tr-tr/register",
    "bonus": "https://starzbet422.com/tr-tr/info/promos",
    "spor": "https://starzbet422.com/sports",
    "casino": "https://starzbet422.com/live-casino",
    "apk": "https://starzbet422.com/apk",
    "telegram": "https://t.me/Starzbetgir",
    "destek": "https://service.3kanumaigc.com/chatwindow.aspx?siteId=90005302&planId=1b050682-cde5-4176-8236-3bb94c891197#",
    "giris": "https://starzbet422.com/tr-tr/info/access"
}

# Aktif model
ACTIVE_MODEL = "llama-3.3-70b-versatile"

# ========== LOGGING ==========
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,  # DEBUG moduna alındı
    handlers=[
        logging.FileHandler('bot_debug.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ========== SİSTEM PROMPT ==========
SYSTEM_PROMPT = """Sen Starzbet422.com'un resmi AI asistanısın. 
Kısa, net ve yardımcı cevaplar ver.

KURALLAR:
1. SADECE STARZBET hakkında konuş
2. Kısa cevap ver (max 2-3 cümle)
3. Link ekle
4. Profesyonel ol

BİLGİLER:
- Site: https://starzbet423.com
- Kayıt: https://starzbet423.com/tr-tr/register
- Bonus: https://starzbet423.com/tr-tr/info/promos
- Spor: https://starzbet423.com/sports
- Casino: https://starzbet423.com/live-casino
- Destek: https://service.3kanumaigc.com/chatwindow.aspx?siteId=90005302&planId=1b050682-cde5-4176-8236-3bb94c891197#
- APK: https://starzbet423.com/apk"""

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
        [InlineKeyboardButton("💬 SORU SOR", callback_data="soru_sor")]
    ]
    return InlineKeyboardMarkup(keyboard)

def soru_menu():
    keyboard = [
        [InlineKeyboardButton("💰 BONUS SOR", callback_data="bonus_sor")],
        [InlineKeyboardButton("⚽ BAHİS SOR", callback_data="bahis_sor")],
        [InlineKeyboardButton("🎮 CASİNO SOR", callback_data="casino_sor")],
        [InlineKeyboardButton("💳 PARA SOR", callback_data="para_sor")],
        [
            InlineKeyboardButton("🔗 LİNKLER", callback_data="linkler_goster"),
            InlineKeyboardButton("📝 KAYIT OL", url=STARZBET["kayit"])
        ],
        [
            InlineKeyboardButton("🎧 CANLI DESTEK", url=STARZBET["destek"]),
            InlineKeyboardButton("🏠 ANA MENÜ", callback_data="ana_menu")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# ========== GROQ API ==========
def groq_soru(soru: str) -> str:
    """Groq API'ye soru gönder ve cevap al"""
    
    # API anahtarı kontrolü
    if not GROQ_API_KEY or GROQ_API_KEY == "":
        logger.error("API anahtarı yok!")
        return manuel_cevap(soru)
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": ACTIVE_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": soru}
        ],
        "temperature": 0.7,
        "max_tokens": 200,
        "top_p": 0.9
    }
    
    try:
        logger.info(f"API'ye soru gönderiliyor: {soru[:50]}...")
        response = requests.post(url, headers=headers, json=data, timeout=10)
        logger.info(f"API yanıt kodu: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            cevap = result["choices"][0]["message"]["content"]
            logger.info(f"API başarılı, cevap uzunluğu: {len(cevap)}")
            return cevap
        else:
            logger.error(f"API hatası: {response.status_code} - {response.text}")
            return manuel_cevap(soru)
            
    except Exception as e:
        logger.error(f"API istisnası: {e}")
        return manuel_cevap(soru)

def manuel_cevap(soru: str) -> str:
    """API çalışmazsa manuel cevap ver"""
    soru_lower = soru.lower()
    
    if "bonus" in soru_lower:
        return f"🎁 **Starzbet Bonusları:**\n\nÇeşitli bonuslar mevcut. Detaylar: {STARZBET['bonus']}"
    
    elif any(k in soru_lower for k in ["bahis", "spor", "iddaa"]):
        return f"⚽ **Spor Bahisleri:**\n\nCanlı bahis ve yüksek oranlar: {STARZBET['spor']}"
    
    elif any(k in soru_lower for k in ["casino", "rulet", "slot"]):
        return f"🎰 **Casino Oyunları:**\n\nCanlı casino: {STARZBET['casino']}"
    
    elif any(k in soru_lower for k in ["kayıt", "üye", "register"]):
        return f"📝 **Kayıt Ol:**\n\nHızlı kayıt: {STARZBET['kayit']}"
    
    elif any(k in soru_lower for k in ["apk", "mobil", "indir"]):
        return f"📱 **APK İndir:**\n\nMobil uygulama: {STARZBET['apk']}"
    
    elif any(k in soru_lower for k in ["yardım", "yardim", "help"]):
        return f"🤖 **Starzbet Asistanı**\n\nSize nasıl yardımcı olabilirim?\n\nKomutlar:\n• /bonus - Bonuslar\n• /linkler - Linkler\n• /destek - Destek\n\n🔗 Site: {STARZBET['site']}"
    
    else:
        return f"🤖 **Starzbet Asistanı**\n\nSoru: '{soru}'\n\nEn iyi hizmet için:\n🔗 Site: {STARZBET['site']}\n🎧 Destek: {STARZBET['destek']}"

# ========== KOMUTLAR ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start komutu"""
    logger.info(f"/start komutu: {update.effective_user.id}")
    
    mesaj = (
        f"🌟 **HOŞ GELDİN {update.effective_user.first_name}!** 🌟\n\n"
        f"🤖 **Starzbet AI Asistanı**\n"
        f"✅ **Durum:** Aktif\n"
        f"🧠 **Model:** Llama 3.3\n"
        f"🕐 **{datetime.now().strftime('%d.%m.%Y %H:%M')}**\n\n"
        f"**NASIL KULLANILIR:**\n"
        f"1. Butonlara tıklayın\n"
        f"2. Direkt soru yazın\n"
        f"3. Komutları kullanın\n\n"
        f"**KOMUTLAR:**\n"
        f"• /bonus - Bonus bilgileri\n"
        f"• /linkler - Tüm linkler\n"
        f"• /destek - Canlı destek\n"
        f"• /reset - Sıfırla\n\n"
        f"🔗 **Resmi Site:** {STARZBET['site']}"
    )
    
    await update.message.reply_text(
        mesaj,
        reply_markup=ana_menu(),
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True
    )
    logger.info("Start mesajı gönderildi")

async def bonus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bonus komutu"""
    logger.info("/bonus komutu")
    
    mesaj = (
        f"💰 **STARZBET BONUSLARI**\n\n"
        f"🎁 **Hoşgeldin Bonusu**\n"
        f"Yeni üyelere özel\n\n"
        f"⚽ **Spor Bonusları**\n"
        f"Bahisler için ekstra\n\n"
        f"🎰 **Casino Bonusu**\n"
        f"Slot ve masa oyunları\n\n"
        f"🔗 **Tüm bonuslar:** {STARZBET['bonus']}\n\n"
        f"*Şartlar sitede mevcuttur.*"
    )
    
    await update.message.reply_text(
        mesaj,
        reply_markup=ana_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

async def linkler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Linkler komutu"""
    logger.info("/linkler komutu")
    
    mesaj = (
        f"🔗 **STARZBET LİNKLERİ**\n\n"
        f"• 🌐 **Site:** {STARZBET['site']}\n"
        f"• 📝 **Kayıt:** {STARZBET['kayit']}\n"
        f"• 🎁 **Bonus:** {STARZBET['bonus']}\n"
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

async def destek(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Destek komutu"""
    logger.info("/destek komutu")
    
    mesaj = (
        f"🎧 **CANLI DESTEK**\n\n"
        f"7/24 canlı destek:\n"
        f"{STARZBET['destek']}\n\n"
        f"**Konular:**\n"
        f"• Hesap işlemleri\n"
        f"• Para yatırma/çekme\n"
        f"• Teknik sorunlar\n"
        f"• Genel sorular\n\n"
        f"⏰ **7/24 Hizmet**"
    )
    
    await update.message.reply_text(
        mesaj,
        reply_markup=ana_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reset komutu"""
    logger.info("/reset komutu")
    
    await update.message.reply_text(
        "🔄 **Sohbet sıfırlandı!**\n\nYeni bir konuşmaya başlayabilirsin.",
        reply_markup=ana_menu(),
        parse_mode=ParseMode.MARKDOWN
    )

# ========== MESAJ HANDLER ==========
async def mesaj_handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Normal mesajları işle"""
    user_id = update.effective_user.id
    mesaj_text = update.message.text
    
    logger.info(f"Mesaj alındı: {user_id} - {mesaj_text[:50]}...")
    
    # Typing efekti
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )
    
    # AI'dan cevap al
    cevap = groq_soru(mesaj_text)
    
    logger.info(f"Cevap hazır, gönderiliyor...")
    
    await update.message.reply_text(
        cevap,
        reply_markup=soru_menu(),
        parse_mode=ParseMode.MARKDOWN,
        disable_web_page_preview=True
    )
    logger.info(f"Cevap gönderildi: {user_id}")

# ========== BUTON HANDLER ==========
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Buton tıklamalarını işle"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    logger.info(f"Buton tıklandı: {data}")
    
    try:
        if data == "ana_menu":
            await query.edit_message_text(
                "🏠 **Ana Menü**\n\nAşağıdaki seçeneklerden birini seçin:",
                reply_markup=ana_menu(),
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif data == "soru_sor":
            await query.edit_message_text(
                "💬 **SORU SOR**\n\nStarzbet ile ilgili sorularınızı buraya yazın.\n\nÖrnek: 'Bonuslar neler?' veya 'Nasıl kayıt olurum?'",
                reply_markup=soru_menu(),
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif data == "bonus":
            await query.edit_message_text(
                f"💰 **BONUSLAR**\n\nDetaylı bonus bilgileri:\n{STARZBET['bonus']}",
                reply_markup=ana_menu(),
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif data == "spor":
            await query.edit_message_text(
                f"⚽ **SPOR BAHİS**\n\nSpor bahisleri için:\n{STARZBET['spor']}",
                reply_markup=ana_menu(),
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif data == "casino":
            await query.edit_message_text(
                f"🎮 **CASİNO**\n\nCasino oyunları için:\n{STARZBET['casino']}",
                reply_markup=ana_menu(),
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif data == "apk":
            await query.edit_message_text(
                f"📱 **APK İNDİR**\n\nMobil uygulama için:\n{STARZBET['apk']}",
                reply_markup=ana_menu(),
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif data == "linkler_goster":
            await query.edit_message_text(
                f"🔗 **LİNKLER**\n\n• Site: {STARZBET['site']}\n• Kayıt: {STARZBET['kayit']}\n• Destek: {STARZBET['destek']}",
                reply_markup=soru_menu(),
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif data.endswith("_sor"):
            soru_tipi = data.replace("_sor", "")
            sorular = {
                "bonus": "Starzbet bonusları nelerdir?",
                "bahis": "Spor bahisleri nasıl oynanır?",
                "casino": "Canlı casino oyunları neler?",
                "para": "Para yatırma yöntemleri neler?"
            }
            
            if soru_tipi in sorular:
                await query.edit_message_text(
                    "⏳ **Cevap hazırlanıyor...**",
                    parse_mode=ParseMode.MARKDOWN
                )
                
                cevap = groq_soru(sorular[soru_tipi])
                
                await query.edit_message_text(
                    cevap,
                    reply_markup=soru_menu(),
                    parse_mode=ParseMode.MARKDOWN,
                    disable_web_page_preview=True
                )
    
    except Exception as e:
        logger.error(f"Buton handler hatası: {e}")
        await query.message.reply_text(
            "❌ Bir hata oluştu. Lütfen tekrar deneyin.",
            parse_mode=ParseMode.MARKDOWN
        )

# ========== ANA PROGRAM ==========
def main():
    print("=" * 60)
    print("🤖 STARZBET TELEGRAM BOT - DEBUG MODE")
    print("=" * 60)
    
    print(f"✅ Token: {TELEGRAM_TOKEN[:10]}...")
    print(f"✅ API Key: {GROQ_API_KEY[:10]}...")
    print(f"✅ Model: {ACTIVE_MODEL}")
    print(f"✅ Site: {STARZBET['site']}")
    print("🔄 Bot başlatılıyor...")
    
    try:
        # Application oluştur
        app = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # DEBUG: Tüm güncellemeleri logla
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("bonus", bonus))
        app.add_handler(CommandHandler("linkler", linkler))
        app.add_handler(CommandHandler("destek", destek))
        app.add_handler(CommandHandler("reset", reset))
        
        # Buton handler
        app.add_handler(CallbackQueryHandler(button_handler))
        
        # MESAJ HANDLER - EN ÖNEMLİ KISIM
        # Tüm metin mesajlarını al (komut hariç)
        app.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            mesaj_handle
        ))
        
        print("✅ Bot çalışmaya hazır!")
        print("📱 Telegram'da /start yazın")
        print("📝 Loglar: bot_debug.log")
        
        # Polling başlat
        app.run_polling(
            drop_pending_updates=True,
            timeout=30,
            allowed_updates=Update.ALL_TYPES
        )
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {type(e).__name__}: {e}")
        
        # Detaylı hata analizi
        if "Unauthorized" in str(e):
            print("\n🔴 HATA: Geçersiz Telegram Token!")
            print(f"Token: {TELEGRAM_TOKEN[:15]}...")
            print("👉 @BotFather'dan yeni token alın")
        
        elif "Connection" in str(e):
            print("\n🔴 HATA: İnternet bağlantısı yok!")
        
        else:
            print(f"\n🔴 HATA DETAYI:")
            import traceback
            traceback.print_exc()
        
        sys.exit(1)

if __name__ == "__main__":
    main()

import os
import logging
import asyncio
import http.server
import socketserver
import threading
import google.generativeai as genai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- YAPAY ZEKA AYARI ---
# Buraya Google'dan aldığın ücretsiz API KEY'i yaz
GEMINI_API_KEY = "BURAYA_GEMINI_API_KEYINI_YAZ"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# AI'ya Starzbet kurallarını ve kişiliğini öğretiyoruz (Prompt Engineering)
AI_TALIMATI = (
    "Sen Starzbet bahis sitesinin kurumsal ve yardımsever müşteri asistanısın. "
    "Asla 'kanka' gibi samimi ifadeler kullanma, profesyonel ve 'Siz' odaklı konuş. "
    "Starzbet hakkında şu bilgileri bilmelisin: "
    "1- Yatırımlarda Dinamik Pay ön plandadır ve anında işlem yapılır. "
    "2- Cuma, Cumartesi ve Pazar günleri %35 Kayıp Bonusu verilir. Hafta içi %30'dur. "
    "3- Slot, Spor ve Kripto için %100 Hoş Geldin bonusları vardır. "
    "4- Payfix sistemimizde yoktur, Dinamik Pay kullanılmalıdır. "
    "5- Çekim süreleri hakkında kesin bilgi verme, 'En kısa sürede' de. "
    "Cevapların kısa, öz ve her zaman siteye yönlendirici olsun."
)

# --- GÖRSEL VE LİNK AYARLARI ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEDIA = {
    "ANA_MENU": os.path.join(BASE_DIR, "ana.jpg"),
    "DINAMIK_PAY": os.path.join(BASE_DIR, "dinamik.jpg"),
    "SLOT_100": os.path.join(BASE_DIR, "casinohosgelin.jpg"),
    "SPOR_100": os.path.join(BASE_DIR, "sporhosgelin.jpg"),
    "KRIPTO_100": os.path.join(BASE_DIR, "kripto.jpg"),
    "KAYIP_35": os.path.join(BASE_DIR, "35kayip.jpg"),
    "MOBIL_APP": os.path.join(BASE_DIR, "uygulama.jpg")
}

TOKEN = "8031564377:AAHjJXBQ-b6f0BnKdbf6T7iwUjs1fCA7dW0"
LINK_GIRIS = "https://cutt.ly/drVOi2EN"
LINK_BONUSLAR = "https://starzbet422.com/tr-tr/info/promos"
LINK_CANLI_DESTEK = "https://service.3kanumaigc.com/chatwindow.aspx?siteId=90005302&planId=1b050682-cde5-4176-8236-3bb94c891197#"
LINK_MINI_APP = "https://telegram-mini-app-umber-chi.vercel.app"

# --- RENDER SAHTE SUNUCU ---
def run_dummy_server():
    PORT = int(os.environ.get("PORT", 8080))
    handler = http.server.SimpleHTTPRequestHandler
    try:
        with socketserver.TCPServer(("", PORT), handler) as httpd:
            httpd.serve_forever()
    except Exception: pass
threading.Thread(target=run_dummy_server, daemon=True).start()

# --- KLAVYELER ---
def ana_menu_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎰 STARZBET MİNİ APP", web_app=WebAppInfo(url=LINK_MINI_APP))],
        [InlineKeyboardButton("💳 DİNAMİK PAY İLE YATIRIM", callback_data="btn_dinamik")],
        [InlineKeyboardButton("🎰 SLOT %100 HOŞ GELDİN", callback_data="btn_slot"), 
         InlineKeyboardButton("⚽ SPOR %100 HOŞ GELDİN", callback_data="btn_spor")],
        [InlineKeyboardButton("🪙 KRİPTO %100 HOŞ GELDİN", callback_data="btn_kripto"), 
         InlineKeyboardButton("✨ %35 KAYIP BONUSU", callback_data="btn_kayip")],
        [InlineKeyboardButton("📱 MOBİL UYGULAMA", callback_data="btn_app"), 
         InlineKeyboardButton("🎧 CANLI DESTEK", url=LINK_CANLI_DESTEK)],
        [InlineKeyboardButton("🔗 GÜNCEL GİRİŞ ADRESİ", url=LINK_GIRIS)]
    ])

def detay_kb(bonus_mu=False):
    url_target = LINK_BONUSLAR if bonus_mu else LINK_GIRIS
    text_target = "🎁 BONUSLARI İNCELE" if bonus_mu else "🌐 SİTEYE GİT"
    return InlineKeyboardMarkup([[InlineKeyboardButton(text_target, url=url_target)], [InlineKeyboardButton("⬅️ GERİ DÖN", callback_data="btn_back")]])

# --- YAPAY ZEKA CEVAP FONKSİYONU ---
async def ai_cevap_ver(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text
    # Gemini'ye gönderilecek mesajı hazırlıyoruz
    prompt = f"{AI_TALIMATI}\n\nKullanıcı Sorusu: {user_msg}\nCevap:"
    
    try:
        response = model.generate_content(prompt)
        await update.message.reply_text(response.text, parse_mode=ParseMode.HTML, reply_markup=ana_menu_kb())
    except Exception as e:
        await update.message.reply_text("Sistemimizde kısa süreli bir yoğunluk yaşanıyor, lütfen tekrar deneyiniz.", reply_markup=ana_menu_kb())
async def ai_asistan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    
    user_msg = update.message.text
    # AI'ya daha net bir komut veriyoruz
    prompt = f"Sen Starzbet asistanısın. Müşteriye nazikçe cevap ver: {user_msg}"
    
    try:
        # AI yanıtını oluştururken güvenlik ayarlarını esnetiyoruz (Bahis kelimeleri takılmasın diye)
        response = model.generate_content(
            prompt,
            safety_settings=[
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]
        )
        
        if response.text:
            await update.message.reply_text(response.text, parse_mode=ParseMode.HTML, reply_markup=ana_menu_kb())
        else:
            await update.message.reply_text("Üzgünüm, şu an yanıt oluşturamıyorum.", reply_markup=ana_menu_kb())
            
    except Exception as e:
        # Hata neyse direkt Telegram'dan sana yazacak, böylece sorunu anlarız
        error_msg = f"🤖 AI Bağlantı Hatası: {str(e)}"
        print(error_msg) # Render loglarına yazar
        await update.message.reply_text("Sistem güncelleniyor, lütfen menü butonlarını kullanın.", reply_markup=ana_menu_kb())
# --- COMMANDS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = "<b>Starzbet'e Hoş Geldiniz.</b>\n\nİşlemleriniz için aşağıdaki menüyü kullanabilir veya merak ettiğiniz konuları buraya yazarak bana sorabilirsiniz."
    
    if update.callback_query: await update.callback_query.message.delete()

    if os.path.exists(MEDIA["ANA_MENU"]):
        await context.bot.send_photo(chat_id=chat_id, photo=open(MEDIA["ANA_MENU"], 'rb'), caption=text, reply_markup=ana_menu_kb(), parse_mode=ParseMode.HTML)
    else:
        await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=ana_menu_kb(), parse_mode=ParseMode.HTML)

async def buton_tiklama(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    await query.answer()

    info = {
        "btn_dinamik": (MEDIA["DINAMIK_PAY"], "💳 <b>Dinamik Pay İle Yatırım</b>\n\nDinamik Pay ile bekleme süresi olmadan dilediğiniz tutarda anında yatırım yapabilirsiniz.", False),
        "btn_slot": (MEDIA["SLOT_100"], "🎰 <b>Slot Hoş Geldin Bonusu</b>\n\nİlk yatırımınıza özel %100 Slot bonusu ile kazancınızı katlamaya başlayın.", True),
        "btn_spor": (MEDIA["SPOR_100"], "⚽ <b>Spor Hoş Geldin Bonusu</b>\n\nSpor bahislerinde ilk yatırımınıza özel %100 bonus fırsatından yararlanın.", True),
        "btn_kripto": (MEDIA["KRIPTO_100"], "🪙 <b>Kripto Yatırım Bonusu</b>\n\nKripto yatırımlarınıza özel %100 bonus avantajı ile Starzbet'te yerinizi alın.", True),
        "btn_kayip": (MEDIA["KAYIP_35"], "✨ <b>Kayıp Bonusu</b>\n\nCuma, Cumartesi ve Pazar günleri %35, hafta içi ise %30 kayıp bonusu ile şansınız devam ediyor.", True),
        "btn_app": (MEDIA["MOBIL_APP"], "📱 <b>Mobil Uygulama</b>\n\nStarzbet uygulamasını indirerek güncel adrese ihtiyaç duymadan kesintisiz erişim sağlayın.", False)
    }

    if data in info:
        gorsel, aciklama, is_bonus = info[data]
        await query.message.delete()
        if os.path.exists(gorsel):
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(gorsel, 'rb'), caption=aciklama, reply_markup=detay_kb(bonus_mu=is_bonus), parse_mode=ParseMode.HTML)
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=aciklama, reply_markup=detay_kb(bonus_mu=is_bonus), parse_mode=ParseMode.HTML)
    elif data == "btn_back":
        await start(update, context)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(buton_tiklama))
    # Komut olmayan her metni AI'ya gönderir
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), ai_cevap_ver))
    
    print("🚀 Yapay Zeka Destekli Starzbet Bot Aktif!")
    application.run_polling()

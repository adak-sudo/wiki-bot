import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# --- AYARLAR ---
# BotFather'dan aldığın Token'ı buraya yapıştır
TOKEN = '7766706327:AAGH9W9bO6nkVEWDzZvmSnk2mKmMXl4gGOk'

# Loglama ayarı (Hataları görmek için)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- FONKSİYONLAR ---

def get_random_wiki():
    """Wikipedia API'den rastgele Türkçe bilgi ve görsel çeker."""
    try:
        # Türkçe Wikipedia'dan rastgele bir sayfa özeti çeker
        url = "https://tr.wikipedia.org/api/rest_v1/page/random/summary"
        
        # Profesyonel yaklaşım: API'ye kim olduğumuzu söyleyen bir User-Agent ekliyoruz
        headers = {'User-Agent': 'GizliWikiBilgiBot/1.0 (https://t.me/SeninBotUsernamin)'}
        
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        # Verileri ayrıştırıyoruz
        title = data.get('title', 'Başlık Yok')
        extract = data.get('extract', 'İçerik bulunamadı.')
        link = data.get('content_urls', {}).get('desktop', {}).get('page', '')
        
        # GÖRSEL KONTROLÜ: 'originalimage' anahtarını kontrol et
        image_url = data.get('originalimage', {}).get('source', None)
        
        return title, extract, link, image_url
    except Exception as e:
        logging.error(f"Hata oluştu: {e}")
        return None, None, None, None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bot linkle ilk başlatıldığında selam verir."""
    await update.message.reply_text(
        "Özel Wiki Bilgi Botu'na hoş geldin! 🎓🤖\n\n"
        "Rastgele ilginç bir bilgi ve görsel öğrenmek için /bilgi yazman yeterli."
    )

async def bilgi_gonder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kullanıcıya görsel ve bilgiyi şık bir formatta sunar."""
    # Verileri çek
    title, extract, link, image_url = get_random_wiki()
    
    if not title:
        await update.message.reply_text("❌ Bir hata oluştu, lütfen tekrar dene.")
        return

    # Mesaj metnini formatla (Bold başlık + Özet)
    formatted_text = f"📖 *{title}*\n\n{extract}"
    
    # "Wikipedia'da Oku" butonu
    keyboard = [[InlineKeyboardButton("🔗 Wikipedia'da Oku", url=link)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # --- GÖRSEL GÖNDERME MANTIĞI ---
    if image_url:
        # Eğer görsel varsa, 'send_photo' kullan ve metni açıklama (caption) olarak ekle
        try:
            await update.message.reply_photo(
                photo=image_url,
                caption=formatted_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        except Exception as photo_error:
            # Görsel gönderirken hata oluşursa (örn: link kırıksa), sadece metni gönder
            logging.error(f"Görsel gönderme hatası: {photo_error}")
            await update.message.reply_text(
                formatted_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
    else:
        # Eğer görsel yoksa, eskisi gibi sadece metni gönder
        await update.message.reply_text(
            formatted_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )

# --- ANA ÇALIŞTIRICI ---
if __name__ == '__main__':
    # Uygulamayı başlatıyoruz
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Komutları bota tanıtıyoruz
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("bilgi", bilgi_gonder))
    
    # Botu çalıştır (Polling yöntemi)
    print("Görsel destekli gizli bot yayında! Sadece linke sahip olanlar kullanabilir...")
    app.run_polling()

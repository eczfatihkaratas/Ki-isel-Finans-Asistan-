"""
PROJE FELSEFESİ VE HAFIZA BLOĞU:
Hedef: Eylül'ün 2027 Robert Kolej Fonu
Mimari: Kuantum Radar V7 (İş Yatırım İstihbaratı + Akıllı Excel Muhasebe)
Yetki: TEFAS güvenlik duvarını atlamak için İş Yatırım tablolarını okur.
"""

import telebot
from telebot import types
import yfinance as yf
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
import feedparser
import gspread 
import cloudscraper 
import time
import datetime
import threading
import os
from flask import Flask

# --- 1. AYARLAR VE HAFIZA KUTUSU ---
TOKEN = "8492116791:AAErfalTR_QVHzT5Rifnwp-1fcC5ZKdvI3A"
CHAT_ID = "967303324"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

scraper = cloudscraper.create_scraper(
    browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
)

GUNUN_FIRSATLARI = {
    "MAKRO": "Veriler toplanıyor...",
    "ABD": "Geniş piyasa taraması devam ediyor...",
    "BIST": "Geniş BIST taraması devam ediyor...",
    "TEFAS": "İş Yatırım üzerinden fon verileri taranıyor..."
}

NEGATIF_KELIMELER = ["savaş", "kriz", "düşüş", "iflas", "dava", "faiz artış", "zarar", "gerginlik", "satış", "çöküş"]
POZITIF_KELIMELER = ["rekor", "kar", "büyüme", "anlaşma", "faiz indirim", "yükseliş", "alım", "destek", "zirve"]

@app.route('/')
def index():
    return "Kuantum Motoru V7 (İş Yatırım Modülü) Devrede!"

# --- 2. DUYGU ANALİZİ (HABER OKUMA) ---
def haber_duygusu_olc(ticker, is_us=True):
    try:
        if is_us:
            rss_url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US"
        else:
            rss_url = "https://www.ekonomim.com/rss"
        
        res = scraper.get(rss_url, timeout=5)
        feed = feedparser.parse(res.content)
        puan = 0
        
        for entry in feed.entries[:5]: 
            baslik = entry.title.lower()
            for kelime in NEGATIF_KELIMELER:
                if kelime in baslik: puan -= 20
            for kelime in POZITIF_KELIMELER:
                if kelime in baslik: puan += 20
        
        if puan > 30: return "POZİTİF 📈"
        elif puan < -30: return "NEGATİF 📉"
        else: return "NÖTR ⚖️"
    except:
        return "NÖTR ⚖️"

# --- 3. TEKNİK + DUYGU HARMANLAYICI ---
def kuantum_analiz_yap(symbol, screener, exchange, is_us=True):
    try:
        handler = TA_Handler(symbol=symbol, screener=screener, exchange=exchange, interval=Interval.INTERVAL_1_DAY)
        analiz = handler.get_analysis()
        rsi = analiz.indicators.get('RSI')
        fiyat = analiz.indicators.get('close')
        tavsiye = analiz.summary.get('RECOMMENDATION')
        
        if fiyat is None or rsi is None: return None
        
        duygu = haber_duygusu_olc(symbol, is_us)
        direnc = analiz.indicators.get('Pivot.M.Classic.R1', fiyat * 1.05)
        destek = analiz.indicators.get('Pivot.M.Classic.S1', fiyat * 0.95)

        if rsi < 30:
            if duygu == "NEGATİF 📉":
                aksiyon = "⚠️ TEKNİK DİPTE AMA HABER KÖTÜ (Bekle)"
            else:
                aksiyon = "🚀 DİPTE! GÜÇLÜ ALIM veya PUT SAT."
            return f"🟢 {symbol}: {fiyat:.2f} | RSI: {rsi:.1f} | Haber: {duygu}\n   └ 🛠 Karar: {aksiyon}\n   └ 🎯 Hedef: {direnc:.2f} | 🛑 Stop: {destek:.2f}"
            
        elif rsi > 70:
            if duygu == "POZİTİF 📈":
                aksiyon = "⚠️ ZİRVEDE AMA HABERLER İYİ (Trendi İzle)"
            else:
                aksiyon = "🍎 ZİRVE! KAR AL veya CALL SAT."
            return f"🔴 {symbol}: {fiyat:.2f} | RSI: {rsi:.1f} | Haber: {duygu}\n   └ 🛠 Karar: {aksiyon}\n   └ 🎯 Geri Çekilme: {destek:.2f} | 🛑 Zarar Kes: {direnc:.2f}"
            
        elif tavsiye == "STRONG_SELL":
             return f"🔴 {symbol}: {fiyat:.2f} | RSI: {rsi:.1f} | Haber: {duygu}\n   └ 🛠 Karar: 📉 GÜÇLÜ DÜŞÜŞ TRENDİ\n   └ 🎯 Beklenti: {destek:.2f}"
             
        elif tavsiye == "STRONG_BUY":
             return f"🟢 {symbol}: {fiyat:.2f} | RSI: {rsi:.1f} | Haber: {duygu}\n   └ 🛠 Karar: 📈 GÜÇLÜ YÜKSELİŞ TRENDİ\n   └ 🎯 Hedef: {direnc:.2f} | 🛑 Stop: {destek:.2f}"
             
        return None
    except:
        return None

# --- 4. GÖLGE TARAYICI (ARKA PLAN) ---
def golge_tarayici():
    while True:
        try:
            # 1. MAKRO
            vix = yf.Ticker("^VIX").history(period="1d")['Close'].iloc[-1]
            makro = f"💎 VIX KORKU ENDEKSİ: {vix:.2f} " + ("(YÜKSEK! KAN VAR 🚨)" if vix > 25 else "(Stabil ⚖️)")
            GUNUN_FIRSATLARI["MAKRO"] = makro
            
            # ========================================================
            # 2. TEFAS -> İŞ YATIRIM İSTİHBARATI
            # ========================================================
            try:
                is_yatirim_url = "https://www.isyatirim.com.tr/tr-tr/analiz/fon/Sayfalar/Tarihsel-Fiyat-Getiri.aspx"
                headers_is = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                
                # 10 Saniye içinde sayfayı çek
                r = scraper.get(is_yatirim_url, headers=headers_is, timeout=10)
                
                # Sitedeki HTML tablolarını pandas ile oku
                df_list = pd.read_html(r.text, decimal=',', thousands='.')
                df = df_list[0] # Sayfadaki ilk ana tablo
                
                # Tablodaki en sağdaki (Genellikle Günlük Getiri) sütununu bul
                son_sutun = df.columns[-1]
                
                # İçinde % işareti falan varsa temizle ve sayıya çevir
                df[son_sutun] = pd.to_numeric(df[son_sutun].astype(str).str.replace('%', ''), errors='coerce')
                
                # Sıfırdan küçük (düşen) fonları bul, en çok düşenden sırala, ilk 3'ü al
                dusenler = df[df[son_sutun] < 0].sort_values(by=son_sutun, ascending=True).head(3)
                
                if not dusenler.empty:
                    tefas_metin = "🚨 DİPTEKİ FON FIRSATLARI (İş Yatırım Radar)\n"
                    for index, row in dusenler.iterrows():
                        # Fon ismini çok uzun olmasın diye 20 karakterle sınırla
                        fon_adi = str(row[0])[:20] 
                        tefas_metin += f"📉 {fon_adi}... : %{row[son_sutun]:.2f}\n"
                    GUNUN_FIRSATLARI["TEFAS"] = tefas_metin
                else:
                    GUNUN_FIRSATLARI["TEFAS"] = "➖ Bugün sert düşen bir fon fırsatı yok."
            except Exception as e:
                # Tablo yüklenemezse veya site bakımdaysa çökmeyi engelle
                GUNUN_FIRSATLARI["TEFAS"] = "➖ İş Yatırım verileri şu an güncelleniyor (Bekleniyor)."

            # 3. BIST 
            bist_hisseler = ["THYAO", "TUPRS", "ISCTR", "KCHOL", "EREGL", "ASELS", "BIMAS", "SAHOL", "AKBNK", "SISE"]
            bist_sonuclar = [kuantum_analiz_yap(h, "turkey", "BIST", False) for h in bist_hisseler]
            GUNUN_FIRSATLARI["BIST"] = "\n".join(filter(None, bist_sonuclar[:5])) or "➖ Ekstrem fırsat yok."

            # 4. ABD 
            abd_hisseler = ["AAPL", "TSLA", "NVDA", "AMD", "MSFT", "AMZN", "META", "GOOGL"]
            abd_sonuclar = [kuantum_analiz_yap(h, "america", "NASDAQ", True) for h in abd_hisseler]
            GUNUN_FIRSATLARI["ABD"] = "\n".join(filter(None, abd_sonuclar[:5])) or "➖ Ekstrem fırsat yok."

            time.sleep(3600) 
        except:
            time.sleep(60)

# --- 5. RAPORLAMA VE MUHASEBE MERKEZİ ---
def radar_raporu_hazirla():
    rapor = "🎯 ZEKİ ASİSTAN: KUANTUM RADAR V7 🎯\n"
    rapor += "----------------------------------\n\n"
    rapor += f"{GUNUN_FIRSATLARI['MAKRO']}\n\n"
    rapor += "🇺🇸 GLOBAL FIRSAT (Teknik + Haber)\n"
    rapor += f"{GUNUN_FIRSATLARI['ABD']}\n\n"
    rapor += "🇹🇷 LOKAL FIRSAT (Teknik + Haber)\n"
    rapor += f"{GUNUN_FIRSATLARI['BIST']}\n\n"
    rapor += "📊 FON FIRSATI (TEFAS & İŞ YATIRIM)\n"
    rapor += f"{GUNUN_FIRSATLARI['TEFAS']}\n"
    rapor += "----------------------------------\n"
    rapor += "👉 İşlemlerini aracı kurumundan hedeflere göre girebilirsin."
    return rapor

def rapor_gonder(hedef_chat_id):
    mesaj = radar_raporu_hazirla()
    parcalar = [mesaj[i:i+3000] for i in range(0, len(mesaj), 3000)]
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ İŞLEM GİRİLDİ (Muhasebeye Yaz)", callback_data="onay"),
               types.InlineKeyboardButton("❌ PAS GEÇ", callback_data="red"))
    
    try:
        for index, parca in enumerate(parcalar):
            if index == len(parcalar) - 1:
                bot.send_message(hedef_chat_id, parca, reply_markup=markup)
            else:
                bot.send_message(hedef_chat_id, parca)
    except Exception as e:
        bot.send_message(hedef_chat_id, f"⚠️ KOD HATASI: {e}")

# Akıllı Filtreli Muhasebe Modülü
def excel_kayit_yap(message):
    if message.text.startswith('/'):
        bot.reply_to(message, "⚠️ HATA: Hisse adı yerine bir komut girdin. Kayıt işlemi iptal edildi.")
        return 
        
    try:
        gc = gspread.service_account(filename='creds.json')
        
        # --- DİKKAT: AŞAĞIDAKİ YERE KENDİ EXCEL ID NUMARANI YAPIŞTIR ---
        sh = gc.open_by_key("14Q8repG8ThqSeSsPyy6uaLrFDdtwsCsdfwj2cu3H3VA")
        
        worksheet = sh.sheet1 

        tarih = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
        islem_detayi = message.text

        worksheet.append_row([tarih, islem_detayi])
        
        bot.reply_to(message, f"✅ İşlem başarıyla KENDİ Excel dosyana işlendi!\n📝 Kaydedilen: {islem_detayi}")
    except Exception as e:
        bot.reply_to(message, f"⚠️ Muhasebe Hatası (Excel'e bağlanılamadı): {e}")

@bot.message_handler(commands=['rapor'])
def manuel_rapor_gonder(message):
    try:
        bot.reply_to(message, "⏳ Piyasalar taranıyor... İş Yatırım verileri çekiliyor...")
        rapor_gonder(message.chat.id)
    except Exception as e:
        bot.reply_to(message, f"⚠️ KOMUT HATASI: {str(e)}")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "onay":
        msg = bot.send_message(call.message.chat.id, "Harika! 📝 Muhasebeye kaydetmem için aldığın hisseyi/fonu ve fiyatı yaz patron.\n(Örn: THYAO 290 TL'den 100 lot alındı)")
        bot.register_next_step_handler(msg, excel_kayit_yap)
    else:
        bot.answer_callback_query(call.id, "Pas geçildi. ✋")

def zamanlayici():
    while True:
        simdi = datetime.datetime.now().strftime("%H:%M")
        if simdi == "16:30" or simdi == "17:45":
            try:
                bot.send_message(CHAT_ID, "🔔 KUANTUM RADARI V7 DEVREDE | Piyasalar Koklanıyor...")
                rapor_gonder(CHAT_ID)
            except:
                pass
            time.sleep(70)
        time.sleep(30)

def bot_calistir():
    threading.Thread(target=zamanlayici, daemon=True).start()
    threading.Thread(target=golge_tarayici, daemon=True).start()
    bot.infinity_polling(timeout=10, long_polling_timeout=5)

if __name__ == "__main__":
    threading.Thread(target=bot_calistir, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

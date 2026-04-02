"""
PROJE FELSEFESİ VE HAFIZA BLOĞU:
Hedef: Eylül'ün 2027 Robert Kolej Fonu
Mimari: Kuantum Radar V3 (Teknik Analiz + DUYGU ANALİZİ / HABER OKUMA)
Yetki: Haber başlıklarını okur, duygu puanı hesaplar ve teknik verilerle harmanlar.
"""

import telebot
from telebot import types
import yfinance as yf
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
import feedparser
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

GUNUN_FIRSATLARI = {
    "MAKRO": "Veriler toplanıyor...",
    "ABD": "Geniş piyasa taraması devam ediyor...",
    "BIST": "Geniş BIST taraması devam ediyor...",
    "TEFAS": "TEFAS verileri taranıyor..."
}

# Duygu Analizi Kelime Sözlüğü (Basit NLP)
NEGATIF_KELIMELER = ["savaş", "kriz", "düşüş", "iflas", "dava", "faiz artış", "zarar", "gerginlik", "satış", "çöküş"]
POZITIF_KELIMELER = ["rekor", "kar", "büyüme", "anlaşma", "faiz indirim", "yükseliş", "alım", "destek", "zirve"]

@app.route('/')
def index():
    return "Haber Koklayan Kuantum Motoru V3 Devrede!"

# --- 2. DUYGU ANALİZİ (HABER OKUMA) MOTORU ---
def haber_duygusu_olc(ticker, is_us=True):
    try:
        if is_us:
            rss_url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US"
        else:
            # BIST için genel ekonomi haberleri
            rss_url = "https://www.ekonomim.com/rss"
        
        feed = feedparser.parse(rss_url)
        puan = 0
        
        for entry in feed.entries[:5]: # Son 5 habere bak
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
        
        # Haberi Okut
        duygu = haber_duygusu_olc(symbol, is_us)
        
        direnc = analiz.indicators.get('Pivot.M.Classic.R1', fiyat * 1.05)
        destek = analiz.indicators.get('Pivot.M.Classic.S1', fiyat * 0.95)

        # Karar Mekanizması (Hibrit)
        if rsi < 30:
            if duygu == "NEGATİF 📉":
                aksiyon = "⚠️ TEKNİK DİPTE AMA HABER KÖTÜ (Bıçak Düşüyor, Bekle)"
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

# --- 4. GÖLGE TARAYICI (ARKA PLAN İŞÇİSİ) ---
def golge_tarayici():
    while True:
        try:
            # 1. MAKRO
            vix = yf.Ticker("^VIX").history(period="1d")['Close'].iloc[-1]
            makro = f"💎 VIX KORKU ENDEKSİ: {vix:.2f} " + ("(YÜKSEK! KAN VAR 🚨)" if vix > 25 else "(Stabil ⚖️)")
            GUNUN_FIRSATLARI["MAKRO"] = makro
            
            # 2. ÖZEL TEFAS HAYALET TARAYICI
            try:
                url = "https://www.tefas.gov.tr/api/profile/boz/getHistory"
                bugun = datetime.datetime.now()
                baslangic = (bugun - datetime.timedelta(days=4)).strftime("%d.%m.%Y")
                bitis = bugun.strftime("%d.%m.%Y")
                payload = f"fontip=YAT&sfontip=&fongrup=&baslangic={baslangic}&bitis={bitis}&fonkod="
                headers = {
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "X-Requested-With": "XMLHttpRequest",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
                }
                res = requests.post(url, data=payload, headers=headers, timeout=15)
                if res.status_code == 200:
                    veri = res.json().get("data", [])
                    if veri:
                        df = pd.DataFrame(veri)
                        df['GÜNLÜK GETİRİ'] = pd.to_numeric(df['GÜNLÜK GETİRİ'], errors='coerce')
                        df_dusenler = df[df['GÜNLÜK GETİRİ'] < 0]
                        en_cok_dusenler = df_dusenler.sort_values(by="GÜNLÜK GETİRİ", ascending=True).head(3)
                        
                        tefas_metin = "🚨 DİPTEKİ FON FIRSATLARI (TEFAS)\n"
                        if not en_cok_dusenler.empty:
                            for index, row in en_cok_dusenler.iterrows():
                                fon_ismi = str(row.get('FON KODU', 'FON'))
                                tefas_metin += f"📉 {fon_ismi}: %{row['GÜNLÜK GETİRİ']:.2f}\n   └ 🛠 Kademeli toplama fırsatı.\n"
                            GUNUN_FIRSATLARI["TEFAS"] = tefas_metin
                        else:
                            GUNUN_FIRSATLARI["TEFAS"] = "➖ Bugün TEFAS'ta sert düşen bir fon fırsatı yok."
                else:
                    GUNUN_FIRSATLARI["TEFAS"] = "➖ TEFAS sunucuları geçici olarak yanıt vermiyor."
            except:
                GUNUN_FIRSATLARI["TEFAS"] = f"➖ TEFAS taraması şu an yapılamıyor."

            # 3. BIST (Teknik + Duygu)
            bist_hisseler = ["THYAO", "TUPRS", "ISCTR", "KCHOL", "EREGL", "ASELS", "BIMAS", "SAHOL", "AKBNK", "SISE"]
            bist_sonuclar = [kuantum_analiz_yap(h, "turkey", "BIST", False) for h in bist_hisseler]
            GUNUN_FIRSATLARI["BIST"] = "\n".join(filter(None, bist_sonuclar[:5])) or "➖ Ekstrem fırsat yok."

            # 4. ABD (Teknik + Duygu)
            abd_hisseler = ["AAPL", "TSLA", "NVDA", "AMD", "MSFT", "AMZN", "META", "GOOGL"]
            abd_sonuclar = [kuantum_analiz_yap(h, "america", "NASDAQ", True) for h in abd_hisseler]
            GUNUN_FIRSATLARI["ABD"] = "\n".join(filter(None, abd_sonuclar[:5])) or "➖ Ekstrem fırsat yok."

            time.sleep(3600) 
        except:
            time.sleep(60)

# --- 5. RAPORLAMA MERKEZİ ---
def radar_raporu_hazirla():
    rapor = "🎯 ZEKİ ASİSTAN: KUANTUM RADAR V3 🎯\n"
    rapor += "----------------------------------\n\n"
    rapor += f"{GUNUN_FIRSATLARI['MAKRO']}\n\n"
    rapor += "🇺🇸 GLOBAL FIRSAT (Teknik + Haber)\n"
    rapor += f"{GUNUN_FIRSATLARI['ABD']}\n\n"
    rapor += "🇹🇷 LOKAL FIRSAT (Teknik + Haber)\n"
    rapor += f"{GUNUN_FIRSATLARI['BIST']}\n\n"
    rapor += "📊 FON FIRSATI (TEFAS)\n"
    rapor += f"{GUNUN_FIRSATLARI['TEFAS']}\n"
    rapor += "----------------------------------\n"
    rapor += "👉 İşlemlerini aracı kurumundan hedeflere göre girebilirsin."
    return rapor

def rapor_gonder(hedef_chat_id):
    mesaj = radar_raporu_hazirla()
    parcalar = [mesaj[i:i+3000] for i in range(0, len(mesaj), 3000)]
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ İŞLEM GİRİLDİ", callback_data="onay"),
               types.InlineKeyboardButton("❌ PAS GEÇ", callback_data="red"))
    
    try:
        for index, parca in enumerate(parcalar):
            if index == len(parcalar) - 1:
                bot.send_message(hedef_chat_id, parca, reply_markup=markup)
            else:
                bot.send_message(hedef_chat_id, parca)
    except Exception as e:
        bot.send_message(hedef_chat_id, f"⚠️ KOD HATASI: {e}")

@bot.message_handler(commands=['rapor'])
def manuel_rapor_gonder(message):
    try:
        bot.reply_to(message, "⏳ Piyasalar KOKLANIYOR... Hem matematik hem duygu analizi yapılıyor...")
        rapor_gonder(message.chat.id)
    except Exception as e:
        bot.reply_to(message, f"⚠️ KOMUT HATASI: {str(e)}")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "onay":
        bot.answer_callback_query(call.id, "Emrin alındı! ✅\nStrateji 2027 hedefine işlendi.")
    else:
        bot.answer_callback_query(call.id, "Pas geçildi. ✋")

def zamanlayici():
    while True:
        simdi = datetime.datetime.now().strftime("%H:%M")
        if simdi == "16:30" or simdi == "17:45":
            try:
                bot.send_message(CHAT_ID, "🔔 KUANTUM RADARI V3 DEVREDE | Piyasalar Koklanıyor...")
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

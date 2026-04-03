"""
PROJE: KUANTUM MOTORU V10 - KÜRESEL HEDGE FON TERMİNALİ
ANAYASA: 
1. Tüm piyasalar (BIST, ABD, Emtia, Döviz) taranır.
2. En iyi 5 fırsat (Call/Put) süzülür.
3. Haber ve duygu analizi zorunludur.
4. Excel (14Q8repG8ThqSeSsPyy6uaLrFDdtwsCsdfwj2cu3H3VA) ana merkezdir.
5. Stop/Kar-Al noktaları uzman hassasiyetiyle verilir.
"""

import telebot
from telebot import types
import yfinance as yf
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
import feedparser
import gspread
import time
import datetime
import threading
import os
from flask import Flask

# --- 1. SİSTEM AYARLARI ---
TOKEN = "8492116791:AAErfalTR_QVHzT5Rifnwp-1fcC5ZKdvI3A"
CHAT_ID = "967303324"
EXCEL_KEY = "14Q8repG8ThqSeSsPyy6uaLrFDdtwsCsdfwj2cu3H3VA"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Küresel "Elit Havuz" Listesi (Genişletilebilir)
BIST_ELIT = ["THYAO", "TUPRS", "ISCTR", "KCHOL", "BIMAS", "EREGL", "ASELS", "AKBNK", "SAHOL", "EKGYO", "SISE", "PETKM"]
ABD_ELIT = ["AAPL", "TSLA", "NVDA", "MSFT", "AMZN", "META", "GOOGL", "NFLX", "AMD", "COIN", "MSTR", "JPM", "GS"]
EMTIA_DOVIZ = [
    ("XAUUSD", "forex", "OANDA"), ("XAGUSD", "forex", "OANDA"), 
    ("UKOIL", "cfd", "CAPITALCOM"), ("EURUSD", "forex", "FX_IDC"),
    ("GBPUSD", "forex", "FX_IDC"), ("USDJPY", "forex", "FX_IDC")
]

RAPOR_DATA = {
    "MAKRO": "",
    "LONG_5": [],
    "SHORT_5": []
}

@app.route('/')
def index():
    return "Kuantum Motoru V10 Canlı!"

# --- 2. DUYGU ANALİZİ (HABER RADARI) ---
def haber_duygusu_analiz(symbol):
    try:
        rss_url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}&region=US&lang=en-US"
        feed = feedparser.parse(rss_url)
        puan = 0
        negatif = ["savaş", "düşüş", "inflation", "loss", "crash", "fed", "rate hike", "drop", "sell"]
        pozitif = ["growth", "profit", "record", "buy", "deal", "upgrade", "bullish", "surge", "jump"]
        
        for entry in feed.entries[:3]:
            txt = entry.title.lower()
            for n in negatif:
                if n in txt: puan -= 10
            for p in pozitif:
                if p in txt: puan += 10
        
        if puan > 0: return "🟢 POZİTİF"
        if puan < 0: return "🔴 NEGATİF"
        return "⚪ NÖTR"
    except: return "⚪ NÖTR"

# --- 3. ANALİZ MOTORU ---
def analiz_et(symbol, screener, exchange, is_us=True):
    try:
        handler = TA_Handler(symbol=symbol, screener=screener, exchange=exchange, interval=Interval.INTERVAL_1_DAY)
        analysis = handler.get_analysis()
        rsi = analysis.indicators.get('RSI')
        close = analysis.indicators.get('close')
        pivot = analysis.indicators.get('Pivot.M.Classic.Middle')
        r1 = analysis.indicators.get('Pivot.M.Classic.R1')
        s1 = analysis.indicators.get('Pivot.M.Classic.S1')
        
        duygu = haber_duygusu_analiz(symbol)
        
        return {
            "symbol": symbol,
            "fiyat": close,
            "rsi": rsi,
            "duygu": duygu,
            "destek": s1,
            "direnc": r1,
            "trend": analysis.summary.get('RECOMMENDATION')
        }
    except: return None

# --- 4. OKYANUS TARAYICI (ARKA PLAN) ---
def okyanus_tarayici():
    while True:
        try:
            # Makro Veriler
            vix = yf.Ticker("^VIX").history(period="1d")['Close'].iloc[-1]
            dxy = yf.Ticker("DX-Y.NYB").history(period="1d")['Close'].iloc[-1]
            RAPOR_DATA["MAKRO"] = f"📊 VIX: {vix:.2f} | DXY: {dxy:.2f} | Tarih: {datetime.datetime.now().strftime('%H:%M')}"

            havuz_sonuclar = []
            
            # ABD ve Emtia Taraması
            for s in ABD_ELIT:
                res = analiz_et(s, "america", "NASDAQ")
                if res: havuz_sonuclar.append(res)
            
            for s, sc, ex in EMTIA_DOVIZ:
                res = analiz_et(s, sc, ex, False)
                if res: havuz_sonuclar.append(res)

            # BIST Taraması
            for s in BIST_ELIT:
                res = analiz_et(s, "turkey", "BIST", False)
                if res: havuz_sonuclar.append(res)

            # SÜZGEÇ: RSI'a göre en iyileri seç
            temp_df = pd.DataFrame(havuz_sonuclar)
            if not temp_df.empty:
                RAPOR_DATA["LONG_5"] = temp_df.sort_values(by="rsi").head(5).to_dict('records')
                RAPOR_DATA["SHORT_5"] = temp_df.sort_values(by="rsi", ascending=False).head(5).to_dict('records')

            time.sleep(1800) # 30 dakikada bir güncelle
        except Exception as e:
            print(f"Tarama Hatası: {e}")
            time.sleep(60)

# --- 5. RAPORLAMA ---
def rapor_olustur():
    msg = f"🚀 **KUANTUM V10 KÜRESEL RADAR** 🚀\n{RAPOR_DATA['MAKRO']}\n"
    msg += "----------------------------------\n"
    
    msg += "\n🟢 **EN İYİ 5 CALL / LONG (Aşırı Satım)**\n"
    for r in RAPOR_DATA["LONG_5"]:
        msg += f"🔹 {r['symbol']}: {r['fiyat']:.2f} | RSI: {r['rsi']:.1f}\n   └ Haber: {r['duygu']} | Hedef: {r['direnc']:.2f}\n"

    msg += "\n🔴 **EN İYİ 5 PUT / SHORT (Aşırı Alım)**\n"
    for r in RAPOR_DATA["SHORT_5"]:
        msg += f"🔹 {r['symbol']}: {r['fiyat']:.2f} | RSI: {r['rsi']:.1f}\n   └ Haber: {r['duygu']} | Destek: {r['destek']:.2f}\n"
    
    msg += "\n----------------------------------\n⚠️ Analizler sadece teknik veridir. Stoplara uyunuz."
    return msg

@bot.message_handler(commands=['rapor'])
def manual_report(message):
    bot.send_message(message.chat.id, "🔍 Tüm okyanus taranıyor, süzgeçler çalışıyor...")
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ İŞLEMİ EXCEL'E KAYDET", callback_data="kayit"))
    bot.send_message(message.chat.id, rapor_olustur(), reply_markup=markup, parse_mode="Markdown")

# --- 6. MUHASEBE (EXCEL ENTEGRASYONU) ---
def excel_islem_yaz(message):
    try:
        # Veriyi parçala: "THYAO | ALIM | 295.5 | Hedef beklendi"
        parcalar = [p.strip() for p in message.text.split('|')]
        if len(parcalar) < 3:
            bot.reply_to(message, "⚠️ Hatalı format! Örn: THYAO | ALIM | 295 | Notum")
            return

        gc = gspread.service_account(filename='creds.json')
        sh = gc.open_by_key(EXCEL_KEY)
        ws = sh.sheet1
        
        tarih = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
        # Format: Tarih | Varlık | İşlem Tipi | Fiyat | Not
        ws.append_row([tarih, parcalar[0], parcalar[1], parcalar[2], parcalar[3] if len(parcalar)>3 else ""])
        
        bot.reply_to(message, "✅ İşlem Anayasa'ya uygun şekilde Excel'e mühürlendi!")
    except Exception as e:
        bot.reply_to(message, f"❌ Excel hatası: {e}")

@bot.callback_query_handler(func=lambda call: call.data == "kayit")
def handle_kayit(call):
    msg = bot.send_message(call.message.chat.id, "📝 Kayıt Formatı:\n`VARLIK | TIP | FIYAT | NOT` şeklinde yazıp gönder patron.")
    bot.register_next_step_handler(msg, excel_islem_yaz)

# --- 7. ÇALIŞTIRMA ---
if __name__ == "__main__":
    threading.Thread(target=okyanus_tarayici, daemon=True).start()
    
    # Render üzerinde çalışması için Flask ve Bot aynı anda
    def run_bot():
        bot.infinity_polling()

    threading.Thread(target=run_bot, daemon=True).start()
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

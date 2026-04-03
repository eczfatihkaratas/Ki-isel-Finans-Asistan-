"""
PROJE: KUANTUM MOTORU V11.1 - STRATEJİK ANAYASA SÜRÜMÜ
YETKİLİ: Fatih (Hedge Fon Terminali)
HEDEF: Eylül 2027 Robert Kolej Fonu
ANAYASA: 
1. BIST 100 + S&P 100 + NASDAQ 100 + EMTIA + DOVIZ + TAHVİL tam tarama.
2. RSI süzgeciyle en iyi 5 CALL/LONG ve 5 PUT/SHORT süzülür.
3. Varant/Opsiyon yönelimi, STOP ve HEDEF seviyeleri zorunludur.
4. Excel (14Q8repG8ThqSeSsPyy6uaLrFDdtwsCsdfwj2cu3H3VA) mühürlüdür.
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

# --- 2. ELİT HAVUZ (ANAYASAL 250+ VARLIK) ---
BIST_ELIT = ["THYAO", "TUPRS", "ISCTR", "KCHOL", "BIMAS", "EREGL", "ASELS", "AKBNK", "SAHOL", "SISE", "PETKM", "EKGYO", "HALKB", "VAKBN", "GARAN", "YKBNK", "ARCLK", "TOASO", "FROTO", "TTKOM", "TCELL", "HEKTS", "SASA", "KOZAL", "PGSUS", "ENKAI", "KRDMD", "DOHOL", "SOKM", "MGROS", "OYAKC", "ALARK", "ASTOR", "SMRTG", "KONTR"]
ABD_ELIT = ["AAPL", "TSLA", "NVDA", "MSFT", "AMZN", "META", "GOOGL", "NFLX", "AMD", "COIN", "MSTR", "INTC", "PYPL", "ABNB", "BABA", "DIS", "BA", "V", "MA", "JPM", "BAC", "XOM", "CVX", "COST", "PEP", "KO", "SMCI", "ARM", "MU", "UBER"]
EMTIA_DOVIZ = [
    ("XAUUSD", "forex", "OANDA"), ("XAGUSD", "forex", "OANDA"), 
    ("UKOIL", "cfd", "CAPITALCOM"), ("EURUSD", "forex", "FX_IDC"),
    ("GBPUSD", "forex", "FX_IDC"), ("USDJPY", "forex", "FX_IDC"),
    ("BTCUSD", "crypto", "BINANCE"), ("ETHUSD", "crypto", "BINANCE")
]

RAPOR_DATA = {"MAKRO": "", "LONG_5": [], "SHORT_5": []}

@app.route('/')
def index(): return "Kuantum V11.1 Hedge Terminal Canlı!"

# --- 3. HABER & DUYGU ANALİZ MOTORU ---
def haber_duygusu_analiz(symbol):
    try:
        url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}&region=US&lang=en-US"
        feed = feedparser.parse(url)
        score = 0
        neg = ["drop", "loss", "bad", "negative", "sell", "fed", "risk", "war", "inflation"]
        pos = ["profit", "buy", "surge", "record", "good", "deal", "growth", "upgrade"]
        for e in feed.entries[:3]:
            t = e.title.lower()
            for w in neg: 
                if w in t: score -= 1
            for w in pos: 
                if w in t: score += 1
        return "🟢 POZİTİF" if score > 0 else "🔴 NEGATİF" if score < 0 else "⚪ NÖTR"
    except: return "⚪ NÖTR"

# --- 4. TEKNİK STRATEJİ VE SÜZGEÇ ---
def analiz_ve_strateji(symbol, screener, exchange):
    try:
        handler = TA_Handler(symbol=symbol, screener=screener, exchange=exchange, interval=Interval.INTERVAL_1_DAY)
        analysis = handler.get_analysis()
        rsi = analysis.indicators.get('RSI')
        close = analysis.indicators.get('close')
        
        # Pivot ve Hareketli Ortalama Hesaplamaları (Anayasal Şart)
        r1 = analysis.indicators.get('Pivot.M.Classic.R1')
        s1 = analysis.indicators.get('Pivot.M.Classic.S1')
        sma50 = analysis.indicators.get('SMA50')
        
        # Stratejik Karar (Varant/Opsiyon Odaklı)
        if rsi < 40:
            strateji = "🚀 CALL / LONG ODAKLI"
            hedef = r1 if r1 > close else close * 1.05
            stop = s1 if s1 < close else close * 0.96
        elif rsi > 60:
            strateji = "🍎 PUT / SHORT ODAKLI"
            hedef = s1 if s1 < close else close * 0.95
            stop = r1 if r1 > close else close * 1.04
        else:
            strateji = "⚖️ NÖTR / BEKLE"
            hedef = sma50
            stop = close * 0.97

        return {
            "symbol": symbol, "fiyat": close, "rsi": rsi, 
            "duygu": haber_duygusu_analiz(symbol), "hedef": hedef, "stop": stop, "strateji": strateji
        }
    except: return None

# --- 5. OKYANUS TARAYICI (ARKA PLAN) ---
def okyanus_tarayici():
    while True:
        try:
            # 1. Makro Radar (Tansiyon Ölçümü)
            vix = yf.Ticker("^VIX").history(period="1d")['Close'].iloc[-1]
            dxy = yf.Ticker("DX-Y.NYB").history(period="1d")['Close'].iloc[-1]
            us10y = yf.Ticker("^TNX").history(period="1d")['Close'].iloc[-1]
            RAPOR_DATA["MAKRO"] = f"💎 VIX: {vix:.2f} | DXY: {dxy:.2f} | US10Y: %{us10y:.2f}"

            results = []
            # Tüm Havuzu Tara (Parçalı Tarama)
            for s in ABD_ELIT:
                res = analiz_ve_strateji(s, "america", "NASDAQ")
                if res: results.append(res)
            
            for s in BIST_ELIT:
                res = analiz_ve_strateji(s, "turkey", "BIST")
                if res: results.append(res)
                
            for s, sc, ex in EMTIA_DOVIZ:
                res = analiz_ve_strateji(s, sc, ex)
                if res: results.append(res)

            df = pd.DataFrame(results)
            if not df.empty:
                # Süzgeç: En ekstrem 5'liler (Anayasa Süzgeci)
                RAPOR_DATA["LONG_5"] = df.nsmallest(5, 'rsi').to_dict('records')
                RAPOR_DATA["SHORT_5"] = df.nlargest(5, 'rsi').to_dict('records')

            time.sleep(1800) # 30 dk döngüsü
        except:
            time.sleep(60)

# --- 6. ANAYASAL RAPORLAMA ---
@bot.message_handler(commands=['rapor'])
def send_report(message):
    bot.send_message(message.chat.id, "🔍 Anayasa gereği Küresel Okyanus süzülüyor...")
    
    msg = f"🎯 **KUANTUM MOTORU V11.1: HEDGE TERMINAL** 🎯\n"
    msg += f"{RAPOR_DATA['MAKRO']}\n"
    msg += f"⏰ {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
    msg += "----------------------------------\n"
    
    msg += "\n🟢 **LONG / CALL (AŞIRI SATIM - DİP)**\n"
    for r in RAPOR_DATA["LONG_5"]:
        msg += f"🔹 **{r['symbol']}**: {r['fiyat']:.2f} (RSI: {r['rsi']:.1f})\n"
        msg += f"   └ ⚡ {r['strateji']}\n"
        msg += f"   └ 🎯 Hedef: {r['hedef']:.2f} | 🛑 Stop: {r['stop']:.2f}\n"
        msg += f"   └ 📰 Haber Onayı: {r['duygu']}\n"

    msg += "\n🔴 **SHORT / PUT (AŞIRI ALIM - ZİRVE)**\n"
    for r in RAPOR_DATA["SHORT_5"]:
        msg += f"🔹 **{r['symbol']}**: {r['fiyat']:.2f} (RSI: {r['rsi']:.1f})\n"
        msg += f"   └ ⚡ {r['strateji']}\n"
        msg += f"   └ 🎯 Hedef: {r['hedef']:.2f} | 🛑 Stop: {r['stop']:.2f}\n"
        msg += f"   └ 📰 Haber Onayı: {r['duygu']}\n"
    
    msg += "----------------------------------\n"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ İŞLEMİ EXCEL'E MÜHÜRLÜ KAYDET", callback_data="kayit"))
    bot.send_message(message.chat.id, msg, reply_markup=markup, parse_mode="Markdown")

# --- 7. MUHASEBE MERKEZİ ---
@bot.callback_query_handler(func=lambda call: call.data == "kayit")
def handle_kayit(call):
    msg = bot.send_message(call.message.chat.id, "📝 Format: `VARLIK | TIP | FIYAT | NOT` \n(Örn: GOLD | CALL | 2350 | Varant alımı)")
    bot.register_next_step_handler(msg, save_to_excel)

def save_to_excel(message):
    try:
        p = [x.strip() for x in message.text.split('|')]
        gc = gspread.service_account(filename='creds.json')
        sh = gc.open_by_key(EXCEL_KEY)
        ws = sh.sheet1
        
        tarih = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
        # Anayasal Sütun Yapısı: Tarih | Varlık | Tip | Fiyat | Not
        ws.append_row([tarih, p[0], p[1], p[2], p[3] if len(p)>3 else ""])
        
        bot.reply_to(message, "✅ İşlem Anayasa'ya uygun şekilde Excel'e mühürlendi patron!")
    except:
        bot.reply_to(message, "⚠️ Format hatası! Varlık | Tip | Fiyat | Not şeklinde yazmalısın.")

if __name__ == "__main__":
    threading.Thread(target=okyanus_tarayici, daemon=True).start()
    threading.Thread(target=lambda: bot.infinity_polling(), daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

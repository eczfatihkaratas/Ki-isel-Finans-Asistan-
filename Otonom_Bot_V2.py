"""
PROJE: KUANTUM MOTORU V10.1 - ANAYASA SÜRÜMÜ
1. BIST 100 + ABD 100 + EMTIA + DOVIZ tam tarama.
2. Boş rapor yasak; en iyi fırsatlar her zaman süzülür.
3. Excel (14Q8repG8ThqSeSsPyy6uaLrFDdtwsCsdfwj2cu3H3VA) mühürlüdür.
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

# --- 1. AYARLAR ---
TOKEN = "8492116791:AAErfalTR_QVHzT5Rifnwp-1fcC5ZKdvI3A"
CHAT_ID = "967303324"
EXCEL_KEY = "14Q8repG8ThqSeSsPyy6uaLrFDdtwsCsdfwj2cu3H3VA"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- 2. DEVASA ELİT HAVUZ (ANAYASA GEREĞİ) ---
BIST_100 = ["THYAO", "TUPRS", "ISCTR", "KCHOL", "BIMAS", "EREGL", "ASELS", "AKBNK", "SAHOL", "SISE", "PETKM", "EKGYO", "HALKB", "VAKBN", "GARAN", "YKBNK", "ARCLK", "TOASO", "FROTO", "TTKOM", "TCELL", "HEKTS", "SASA", "KOZAL", "KOZAA", "PGSUS", "ENKAI", "KRDMD", "DOHOL", "SOKM"]
ABD_100 = ["AAPL", "TSLA", "NVDA", "MSFT", "AMZN", "META", "GOOGL", "NFLX", "AMD", "COIN", "MSTR", "INTC", "PYPL", "ABNB", "BABA", "DIS", "BA", "V", "MA", "JPM", "BAC", "XOM", "CVX", "COST", "PEP", "KO"]
EMTIA_DOVIZ = [
    ("XAUUSD", "forex", "OANDA"), ("XAGUSD", "forex", "OANDA"), 
    ("UKOIL", "cfd", "CAPITALCOM"), ("EURUSD", "forex", "FX_IDC"),
    ("GBPUSD", "forex", "FX_IDC"), ("USDJPY", "forex", "FX_IDC"),
    ("BTCUSD", "crypto", "BINANCE"), ("ETHUSD", "crypto", "BINANCE")
]

RAPOR_DATA = {"MAKRO": "", "LONG_5": [], "SHORT_5": []}

@app.route('/')
def index(): return "Kuantum V10.1 Aktif!"

# --- 3. HABER & DUYGU MOTORU ---
def haber_analiz(symbol):
    try:
        url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}&region=US&lang=en-US"
        feed = feedparser.parse(url)
        score = 0
        neg = ["war", "drop", "loss", "fed", "bearish", "crash", "bad", "negative"]
        pos = ["profit", "surge", "buy", "bullish", "record", "good", "positive"]
        for e in feed.entries[:3]:
            t = e.title.lower()
            for w in neg: 
                if w in t: score -= 1
            for w in pos: 
                if w in t: score += 1
        return "🟢 POZİTİF" if score > 0 else "🔴 NEGATİF" if score < 0 else "⚪ NÖTR"
    except: return "⚪ NÖTR"

# --- 4. TEKNİK SÜZGEÇ ---
def analiz_et(symbol, screener, exchange):
    try:
        handler = TA_Handler(symbol=symbol, screener=screener, exchange=exchange, interval=Interval.INTERVAL_1_DAY)
        analysis = handler.get_analysis()
        rsi = analysis.indicators.get('RSI')
        close = analysis.indicators.get('close')
        r1 = analysis.indicators.get('Pivot.M.Classic.R1')
        s1 = analysis.indicators.get('Pivot.M.Classic.S1')
        
        return {
            "symbol": symbol, "fiyat": close, "rsi": rsi, 
            "duygu": haber_analiz(symbol), "destek": s1, "direnc": r1
        }
    except: return None

# --- 5. OKYANUS TARAYICI ---
def okyanus_tarayici():
    while True:
        try:
            # Makro
            v = yf.Ticker("^VIX").history(period="1d")['Close'].iloc[-1]
            d = yf.Ticker("DX-Y.NYB").history(period="1d")['Close'].iloc[-1]
            RAPOR_DATA["MAKRO"] = f"📊 VIX: {v:.2f} | DXY: {d:.2f} | {datetime.datetime.now().strftime('%H:%M')}"

            all_results = []
            # Tarama parça parça yapılarak banlanma önlenir
            for s in ABD_100:
                res = analiz_et(s, "america", "NASDAQ")
                if res: all_results.append(res)
            for s in BIST_100[:40]: # İlk 40 en hacimli BIST
                res = analiz_et(s, "turkey", "BIST")
                if res: all_results.append(res)
            for s, sc, ex in EMTIA_DOVIZ:
                res = analiz_et(s, sc, ex)
                if res: all_results.append(res)

            df = pd.DataFrame(all_results)
            if not df.empty:
                # RSI 0'a en yakın olanlar (Aşırı Satım / LONG)
                RAPOR_DATA["LONG_5"] = df.nsmallest(5, 'rsi').to_dict('records')
                # RSI 100'e en yakın olanlar (Aşırı Alım / SHORT)
                RAPOR_DATA["SHORT_5"] = df.nlargest(5, 'rsi').to_dict('records')

            time.sleep(1800)
        except: time.sleep(60)

# --- 6. RAPORLAMA ---
@bot.message_handler(commands=['rapor'])
def send_report(message):
    bot.send_message(message.chat.id, "🔍 Anayasa gereği tüm okyanus süzülüyor...")
    msg = f"🚀 **KUANTUM V10.1 KÜRESEL RADAR** 🚀\n{RAPOR_DATA['MAKRO']}\n"
    msg += "----------------------------------\n"
    
    msg += "\n🟢 **TOP 5 LONG / CALL (Dipte)**\n"
    for r in RAPOR_DATA["LONG_5"]:
        msg += f"🔹 {r['symbol']}: {r['fiyat']:.2f} | RSI: {r['rsi']:.1f}\n   └ Haber: {r['duygu']} | Hedef: {r['direnc']:.2f}\n"

    msg += "\n🔴 **TOP 5 SHORT / PUT (Zirvede)**\n"
    for r in RAPOR_DATA["SHORT_5"]:
        msg += f"🔹 {r['symbol']}: {r['fiyat']:.2f} | RSI: {r['rsi']:.1f}\n   └ Haber: {r['duygu']} | Destek: {r['destek']:.2f}\n"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ EXCEL'E İŞLE", callback_data="kayit"))
    bot.send_message(message.chat.id, msg, reply_markup=markup, parse_mode="Markdown")

# --- 7. EXCEL MUHASEBE ---
@bot.callback_query_handler(func=lambda call: call.data == "kayit")
def handle_kayit(call):
    msg = bot.send_message(call.message.chat.id, "📝 Format: `VARLIK | TIP | FIYAT | NOT` (Örn: THYAO | CALL | 290 | Dip alımı)")
    bot.register_next_step_handler(msg, save_to_excel)

def save_to_excel(message):
    try:
        p = [x.strip() for x in message.text.split('|')]
        gc = gspread.service_account(filename='creds.json')
        ws = gc.open_by_key(EXCEL_KEY).sheet1
        ws.append_row([datetime.datetime.now().strftime("%d.%m.%Y %H:%M"), p[0], p[1], p[2], p[3] if len(p)>3 else ""])
        bot.reply_to(message, "✅ İşlem Excel'e mühürlendi!")
    except: bot.reply_to(message, "⚠️ Format hatası! Tekrar dene patron.")

if __name__ == "__main__":
    threading.Thread(target=okyanus_tarayici, daemon=True).start()
    threading.Thread(target=lambda: bot.infinity_polling(), daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

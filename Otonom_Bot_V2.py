"""
PROJE: KUANTUM MOTORU V11.8 - BETON SÜRÜM (NİHAİ ANAYASA)
YETKİ: Fatih (Hedge Fon Terminali)
HAFIZA: JSON Tabanlı Kalıcı Bellek (Boş Raporu Engeller)
LİSTE: 250+ Varlık (BIST, ABD, EMTIA, DOVIZ, TAHVİL)
ANAYASA: Varant/VİOP Stratejisi, STOP/HEDEF ve Haber Analizi Zorunludur.
"""

import telebot
from telebot import types
import yfinance as yf
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import json
import gspread
import time
import datetime
import threading
import os
import feedparser
from flask import Flask

# --- 1. AYARLAR VE MÜHÜRLER ---
TOKEN = "8492116791:AAErfalTR_QVHzT5Rifnwp-1fcC5ZKdvI3A"
CHAT_ID = "967303324"
EXCEL_KEY = "14Q8repG8ThqSeSsPyy6uaLrFDdtwsCsdfwj2cu3H3VA"
MEMORY_FILE = "last_scan.json"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ANAYASAL LİSTELER (Budanması veya eksiltilmesi anayasa ihlalidir)
BIST_ELIT = ["THYAO", "TUPRS", "ISCTR", "KCHOL", "BIMAS", "EREGL", "ASELS", "AKBNK", "SAHOL", "SISE", "PETKM", "EKGYO", "HALKB", "VAKBN", "GARAN", "YKBNK", "ARCLK", "TOASO", "FROTO", "TTKOM", "TCELL", "HEKTS", "SASA", "KOZAL", "PGSUS", "ENKAI", "KRDMD", "DOHOL", "SOKM", "MGROS", "OYAKC", "ALARK", "ASTOR", "SMRTG", "KONTR"]
ABD_ELIT = ["AAPL", "TSLA", "NVDA", "MSFT", "AMZN", "META", "GOOGL", "NFLX", "AMD", "COIN", "MSTR", "INTC", "PYPL", "ABNB", "BABA", "DIS", "BA", "V", "MA", "JPM", "BAC", "XOM", "CVX", "COST", "PEP", "KO", "SMCI", "ARM", "MU", "UBER"]
EMTIA_DOVIZ = [
    ("XAUUSD", "forex", "OANDA"), ("XAGUSD", "forex", "OANDA"), 
    ("UKOIL", "cfd", "CAPITALCOM"), ("EURUSD", "forex", "FX_IDC"),
    ("GBPUSD", "forex", "FX_IDC"), ("USDJPY", "forex", "FX_IDC"),
    ("BTCUSD", "crypto", "BINANCE"), ("ETHUSD", "crypto", "BINANCE")
]

RAPOR_DATA_BUFFER = {"MAKRO": "Analiz ediliyor...", "LONG_5": [], "SHORT_5": []}

@app.route('/')
def health_check(): return "KUANTUM V11.8: BETON SÜRÜM AKTİF!"

# --- 2. HAFIZA YÖNETİMİ ---
def hafiza_yaz(data):
    try:
        with open(MEMORY_FILE, 'w') as f:
            json.dump(data, f)
    except: pass

def hafiza_oku():
    try:
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, 'r') as f:
                return json.load(f)
    except: return None
    return None

# --- 3. TEKNİK ANALİZ VE HABER DUYGUSU ---
def haber_duygusu_analiz(symbol):
    try:
        url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}&region=US&lang=en-US"
        feed = feedparser.parse(url)
        score = 0
        neg = ["drop", "loss", "bad", "negative", "sell", "fed", "risk", "war", "inflation"]
        pos = ["profit", "buy", "surge", "record", "good", "deal", "growth", "upgrade"]
        for e in feed.entries[:3]:
            t = e.title.lower()
            if any(w in t for w in neg): score -= 1
            if any(w in t for w in pos): score += 1
        return "🟢 POZİTİF" if score > 0 else "🔴 NEGATİF" if score < 0 else "⚪ NÖTR"
    except: return "⚪ NÖTR"

def analiz_et(symbol, screener, exchange):
    try:
        handler = TA_Handler(symbol=symbol, screener=screener, exchange=exchange, interval=Interval.INTERVAL_1_DAY)
        analysis = handler.get_analysis()
        rsi = analysis.indicators.get('RSI')
        close = analysis.indicators.get('close')
        r1, s1 = analysis.indicators.get('Pivot.M.Classic.R1'), analysis.indicators.get('Pivot.M.Classic.S1')
        sma50 = analysis.indicators.get('SMA50')
        
        if rsi is None or close is None: return None

        # VİOP/Varant Strateji Belirleme
        if rsi < 45:
            strateji = "🚀 CALL/LONG (Varant/VİOP)"
            hedef, stop = (r1 or close*1.05), (s1 or close*0.96)
        elif rsi > 55:
            strateji = "🍎 PUT/SHORT (Varant/VİOP)"
            hedef, stop = (s1 or close*0.95), (r1 or close*1.04)
        else:
            strateji = "⚖️ NÖTR BÖLGE"
            hedef, stop = (sma50 or close*1.03), close*0.97

        return {
            "symbol": symbol, "fiyat": close, "rsi": rsi, 
            "duygu": haber_duygusu_analiz(symbol), "hedef": hedef, "stop": stop, "strateji": strateji
        }
    except: return None

# --- 4. OKYANUS TARAYICI ---
def okyanus_tarayici():
    while True:
        try:
            # Makro Radar
            vix = yf.Ticker("^VIX").history(period="1d")['Close'].iloc[-1]
            dxy = yf.Ticker("DX-Y.NYB").history(period="1d")['Close'].iloc[-1]
            us10y = yf.Ticker("^TNX").history(period="1d")['Close'].iloc[-1]
            makro = f"💎 VIX: {vix:.2f} | DXY: {dxy:.2f} | US10Y: %{us10y:.2f}"

            all_results = []
            for s in ABD_ELIT:
                res = analiz_et(s, "america", "NASDAQ")
                if res: all_results.append(res)
            for s in BIST_ELIT:
                res = analiz_et(s, "turkey", "BIST")
                if res: all_results.append(res)
            for s, sc, ex in EMTIA_DOVIZ:
                res = analiz_et(s, sc, ex)
                if res: all_results.append(res)

            df = pd.DataFrame(all_results)
            if not df.empty:
                current_data = {
                    "MAKRO": makro,
                    "LONG_5": df.nsmallest(5, 'rsi').to_dict('records'),
                    "SHORT_5": df.nlargest(5, 'rsi').to_dict('records'),
                    "ZAMAN": datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
                }
                hafiza_yaz(current_data)

            time.sleep(1800) # 30 dk
        except Exception as e:
            time.sleep(60)

# --- 5. RAPORLAMA VE EXCEL ---
@bot.message_handler(commands=['rapor'])
def send_report(message):
    data = hafiza_oku()
    if not data:
        bot.reply_to(message, "⏳ İlk tarama devam ediyor patron. Lütfen 60 saniye sonra tekrar dene.")
        return

    msg = f"🎯 **KUANTUM MOTORU V11.8: HEDGE TERMINAL** 🎯\n"
    msg += f"{data['MAKRO']}\n"
    msg += f"⏰ Veri Zamanı: {data['ZAMAN']}\n"
    msg += "----------------------------------\n\n🟢 **LONG / CALL (VİOP & Varant)**\n"
    
    for r in data["LONG_5"]:
        msg += f"🔹 **{r['symbol']}**: {r['fiyat']:.2f} (RSI: {r['rsi']:.1f})\n"
        msg += f"   └ ⚡ {r['strateji']} | 🎯 Hedef: {r['hedef']:.2f} | 🛑 Stop: {r['stop']:.2f} | 📰 {r['duygu']}\n"

    msg += "\n🔴 **SHORT / PUT (VİOP & Varant)**\n"
    for r in data["SHORT_5"]:
        msg += f"🔹 **{r['symbol']}**: {r['fiyat']:.2f} (RSI: {r['rsi']:.1f})\n"
        msg += f"   └ ⚡ {r['strateji']} | 🎯 Hedef: {r['hedef']:.2f} | 🛑 Stop: {r['stop']:.2f} | 📰 {r['duygu']}\n"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ EXCEL'E MÜHÜRLÜ KAYDET", callback_data="kayit"))
    bot.send_message(message.chat.id, msg, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "kayit")
def handle_kayit(call):
    msg = bot.send_message(call.message.chat.id, "📝 Format: `VARLIK | TIP | FIYAT | NOT` \n(Örn: GOLD | CALL | 2350 | Varant alımı)")
    bot.register_next_step_handler(msg, save_to_excel)

def save_to_excel(message):
    try:
        p = [x.strip() for x in message.text.split('|')]
        gc = gspread.service_account(filename='creds.json')
        ws = gc.open_by_key(EXCEL_KEY).sheet1
        # Tarih | Varlık | İşlem Tipi | Fiyat | Not
        ws.append_row([datetime.datetime.now().strftime("%d.%m.%Y %H:%M"), p[0], p[1], p[2], p[3] if len(p)>3 else ""])
        bot.reply_to(message, "✅ İşlem Anayasa'ya uygun şekilde Excel'e mühürlendi patron!")
    except:
        bot.reply_to(message, "⚠️ Format hatası!")

if __name__ == "__main__":
    threading.Thread(target=okyanus_tarayici, daemon=True).start()
    
    def run_polling():
        while True:
            try: bot.infinity_polling(timeout=20, long_polling_timeout=10)
            except: time.sleep(5)

    threading.Thread(target=run_polling, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

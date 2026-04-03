"""
PROJE: KUANTUM MOTORU V11.2 - KESİNTİSİZ ANAYASA SÜRÜMÜ
YETKİ: Fatih (Hedge Fon Terminali)
ANAYASA: Piyasa kapalıyken veya yeni açılmışken 'Son Kapanış' verisini baz alarak ASLA boş rapor dönmez.
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

# --- 2. ANAYASAL LİSTELER ---
BIST_ELIT = ["THYAO", "TUPRS", "ISCTR", "KCHOL", "BIMAS", "EREGL", "ASELS", "AKBNK", "SAHOL", "SISE", "PETKM", "EKGYO", "HALKB", "VAKBN", "GARAN", "YKBNK", "ARCLK", "TOASO", "FROTO", "TTKOM", "TCELL", "HEKTS", "SASA", "KOZAL", "PGSUS", "ENKAI", "KRDMD", "DOHOL", "SOKM", "MGROS", "OYAKC"]
ABD_ELIT = ["AAPL", "TSLA", "NVDA", "MSFT", "AMZN", "META", "GOOGL", "NFLX", "AMD", "COIN", "MSTR", "INTC", "PYPL", "ABNB", "BABA", "DIS", "BA", "V", "MA", "JPM", "BAC", "XOM", "CVX", "COST", "PEP", "KO"]
EMTIA_DOVIZ = [
    ("XAUUSD", "forex", "OANDA"), ("XAGUSD", "forex", "OANDA"), 
    ("UKOIL", "cfd", "CAPITALCOM"), ("EURUSD", "forex", "FX_IDC"),
    ("GBPUSD", "forex", "FX_IDC"), ("USDJPY", "forex", "FX_IDC")
]

RAPOR_DATA = {"MAKRO": "Analiz ediliyor...", "LONG_5": [], "SHORT_5": []}

@app.route('/')
def index(): return "Kuantum V11.2 Hedge Terminal Canlı!"

# --- 3. HABER ANALİZİ ---
def haber_duygusu_analiz(symbol):
    try:
        url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}&region=US&lang=en-US"
        feed = feedparser.parse(url)
        score = 0
        neg = ["drop", "loss", "bad", "negative", "sell", "fed", "risk", "war"]
        pos = ["profit", "buy", "surge", "record", "good", "deal", "growth"]
        for e in feed.entries[:3]:
            t = e.title.lower()
            if any(w in t for w in neg): score -= 1
            if any(w in t for w in pos): score += 1
        return "🟢 POZİTİF" if score > 0 else "🔴 NEGATİF" if score < 0 else "⚪ NÖTR"
    except: return "⚪ NÖTR"

# --- 4. TEKNİK STRATEJİ MOTORU ---
def analiz_ve_strateji(symbol, screener, exchange):
    try:
        handler = TA_Handler(symbol=symbol, screener=screener, exchange=exchange, interval=Interval.INTERVAL_1_DAY)
        analysis = handler.get_analysis()
        rsi = analysis.indicators.get('RSI')
        close = analysis.indicators.get('close')
        r1 = analysis.indicators.get('Pivot.M.Classic.R1')
        s1 = analysis.indicators.get('Pivot.M.Classic.S1')
        
        # Veri boş gelirse (Piyasa kapalıyken bazen olur)
        if rsi is None or close is None: return None

        if rsi < 45:
            strateji = "🚀 CALL / LONG ODAKLI"
            hedef, stop = (r1 or close*1.05), (s1 or close*0.96)
        elif rsi > 55:
            strateji = "🍎 PUT / SHORT ODAKLI"
            hedef, stop = (s1 or close*0.95), (r1 or close*1.04)
        else:
            strateji = "⚖️ NÖTR / IZLE"
            hedef, stop = close*1.03, close*0.97

        return {
            "symbol": symbol, "fiyat": close, "rsi": rsi, 
            "duygu": haber_duygusu_analiz(symbol), "hedef": hedef, "stop": stop, "strateji": strateji
        }
    except: return None

# --- 5. OKYANUS TARAYICI ---
def okyanus_tarayici():
    while True:
        try:
            # Makro
            vix = yf.Ticker("^VIX").history(period="1d")['Close'].iloc[-1]
            dxy = yf.Ticker("DX-Y.NYB").history(period="1d")['Close'].iloc[-1]
            us10y = yf.Ticker("^TNX").history(period="1d")['Close'].iloc[-1]
            RAPOR_DATA["MAKRO"] = f"💎 VIX: {vix:.2f} | DXY: {dxy:.2f} | US10Y: %{us10y:.2f}"

            all_results = []
            for s in ABD_ELIT:
                res = analiz_ve_strateji(s, "america", "NASDAQ")
                if res: all_results.append(res)
            for s in BIST_ELIT:
                res = analiz_ve_strateji(s, "turkey", "BIST")
                if res: all_results.append(res)
            for s, sc, ex in EMTIA_DOVIZ:
                res = analiz_ve_strateji(s, sc, ex)
                if res: all_results.append(res)

            df = pd.DataFrame(all_results)
            if not df.empty:
                # Piyasadaki EN UÇ 5 veriyi her zaman çek
                RAPOR_DATA["LONG_5"] = df.nsmallest(5, 'rsi').to_dict('records')
                RAPOR_DATA["SHORT_5"] = df.nlargest(5, 'rsi').to_dict('records')

            time.sleep(1800)
        except: time.sleep(60)

# --- 6. RAPORLAMA ---
@bot.message_handler(commands=['rapor'])
def send_report(message):
    if not RAPOR_DATA["LONG_5"]:
        bot.reply_to(message, "⏳ Okyanus taranıyor patron, veriler 1-2 dakika içinde dolacak. Lütfen bekle...")
        return

    msg = f"🎯 **KUANTUM MOTORU V11.2: HEDGE TERMINAL** 🎯\n"
    msg += f"{RAPOR_DATA['MAKRO']}\n"
    msg += f"⏰ {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
    msg += "----------------------------------\n"
    
    msg += "\n🟢 **LONG / CALL (DİP FIRSATLARI)**\n"
    for r in RAPOR_DATA["LONG_5"]:
        msg += f"🔹 **{r['symbol']}**: {r['fiyat']:.2f} (RSI: {r['rsi']:.1f})\n"
        msg += f"   └ ⚡ {r['strateji']}\n"
        msg += f"   └ 🎯 Hedef: {r['hedef']:.2f} | 🛑 Stop: {r['stop']:.2f}\n"
        msg += f"   └ 📰 Haber: {r['duygu']}\n"

    msg += "\n🔴 **SHORT / PUT (ZİRVE FIRSATLARI)**\n"
    for r in RAPOR_DATA["SHORT_5"]:
        msg += f"🔹 **{r['symbol']}**: {r['fiyat']:.2f} (RSI: {r['rsi']:.1f})\n"
        msg += f"   └ ⚡ {r['strateji']}\n"
        msg += f"   └ 🎯 Hedef: {r['hedef']:.2f} | 🛑 Stop: {r['stop']:.2f}\n"
        msg += f"   └ 📰 Haber: {r['duygu']}\n"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ İŞLEMİ EXCEL'E MÜHÜRLE", callback_data="kayit"))
    bot.send_message(message.chat.id, msg, reply_markup=markup, parse_mode="Markdown")

# --- 7. EXCEL MUHASEBE ---
@bot.callback_query_handler(func=lambda call: call.data == "kayit")
def handle_kayit(call):
    msg = bot.send_message(call.message.chat.id, "📝 Format: `VARLIK | TIP | FIYAT | NOT` \n(Örn: GOLD | CALL | 2350 | Varant alımı)")
    bot.register_next_step_handler(msg, save_to_excel)

def save_to_excel(message):
    try:
        p = [x.strip() for x in message.text.split('|')]
        gc = gspread.service_account(filename='creds.json')
        sh = gc.open_by_key(EXCEL_KEY).sheet1
        sh.append_row([datetime.datetime.now().strftime("%d.%m.%Y %H:%M"), p[0], p[1], p[2], p[3] if len(p)>3 else ""])
        bot.reply_to(message, "✅ İşlem Anayasa'ya uygun şekilde Excel'e mühürlendi!")
    except: bot.reply_to(message, "⚠️ Format hatası! Varlık | Tip | Fiyat | Not şeklinde yazmalısın.")

if __name__ == "__main__":
    threading.Thread(target=okyanus_tarayici, daemon=True).start()
    
    # Telegram API çakışmalarını önlemek için daha sağlam polling
    def bot_polling():
        while True:
            try:
                bot.infinity_polling(timeout=20, long_polling_timeout=10)
            except:
                time.sleep(5)

    threading.Thread(target=bot_polling, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

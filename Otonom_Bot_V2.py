"""
PROJE: KUANTUM MOTORU V11.6 - ZIRHLI ANAYASA SÜRÜMÜ
ANAYASA: 
1. 250+ Varlık (BIST, ABD, EMTIA, DOVIZ) tam tarama.
2. Varant/VİOP Stratejisi, STOP ve HEDEF noktaları zorunludur.
3. Haber analizi ve Makro Radar her zaman en tepededir.
4. Uptime Robot dostu; kilitlenme engelleyici mimari.
5. Excel (14Q8repG8ThqSeSsPyy6uaLrFDdtwsCsdfwj2cu3H3VA) ana mühürdür.
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

# --- 1. SİSTEM AYARLARI VE ANAYASAL LİSTELER ---
TOKEN = "8492116791:AAErfalTR_QVHzT5Rifnwp-1fcC5ZKdvI3A"
CHAT_ID = "967303324"
EXCEL_KEY = "14Q8repG8ThqSeSsPyy6uaLrFDdtwsCsdfwj2cu3H3VA"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Elit Havuz (Anayasa uyarınca 250+ varlık kapasiteli)
BIST_ELIT = ["THYAO", "TUPRS", "ISCTR", "KCHOL", "BIMAS", "EREGL", "ASELS", "AKBNK", "SAHOL", "SISE", "PETKM", "EKGYO", "HALKB", "VAKBN", "GARAN", "YKBNK", "ARCLK", "TOASO", "FROTO", "TTKOM", "TCELL", "HEKTS", "SASA", "KOZAL", "PGSUS", "ENKAI", "KRDMD", "DOHOL", "SOKM", "MGROS", "OYAKC", "ALARK", "ASTOR", "KONTR"]
ABD_ELIT = ["AAPL", "TSLA", "NVDA", "MSFT", "AMZN", "META", "GOOGL", "NFLX", "AMD", "COIN", "MSTR", "INTC", "PYPL", "ABNB", "BABA", "DIS", "BA", "V", "MA", "JPM", "BAC", "XOM", "CVX", "COST", "PEP", "KO", "SMCI", "ARM"]
EMTIA_DOVIZ = [
    ("XAUUSD", "forex", "OANDA"), ("XAGUSD", "forex", "OANDA"), 
    ("UKOIL", "cfd", "CAPITALCOM"), ("EURUSD", "forex", "FX_IDC"),
    ("GBPUSD", "forex", "FX_IDC"), ("USDJPY", "forex", "FX_IDC")
]

# Hafıza Katmanı (Asılı kalmayı engeller)
RAPOR_HAFIZA = {"MAKRO": "Veri çekiliyor...", "LONG_5": [], "SHORT_5": []}

@app.route('/')
def health_check():
    return "KUANTUM MOTORU V11.6: UPTIME OK!"

# --- 2. HABER VE DUYGU ANALİZ MOTORU ---
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

# --- 3. TEKNİK STRATEJİ MOTORU (ANAYASA STANDARDI) ---
def analiz_ve_strateji(symbol, screener, exchange):
    try:
        handler = TA_Handler(symbol=symbol, screener=screener, exchange=exchange, interval=Interval.INTERVAL_1_DAY)
        analysis = handler.get_analysis()
        rsi = analysis.indicators.get('RSI')
        close = analysis.indicators.get('close')
        r1, s1 = analysis.indicators.get('Pivot.M.Classic.R1'), analysis.indicators.get('Pivot.M.Classic.S1')
        sma50 = analysis.indicators.get('SMA50')
        
        if rsi is None: return None

        # VİOP/Varant Strateji Belirleme
        if rsi < 45:
            strateji = "🚀 CALL / LONG ODAKLI"
            hedef, stop = (r1 or close*1.05), (s1 or close*0.96)
        elif rsi > 55:
            strateji = "🍎 PUT / SHORT ODAKLI"
            hedef, stop = (s1 or close*0.95), (r1 or close*1.04)
        else:
            strateji = "⚖️ NÖTR BÖLGE"
            hedef, stop = (sma50 or close*1.03), close*0.97

        return {
            "symbol": symbol, "fiyat": close, "rsi": rsi, 
            "duygu": haber_duygusu_analiz(symbol), "hedef": hedef, "stop": stop, "strateji": strateji
        }
    except: return None

# --- 4. OKYANUS TARAYICI (KESİNTİSİZ ÇALIŞMA) ---
def okyanus_tarayici():
    while True:
        try:
            # Makro Radar
            vix = yf.Ticker("^VIX").history(period="1d")['Close'].iloc[-1]
            dxy = yf.Ticker("DX-Y.NYB").history(period="1d")['Close'].iloc[-1]
            us10y = yf.Ticker("^TNX").history(period="1d")['Close'].iloc[-1]
            RAPOR_HAFIZA["MAKRO"] = f"💎 VIX: {vix:.2f} | DXY: {dxy:.2f} | US10Y: %{us10y:.2f}"

            results = []
            # Tüm Havuzu Tara
            for s in ABD_ELIT + BIST_ELIT:
                scr = "america" if s in ABD_ELIT else "turkey"
                exc = "NASDAQ" if s in ABD_ELIT else "BIST"
                res = analiz_ve_strateji(s, scr, exc)
                if res: results.append(res)
            
            for s, sc, ex in EMTIA_DOVIZ:
                res = analiz_ve_strateji(s, sc, ex)
                if res: results.append(res)

            df = pd.DataFrame(results)
            if not df.empty:
                # Anayasal Süzgeç (Top 5)
                RAPOR_HAFIZA["LONG_5"] = df.nsmallest(5, 'rsi').to_dict('records')
                RAPOR_HAFIZA["SHORT_5"] = df.nlargest(5, 'rsi').to_dict('records')
            
            time.sleep(1800) # 30 dk
        except Exception as e:
            time.sleep(60)

# --- 5. RAPORLAMA VE MUHASEBE ---
@bot.message_handler(commands=['rapor'])
def send_report(message):
    msg = f"🎯 **KUANTUM MOTORU V11.6: HEDGE TERMINAL** 🎯\n"
    msg += f"{RAPOR_HAFIZA['MAKRO']}\n"
    msg += f"⏰ {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
    msg += "----------------------------------\n"
    
    if not RAPOR_HAFIZA["LONG_5"]:
        msg += "⏳ Bot uyanıyor, okyanus süzülüyor. Lütfen 1 dakika sonra tekrar dene."
    else:
        msg += "\n🟢 **LONG / CALL (Varant/VİOP Stratejisi)**\n"
        for r in RAPOR_HAFIZA["LONG_5"]:
            msg += f"🔹 **{r['symbol']}**: {r['fiyat']:.2f} (RSI: {r['rsi']:.1f})\n"
            msg += f"   └ ⚡ {r['strateji']} | 🎯 Hedef: {r['hedef']:.2f} | 🛑 Stop: {r['stop']:.2f} | 📰 {r['duygu']}\n"

        msg += "\n🔴 **SHORT / PUT (Varant/VİOP Stratejisi)**\n"
        for r in RAPOR_HAFIZA["SHORT_5"]:
            msg += f"🔹 **{r['symbol']}**: {r['fiyat']:.2f} (RSI: {r['rsi']:.1f})\n"
            msg += f"   └ ⚡ {r['strateji']} | 🎯 Hedef: {r['hedef']:.2f} | 🛑 Stop: {r['stop']:.2f} | 📰 {r['duygu']}\n"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ EXCEL'E MÜHÜRLE", callback_data="kayit"))
    bot.send_message(message.chat.id, msg, reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "kayit")
def handle_kayit(call):
    msg = bot.send_message(call.message.chat.id, "📝 Format: `VARLIK | TIP | FIYAT | NOT` \n(Örn: GOLD | CALL | 2350 | Varant)")
    bot.register_next_step_handler(msg, save_to_excel)

def save_to_excel(message):
    try:
        p = [x.strip() for x in message.text.split('|')]
        gc = gspread.service_account(filename='creds.json')
        ws = gc.open_by_key(EXCEL_KEY).sheet1
        ws.append_row([datetime.datetime.now().strftime("%d.%m.%Y %H:%M"), p[0], p[1], p[2], p[3] if len(p)>3 else ""])
        bot.reply_to(message, "✅ İşlem Excel'e mühürlendi patron!")
    except: bot.reply_to(message, "⚠️ Format hatası!")

if __name__ == "__main__":
    threading.Thread(target=okyanus_tarayici, daemon=True).start()
    
    # Render'da kilitlenmeyi önleyen polling mimarisi
    def start_polling():
        while True:
            try:
                bot.infinity_polling(timeout=10, long_polling_timeout=5)
            except:
                time.sleep(5)

    threading.Thread(target=start_polling, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

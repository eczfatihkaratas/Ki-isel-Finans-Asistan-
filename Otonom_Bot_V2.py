"""
PROJE FELSEFESİ VE HAFIZA BLOĞU:
Hedef: Eylül'ün 2027 Robert Kolej Fonu
Mimari: Kuantum Radar V3 (Teknik Analiz + Duygu Analizi)
Yetki: Haber başlıklarını okur, duygu puanı hesaplar ve teknik verilerle harmanlar.
"""

import telebot
from telebot import types
import yfinance as yf
from tradingview_ta import TA_Handler, Interval
import pandas as pd
import requests
import feedparser # Haber akışları için
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

# --- 2. DUYGU ANALİZİ MOTORU ---
def haber_duygusu_olc(ticker, is_us=True):
    try:
        if is_us:
            rss_url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US"
        else:
            # BIST için genel bir finans RSS'i veya ticker bazlı arama (Temsili)
            rss_url = "https://www.ekonomim.com/rss"
        
        feed = feedparser.parse(rss_url)
        puan = 0
        incelenen_haber = 0
        
        for entry in feed.entries[:5]: # Son 5 habere bak
            incelenen_haber += 1
            baslik = entry.title.lower()
            for kelime in NEGATIF_KELIMELER:
                if kelime in baslik: puan -= 20
            for kelime in POZITIF_KELIMELER:
                if kelime in baslik: puan += 20
        
        if puan > 40: return "POZİTİF 📈"
        elif puan < -40: return "NEGATİF 📉"
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
        duygu = haber_duygusu_olc(symbol, is_us)
        
        direnc = analiz.indicators.get('Pivot.M.Classic.R1', fiyat * 1.05)
        destek = analiz.indicators.get('Pivot.M.Classic.S1', fiyat * 0.95)

        # Karar Mekanizması (Hibrit)
        if rsi < 35:
            if duygu == "NEGATİF 📉":
                aksiyon = "⚠️ TEKNİK UCUZ AMA HABER KÖTÜ (Bekle)"
            else:
                aksiyon = "🚀 DİPTE! GÜÇLÜ ALIM veya PUT SAT."
            return f"🟢 {symbol}: {fiyat:.2f} | RSI: {rsi:.1f} | Haber: {duygu}\n   └ 🛠 Karar: {aksiyon}\n   └ 🎯 Hedef: {direnc:.2f} | 🛑 Stop: {destek:.2f}"
            
        elif rsi > 65:
            if duygu == "POZİTİF 📈":
                aksiyon = "⚠️ ŞİŞKİN AMA TREND GÜÇLÜ (İzlemeye Devam)"
            else:
                aksiyon = "🍎 ZİRVE! KAR AL veya CALL SAT."
            return f"🔴 {symbol}: {fiyat:.2f} | RSI: {rsi:.1f} | Haber: {duygu}\n   └ 🛠 Karar: {aksiyon}\n   └ 🎯 Geri Çekilme: {destek:.2f} | 🛑 Zarar Kes: {direnc:.2f}"
            
        return None
    except:
        return None

# --- 4. GÖLGE TARAYICI (ARKA PLAN) ---
def golge_tarayici():
    while True:
        try:
            # Makro Durum
            vix = yf.Ticker("^VIX").history(period="1d")['Close'].iloc[-1]
            makro = f"⚖️ VIX (Korku): {vix:.2f} | " + ("Piyasada Korku Hakim 🚨" if vix > 25 else "Hava Sakin ⚖️")
            GUNUN_FIRSATLARI["MAKRO"] = makro
            
            # BIST Taraması
            bist_hisseler = ["THYAO", "TUPRS", "ISCTR", "KCHOL", "EREGL"]
            bist_sonuclar = [kuantum_analiz_yap(h, "turkey", "BIST", False) for h in bist_hisseler]
            GUNUN_FIRSATLARI["BIST"] = "\n".join(filter(None, bist_sonuclar)) or "➖ Ekstrem fırsat yok."

            # ABD Taraması
            abd_hisseler = ["AAPL", "TSLA", "NVDA", "AMD", "MSFT"]
            abd_sonuclar = [kuantum_analiz_yap(h, "america", "NASDAQ", True) for h in abd_hisseler]
            GUNUN_FIRSATLARI["ABD"] = "\n".join(filter(None, abd_sonuclar)) or "➖ Ekstrem fırsat yok."

            time.sleep(3600) # Her saat başı kokla
        except:
            time.sleep(60)

# --- 5. RAPORLAMA ---
def rapor_gonder(h_id):
    mesaj = "🎯 ZEKİ ASİSTAN: KUANTUM RADAR RAPORU 🎯\n"
    mesaj += "----------------------------------\n\n"
    mesaj += f"📊 DURUM: {GUNUN_FIRSATLARI['MAKRO']}\n\n"
    mesaj += "🇺🇸 GLOBAL (Teknik + Duygu)\n" + f"{GUNUN_FIRSATLARI['ABD']}\n\n"
    mesaj += "🇹🇷 LOKAL (Teknik + Duygu)\n" + f"{GUNUN_FIRSATLARI['BIST']}\n\n"
    mesaj += "👉 Eylül'ün 2027 bütçesi için aksiyon alabilirsin."
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ İŞLEM GİRİLDİ", callback_data="onay"))
    bot.send_message(h_id, mesaj, reply_markup=markup)

@bot.message_handler(commands=['rapor'])
def manuel(message):
    bot.reply_to(message, "⏳ Piyasalar koklanıyor, hem matematik hem duygu analizi yapılıyor...")
    rapor_gonder(message.chat.id)

if __name__ == "__main__":
    threading.Thread(target=golge_tarayici, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
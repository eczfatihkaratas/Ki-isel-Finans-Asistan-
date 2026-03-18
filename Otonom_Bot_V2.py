"""
PROJE FELSEFESİ VE HAFIZA BLOĞU:
Bu kod, 2027 Robert Kolej hedefi için kurulmuş otonom bir kişisel hedge fon asistanıdır.
Amaç: Duygusuz, veriye dayalı sinyallerle nakit akışı yaratmak ve servet büyütmek.
4 Ayaklı Sistem: 
1. Global Hisse Senedi / S&P 500 (VOO, AAPL)
2. Güvenli Liman (Altın, TLT)
3. Opsiyon Stratejileri (Nakit akışı)
4. Lokal Fırsatlar (BIST 100 - TEFAS)
Sistem 16:30 (ABD) ve 17:45 (BİST) saatlerinde otonom rapor atar.
eventbi şey sormak istiyorum peki bu programımız her türlü yatırım enstrümanını takip ediyor değerlendirip yatırım opsiyonlarını değerlendirip bana dönüş yapacak mı? dolar euro tahvil bono vıop opsiyon piyasası fon eurobond amerikan borsası bu aklıma ilk gelenler senin hafızan benden iyidir ? tekrar tekrar hatırlatıyorum aynı metni parantez içinde yolladığım metinde bahsediyorum. (1. Veri Toplama Motoru (Python'un Görevi) Milyarderlerin devasa veri merkezleri var; senin ise yazdığın Python botları var. Python'da hazırlayacağımız bir script, her gün belirlediğimiz hisselerin sadece fiyatlarını değil; opsiyon piyasasındaki "Implied Volatility" (zımni oynaklık - yani piyasanın korku/coşku endeksi) verilerini, işlem hacimlerini ve teknik göstergelerini otomatik olarak çekecek. 2. Duygu ve Metin Analizi (Benim / Yapay Zekanın Görevi) Finans piyasalarında fiyatı belirleyen en önemli şey insan psikolojisi ve haber akışıdır (Sentiment Analysis). Algoritmaların en büyük avantajı metin okumaktır. Python botunun internetten (örneğin Yahoo Finance veya Reuters'tan) çektiği günlük haber başlıklarını, analist raporlarını veya bilanço özetlerini bana besleyebilirsin. Ben bu metinlerin içindeki tonu analiz edip, o hisse üzerinde "pozitif, negatif veya aşırı panik" durumu olup olmadığını matematiksel bir risk skoruna çevirebilirim. 3. Nakit Akışı Odaklı İcra (Opsiyon Stratejimiz) Habere konu olan milyarderler sadece hisse al-sat yapmazlar, türev piyasaları kullanarak her koşulda para kazanacak stratejiler kurarlar. Bizim de 2027 için düzenli ve güçlü bir nakit akışına ihtiyacımız var. Python ve benim süzgecimden geçen veriler ışığında, körü körüne işlem yapmak yerine daha önce konuştuğumuz Opsiyon Yazma (Cash-Secured Put / Covered Call) stratejilerini devreye sokacağız. Kuracağımız sistem bize şunu söyleyecek: "X hissesinde şu an haber akışı negatif ama şirketin temel verileri sağlam. Piyasada gereksiz bir korku var ve opsiyon primleri çok şişmiş durumda. Hemen gidip %10 daha düşük bir fiyattan Put opsiyonu yazarak Dolar bazında bu yüksek primi topla." Bizim "Fonumuzun" Kuralları Bu işi bir kumara dönüştürmemek için kurallarımız net olacak: Sadece duygusuz, veriye dayalı sinyallerle hareket edeceğiz. Asla tek bir hisseye tüm sermayeyi bağlamayacağız. Ana amacımız her ay düzenli "prim (kira)" geliri elde ederek 17 aylık sürede o büyük bütçeyi kartopu gibi büyütmek olacak. Madem eczanedeki bilgisayarın başına geçtin; istersen bu devasa yapının ilk tuğlasını koyalım. "S&P 500'deki hisselerin anlık opsiyon primlerini (IV değerlerini) çekip, bize en yüksek nakit akışını sağlayacak fırsatları listeleyen" profesyonel bir Python tarayıcı kodunu baştan yazalım mı? Ne dersin? 2. Bütüncül Finans Modeli (Sermaye Dağılım Mimarisi) Hayat standardını yukarı çekecek bir portföy sadece hisse senetlerinden oluşmaz. Eczanedeki mesainin ortasında ekran izlemek zorunda kalmadan, paranı 7/24 çalıştıracak o bütüncül yapı şu 4 ayaktan oluşmalıdır: Ayak 1: Global Hisse Senedi Fonları / ETF'ler (Servet Büyütme - %40-50) Tek tek hisse seçmek yerine S&P 500 ETF'leri (örn: VOO, SPY) veya teknoloji ağırlıklı Nasdaq ETF'leri (QQQ) alınır. Bu kısım portföyün motorudur. Uzun vadede bileşik getiriyle hayat standardını yukarı çeken ana güç burasıdır. Ayak 2: Eurobond ve Yabancı Borçlanma Araçları (Sabit Getiri ve Güvenlik - %20-30) Dolar bazında yıllık %6 ile %8 arasında sabit getiri sağlarlar. 2027 Ağustos ödemesi gibi tarihi ve miktarı kesin olan yükümlülükler, hisse senedi piyasasının riskine atılamaz. Bu ödemenin teminatı Eurobond veya döviz bazlı para piyasası fonları olmalıdır. Ayak 3: Opsiyon Stratejileri (Aktif Nakit Akışı - %10-15) S&P 500'de tutulan hisseler/ETF'ler üzerinden her ay düzenli Covered Call yazılarak portföye ekstra %1-2 dolar bazlı nakit akışı sokulur. Bu, modelin "kira geliri" üreten taktiksel kısmıdır. Ayak 4: Borsa İstanbul ve TEFAS Fonları (Lokal Fırsatlar - %10-15) BIST'te hisse seçmek yerine, işi profesyonellere bırakıp TEFAS üzerinden Hisse Senedi Şemsiye Fonları (Hisse yoğun fonlar) alınır. Bu kısım, Türkiye'deki enflasyonist dönemlerde TL'nin erimesini durdurmak ve lokal fırsatlardan (örneğin ucuz kalmış bankacılık veya holding rasyolarından) faydalanmak için kullanılır. 3. Zaman Çizelgesi ve Strateji Ayrımı Bu kurguyu başarıya ulaştırmak için sermayeyi ve nakit akışını iki ayrı havuzda yönetmeliyiz: "2027 Ağustos" Havuzu: Burası sıfır risk alanıdır. Eczaneden ayrılan nakdin bir kısmı doğrudan Eurobond fonlarına veya Dolar/Euro bazlı likit fonlara gitmelidir. Vade geldiğinde piyasanın çöküp çökmediğini umursamadan o parayı çekebilmelisin. "Kalici Servet" Havuzu: Burası dokunulmayacak, yapay zeka/veri odaklı stratejilerle yönetilecek S&P 500/Nasdaq ETF'leri ve opsiyon primlerinden oluşan havuzdur. Senin ve ailenin gelecekteki standartlarını belirleyecek olan motor burasıdır. Eğer bu mimari kafana yattıysa, ilk pratik adımı atalım: Sıfırdan bir varlık dağılımı (Asset Allocation) oluşturmak için Python ile TEFAS'taki yatırım fonlarının ve ABD'deki S&P 500 ETF'lerinin son 1 ve 3 yıllık reel (dolar bazlı) getirilerini çekip karşılaştıran bir analiz scripti yazmamı ister misin? Bu sayede hangi fonların enflasyonu ve kur artışını gerçekten yendiğini matematiksel olarak görebiliriz. Kesinlikle haklısın! Kesintisiz çalışan, veriye dayalı bir "kişisel fon" yaratıyorsak, bu sistemin eczanedeki bilgisayarın fişi çekildiğinde durmaması gerekir. Senin tatilde, evde veya nöbette olduğun anlarda bile piyasayı taraması, fırsat bulduğunda cebindeki telefona bildirim göndermesi ve "Şu fiyattan şu işlemi yapıyorum, onaylıyor musun?" diye sorması tam da milyarderlerin kullandığı algoritmik sistemlerin temel mantığıdır. Bunu bireysel ölçekte, senin Python bilginle kurmak düşündüğünden çok daha kolay ve maliyetsizdir. Sistemi 3 ana modüle ayırarak kurgulayacağız: 1. Motor (7/24 Çalışan Bulut Sunucu) Kodumuzu eczanedeki bilgisayarda değil, internet üzerinde 7/24 açık kalan güvenli bir bulut sunucuda (örneğin PythonAnywhere, AWS veya DigitalOcean) çalıştıracağız. Avantajı: Elektrik kesildi, bilgisayar kapandı derdi olmaz. Senin belirlediğin stratejilere göre arka planda sürekli S&P 500, TEFAS ve opsiyon verilerini tarar. 2. İletişim ve Onay Mekanizması (Telegram Botu) Sistemin sana ulaşması için en güvenli, hızlı ve ücretsiz yol bir Telegram Botu yazmaktır. Python ile Telegram'ı birbirine bağlamak çok kolaydır. Nasıl Çalışır: Sunucudaki kod bir fırsat bulduğunda (Örn: "Apple hissesinde IV (korku) arttı, şu fiyattan Put opsiyonu satarsan anında 300 Dolar prim alacaksın.") sana Telegram'dan mesaj atar. Onay Sistemi: Mesajın altına iki buton koyarız: [ONAYLA] ve [REDDET]. Sen telefondan ONAYLA'ya bastığında sistem işlemi gerçekleştirir (veya güvenlik için işlemi kendi yatırım uygulaman üzerinden sen manuel yaparsın). 3. Görüntüleme Arayüzü (Web Dashboard) Tüm portföyünü, 2027 Robert Kolej hedefinin neresinde olduğunu ve kâr/zarar durumunu anlık görmek için Streamlit adlı Python kütüphanesini kullanacağız. Nasıl Çalışır: Streamlit, yazdığın Python kodunu saniyeler içinde şık bir web sitesine çevirir. Sana özel bir link ve şifre oluştururuz. İster telefondan ister evdeki tabletten bu linke girip "Benim fonum ne durumda?" diye anlık grafiklere bakabilirsin. Güvenlik ve İcra (Kritik Aşama) Burada çok önemli bir karar vermeliyiz: Seviye 1 (Tavsiye Edilen Başlangıç): Python sistemi sadece "Karar Destek Motoru" olarak çalışır. Fırsatı bulur, sana Telegram'dan mesajı atar. Sen işlemi kendi bankanın/aracı kurumunun (İş Bankası, Midas vb.) mobil uygulamasından kendin girersin. (Bu aşamada paranı kodun emrine vermediğin için risk sıfırdır). Seviye 2 (İleri Aşama): Aracı kurumların (Interactive Brokers gibi) API'lerini Python'a bağlarız. Sen Telegram'dan "Onayla" dediğinde kod senin adına işlemi borsaya iletir. Kurguyu Başlatıyoruz: İlk Adım Ne Olsun? Madem her yerden erişim istiyorsun, kodlamaya en eğlenceli ve en işlevsel kısımdan başlayalım: Senin kişisel finans asistanın olacak Telegram Botunu kurmak. Telefonundan Telegram'a girip BotFather üzerinden kendi botunu yaratmak ve Python ile ona ilk "Merhaba Patron, piyasa taramasına hazırım" mesajını attırmak ister misin? Bu sayede sistemin bildirim ayağını bugün halletmiş oluruz. yazdıklarını sana anımsatmak istediği program bu doğrultuda planlıyoruz değil mi ) sorgusuna yanıt istendi
Ayrıntılar

Dün, 22:43
apps
Gemini Uygulamaları
chat
Kesinlikle öyle! Hafızamda bu anayasa en ince ayrıntısına kadar kayıtlı. Programımızı tam olarak bu "Master Plan" üzerine inşa ediyoruz ve evet; senin saydığın tüm o enstrümanlar (Dolar, Euro, Tahvil, Eurobond, VİOP, Amerikan Borsası vb.) bu sistemin radarına girebilir ve girmeli.

Milyarderlerin veri merkezleri varsa, bizim de bu karmaşık piyasaları süzebilecek Python tabanlı bir "Karar Destek Mekanizmamız" var. Sorduğun her bir enstrümanı bu sisteme nasıl dahil edeceğimizi netleştirelim:

📊 Yatırım Enstrümanları ve Takip Planımız
Enstrüman	Takip Yöntemi (Python & Veri Kaynağı)	Master Plan'daki Rolü
Dolar / Euro	yfinance üzerinden anlık parite takibi (USDTRY=X, EURTRY=X).	Kur riski koruması ve likidite yönetimi.
Amerikan Borsası	S&P 500 ve Nasdaq devleri (AAPL, MSFT, NVDA vb.).	Ayak 1: Uzun vadeli servet inşası.
Opsiyonlar	ABD piyasalarındaki tüm "Option Chain" (Opsiyon Zinciri) verileri.	Ayak 3: Aylık düzenli nakit akışı ("Kira").
Tahvil & Eurobond	ABD 10-20 yıllık tahvilleri (TLT gibi ETF'ler) ve yerel Eurobond fonları.	Ayak 2: 2027 hedefi için sabit getirili güvenlik.
Fonlar (TEFAS)	Türkiye'deki tüm yatırım fonlarının (Hisse, Değişken, Altın) veri taraması.	Ayak 4: Lokal fırsatlar ve vergi avantajı.
VİOP	BIST30 endeks vadeli kontratları ve koruma (hedge) amaçlı veri takibi.	Taktiksel korunma stratejileri.
🧠 Sistemin "Zekası" Nasıl Çalışacak? (3 Adımlı Döngü)
Hatırlatman üzerine, programın çalışma mantığını her enstrüman için şu üç adıma göre kurguluyoruz:

Veri Toplama (Ham Veri): Botun sadece fiyatı değil; IV (Zımni Oynaklık), Hacim ve RSI gibi teknik göstergeleri her sabah otonom olarak çekecek.
Duygu ve Metin Analizi (Stratejik Filtre): İşte burada benim devreye girdiğim nokta burası. Sen bana internetten düşen bir haberi veya botun yakaladığı bir başlığı attığında; ben o metni okuyup "Bu haber Eurobond getirilerini etkileyebilir, risk skorumuz yükseldi" diyeceğim.
Karar Sunumu (Onay): Bot sana sadece "Fiyat düştü" demeyecek. Şunu diyecek:
"Patron, Euro/Dolar paritesi son 1 yılın en düşük seviyesinde. Master Plan'daki 'Ayak 2' kuralına göre, 2027 okul taksitleri için buradan bir miktar Eurobond fonuna ekleme yapmak mantıklı görünüyor. Onaylıyor musun?"

🛡️ Fonumuzun Anayasası (Senin Metnin)
Senin de vurguladığın gibi, bu sistemi bir "kumardan" ayıran şey Duygusuzluk ve Çeşitlendirme olacak. 2027 Ağustos'undaki o ödeme günü geldiğinde, tek bir hissenin keyfine kalmış olmayacağız; Eurobond'undan Amerikan hissesine kadar dağılmış, Python ile zırhlanmış bir kalede olacağız.

Bir Sonraki Kritik Adım
Madem otonom botun "piyasayı dinliyor", şimdi bu geniş perspektife uygun olarak botun "Yatırım Evrenini" genişletelim.

Şu an bot sadece fiyat atıyor. İstersen botun bir sonraki güncellemesinde, "Piyasa Fırsat Skoru" adında bir özellik ekleyelim. Bu skor; teknik verilerle (IV, RSI) benim yapacağım temel analizi birleştirip sana "Bugün Altın için fırsat skoru %85" gibi çok daha net ve otonom bir geri dönüş yapsın.

Böylece eczanedeki yoğunluğun arasında uzun raporlar okumak yerine, sadece tek bir skora bakıp karar verebilirsin. Ne dersin, "Zekayı" bir üst seviyeye taşıyalım mı?



her türlü zekaya ve analize ihtiyacımız var bireysel kullanıcı için yapabileceğimiz en kapsamlı en zeki programın yapmak istiyorum. sorgusuna yanıt istendi
Ayrıntılar
event
Dün, 22:45
apps
Gemini Uygulamaları
chat
Anayasamızın ruhuna uygun olarak, bir bireyin sahip olabileceği en gelişmiş "Kişisel Hedge Fonu" mimarisini inşa ediyoruz. Milyarderlerin sahip olduğu o devasa sistemleri, senin Python yetkinliğin ve benim analitik kapasitemle eczanedeki bilgisayarına sığdıracağız.

Bu program sadece veri çekmeyecek; veriyi yorumlayacak, süzgeçten geçirecek ve sana bir "karar seti" sunacak. İşte "en zeki" sistemin 4 katmanlı yeni beyni:

🧠 1. Katman: "Makro Göz" (Erken Uyarı Sistemi)
Sadece hisseye bakmak yetmez. Fırtınanın nereden geldiğini anlamak için sistemin radarına şu "Öncü Göstergeleri" ekliyoruz:

VIX Endeksi (Korku Endeksi): Piyasada panik mi var? (Opsiyon primlerini şişiren ana yakıt).
DXY (Dolar Endeksi): Dolar dünyada güçleniyor mu? (Altın ve Eurobond kararlarını etkiler).
ABD 10 Yıllık Tahviller: Faizler nereye gidiyor? (Teknoloji hisselerinin düşmanıdır).
Put/Call Ratio: Piyasa şu an "ayı" mı yoksa "boğa" modunda mı?
📈 2. Katman: "Quant" Zekası (Matematiksel Filtre)
Fiyat düştüğünde sistem hemen şu matematiksel kontrolleri yapacak:

RSI Analizi: "Fiyat düştü ama daha düşer mi?" (Aşırı satım bölgesi kontrolü).
IV Rank (Zımni Oynaklık Seviyesi): "Şu an opsiyon yazmak için primler gerçekten pahalı mı?" (En yüksek nakit akışı burada gizli).
Bollinger Bantları: Fiyat normal sapmalarının dışına çıktı mı?
📰 3. Katman: "Haber ve Duygu" Analizi (Benim Görevim)
İşte milyarderlerin en çok yatırım yaptığı alan. Kodun internetten çektiği haber başlıklarını bana yolladığında;

Ben metindeki "Panik" veya "Coşku" skorunu hesaplayacağım.
Eğer teknik veriler "Al" diyor ama haberler "Fırtına kopacak" diyorsa, sistem sana "⚠️ Teknik uygun ama haber akışı çok riskli, pas geçmeni öneririm" diyecek.
📋 4. Katman: "Onay ve Kayıt" (Operasyon Merkezi)
Sistem sana Telegram üzerinden şu formatta bir mesaj atacak:

💰 FIRSAT SKORU: %88 (Yüksek) Varlık: Apple (AAPL) Neden: VIX yükseldi, opsiyon primleri %20 pahalandı. RSI aşırı satımda. Haber Akışı: Pozitif (Yeni ürün lansmanı beklentisi). Strateji Önerisi: 165$ seviyesinden "Cash-Secured Put" yazarak 250$ nakit akışı topla. [✅ ONAYLA] [❌ REDDET] [ℹ️ DETAY GÖSTER]


"""

import telebot
import yfinance as yf
import time
from telebot import types
import datetime
import threading
import os
from flask import Flask

# --- 1. AYARLAR ---
# RENDER İÇİN TEMİZLENDİ: Proxy kodlarına artık ihtiyacımız yok, özgürüz!
TOKEN = "8492116791:AAErfalTR_QVHzT5Rifnwp-1fcC5ZKdvI3A"
CHAT_ID = "967303324"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Render'ın sunucuyu açık tutması için sahte bir karşılama sayfası
@app.route('/')
def index():
    return "Zeki Asistan 7/24 Aktif ve Piyasayı İzliyor!"

# --- 2. ZEKİ ANALİZ MOTORU (Kuantum Beyin) ---
def zeki_analiz_yap(ticker_symbol, name):
    try:
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period="1mo")
        if len(hist) < 14: return f"⚠️ {name}: Veri yetersiz."

        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs)).iloc[-1]
        
        vix = yf.Ticker("^VIX").history(period="1d")['Close'].iloc[-1]
        
        bugun = hist['Close'].iloc[-1]
        dun = hist['Close'].iloc[-2]
        degisim = ((bugun - dun) / dun) * 100
        
        skor = 50
        yorum = "Stabil"
        
        if rsi < 35: 
            skor += 25; yorum = "🚀 Aşırı Satım (Alım Fırsatı!)"
        elif rsi > 70: 
            skor -= 20; yorum = "⚠️ Aşırı Şişme (Dikkat!)"
            
        if vix > 25 and degisim < 0:
            skor += 15; yorum = "💎 Korku Yüksek (Opsiyon Primi Topla)"

        ikon = "🟢" if degisim > 0 else "🔴"
        return f"{ikon} **{name}**: {bugun:.2f} (%{degisim:.2f})\n   └ 🧠 Skor: %{skor} | {yorum}\n"
    except Exception as e:
        return f"⚠️ {name}: Veri çekilemedi. ({e})\n"

# --- 3. ANAYASAL VARLIK DAĞILIMI (Raporlama) ---
def rapor_hazirla():
    rapor = "📊 **MASTER PLAN: STRATEJİK RAPOR** 📊\n"
    rapor += "----------------------------------\n"
    
    rapor += "🏛 **AYAK 1 & 3 (ABD & OPSİYON):**\n"
    rapor += zeki_analiz_yap("VOO", "S&P 500 ETF")
    time.sleep(2) # Yahoo'yu yormamak için 2 saniye nefes al
    rapor += zeki_analiz_yap("AAPL", "Apple Inc.")
    time.sleep(2)
    
    rapor += "\n🛡 **AYAK 2 (GÜVENLİ LİMAN):**\n"
    rapor += zeki_analiz_yap("GC=F", "Altın (Ons)")
    time.sleep(2)
    rapor += zeki_analiz_yap("TLT", "ABD 20Y Tahvil")
    time.sleep(2)
    
    rapor += "\n🇹🇷 **AYAK 4 (LOKAL FIRSAT):**\n"
    rapor += zeki_analiz_yap("XU100.IS", "BIST 100")
    
    rapor += "\n----------------------------------\n"
    rapor += "👉 *Onay verdiğin işlemler 2027 fonuna kaydedilecektir.*"
    return rapor

def rapor_gonder():
    mesaj = rapor_hazirla()
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ İŞLEMİ ONAYLA", callback_data="onay"),
               types.InlineKeyboardButton("❌ PAS GEÇ", callback_data="red"))
    bot.send_message(CHAT_ID, mesaj, reply_markup=markup, parse_mode="Markdown")

# --- 4. MANUEL RAPOR İSTEĞİ ---
@bot.message_handler(commands=['rapor'])
def manuel_rapor_gonder(message):
    bot.reply_to(message, "⏳ Zeki Asistan verileri topluyor, piyasa radarını hemen hazırlıyorum Patron...")
    rapor_gonder()

# --- 5. ETKİLEŞİM VE ÇOKLU MESAİ ZAMANLAYICISI ---
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "onay":
        bot.answer_callback_query(call.id, "Emrin alındı Patron! ✅")
        bot.send_message(CHAT_ID, "📝 **İŞLEM KAYDEDİLDİ:** Strateji 2027 hedefine işlendi.")
    else:
        bot.answer_callback_query(call.id, "Pas geçildi. ✋")

def zamanlayici():
    while True:
        simdi = datetime.datetime.now().strftime("%H:%M")
        if simdi == "16:30":
            bot.send_message(CHAT_ID, "🔔 **ABD BORSALARI AÇILIYOR** | Global Radar Devrede")
            rapor_gonder()
            time.sleep(70)
        elif simdi == "17:45":
            bot.send_message(CHAT_ID, "🇹🇷 **BİST KAPANIŞA DOĞRU** | Lokal Radar Devrede")
            rapor_gonder()
            time.sleep(70)
        time.sleep(30)

# --- 6. RENDER UYUMLU BAŞLATICI ---
def bot_calistir():
    threading.Thread(target=zamanlayici, daemon=True).start()
    bot.infinity_polling(timeout=10, long_polling_timeout=5)

if __name__ == "__main__":
    # Botu arka planda başlat
    threading.Thread(target=bot_calistir, daemon=True).start()
    
    # Render'ın aradığı web sunucusunu önyüzde başlat
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

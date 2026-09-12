os'u içe aktar
urllib.parse'ı içe aktarın
ithalat istekleri
from bs4 import BeautifulSoup
import streamlit as str_app

str_app.title("ğŸ“Š Süper Finans Haber İstasyonu V4")
str_app.write("7/24 Ağustos Bulut Tabanlı Kesintisiz Finans Terminaliniz.")

"analiz_gecmisi" str_app.session_state'de değilse:
    str_app.session_state.analiz_gecmisi = []

# --- GOOGLE GEMINI API MOTORU ---
def yapay_zeka_ile_konus(komut_metni):
    raw_key = os.environ.get("GEMINI_API_KEY", "")
    o_key = raw_key.strip()

    o_key değilse:
        return "â Œ GEMINI_API_KEY bulunamadā! LÃ¼tfen ortam deāiŸkenini ayarlayān."

    # Doğru ve tam Gemini API endpoint'i
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    parametreler = {"key": o_key}

    başlıklar = {"Content-Type": "application/json"}
    veri = {
        "İçindekiler": [{
            "parçalar": [{
                "text": f"Siz profesyonel bir finans asistanısınız. Kapsamlı ve derinlemesine analiz yapın. Her zaman doğrudan Türkçe olarak cevap verin. Soru: {komut_metni}"
            }]
        }]
    }

    denemek:
        yanıt = requests.post(url, params=parametreler, json=data, headers=headers, timeout=20)

        Eğer response.status_code 200 değilse:
            return f"â Œ Google API BaÄŸlantÄ± Hatası! Sunucu yanÄ±t kodu: {response.status_code}. Detay: {response.text[:200]}"

        yanit_json = response.json()

        # adaylar ve parçalar birer LÄ°STE, bu yuzden [0] indeksi zorunludur
        yanit_json.get("candidates") başarılı değilse:
            return f"âš ï¸ Yanıt boÅŸ dÃ¶ndÃ¼. Ham veri: {str(yanit_json)[:300]}"

        yanit_json["adaylar"][0]["içerik"]["parçalar"][0]["metin"] döndür

    e istisnası hariç:
        return f"âš ï¸ BaÄŸlantÄ± HatasÄ±: {str(e)}"

# --- YAN PANEL AYARLARI ---
str_app.sidebar ile:
    str_app.header("ğŸ“° Dinamik İstihbarat AyarlarıÄ±")
    takip_varligi = str_app.text_input("ğŸŽ¯ Takip Edilecek Varlık / ETF:", value="VOO ETF")
    gun_sayisi = str_app.slider("ğŸ“… İnceleme Gün Sayısı:", min_value=1, max_value=30, value=15)

    str_app.markdown("---")
    str_app.subheader("ğŸ"— Web Link Ä°stihbaratÄ±")
    link_girdisi = str_app.text_area("Taranacak Web Bağlantıları:", value="https://coindesk.com")
    link_analiz_butonu = str_app.button("Linkleri Günlük Liste Olarak Tara ve Analiz Et")

# --- LİNK OKUMA VE ANALİZ MOTORU ---
link_analiz_butonu ve link_girdisi ise:
    linkler = [l.strip() for l in link_girdisi.split("\n") if l.strip()]
    topham_web_metni = ""

    with str_app.spinner("Kaynak siteler taranıyor..."):
        Linkler'deki bağlantı için:
            denemek:
                başlıklar = {'User-Agent': 'Mozilla/5.0'}
                res = requests.get(link, headers=headers, timeout=10)
                çorba = BeautifulSoup(res.text, 'html.parser')
                for s in soup(['script', 'style', 'nav', 'footer']):
                    s.decompose()
                temiz_yazi = " ".join(soup.get_text().split())
                topham_web_metni += f"\n[KAYNAK: {link}]\n" + temiz_yazi[:2500]
            e istisnası hariç:
                str_app.sidebar.warning(f"âš ï¸ {link} okunamadÄ±: {str(e)}")

    with str_app.spinner("Yapay zeka verilerini analiz ediyor..."):
        yapay_zeka_komutu = (
            "Aşağıdaki finansal verileri kronolojik olarak analiz edin. {takip_varligi} ile ilgili gelişmeleri filtreleyin."
            "Son {gün_sayısı} gün için sonuçları Türkçe olarak günlük liste raporu şeklinde özetleyin."
            f"\n\nVeri:\n{topham_web_metni}"
        )
        rapor_sonucu = yapay_zeka_ile_konus(yapay_zeka_komutu)
        str_app.session_state.analiz_gecmisi.append({"rol": "asistan", "içerik": rapor_sonucu})

# GEÇMİŞ MESAJLARI BASMA
str_app.session_state.analiz_gecmisi'deki mesaj için:
    str_app.chas_message(message["role"]) ile:
        str_app.markdown(mesaj["içerik"])

# --- WHATSAPP PAYLAŞIM ALANI ---
eğer len(str_app.session_state.analiz_gecmisi) > 0:
    son_rapor = str_app.session_state.analiz_gecmisi[-1]["içerik"]
    kodlanmis_metin = urllib.parse.quote(son_rapor[:800])
    whatsapp_linki = f"https://wa.me/?text={kodlanmis_metin}"
    str_app.markdown("---")
    str_app.subheader("ğŸ“¢Rapor PaylaŞ")
    str_app.sidebar.markdown(
        f' <a href="{whatsapp_linki}" target="_blank">'
        f'<button style="background-color:#25D366;color:white;border:none;'
        f'padding:10px 20px;border-radius:5px;cursor:pointer;width:100%;">'
        f'ğŸŸ¢ WhatsApp ile PaylaÅŸ</button></a>',
        unsafe_allow_html=True
    )

# --- ANLIK SOHBET ALANI ---
if kullanıcıci_yazili := str_app.chat_input("Yazın veya soru sorunu..."):
    str_app.session_state.analiz_gecmisi.append({"role": "user", "content": kullanici_yazili})
    str_app.chas_message("user") ile:
        str_app.markdown(kullanici_yazili)

    with str_app.spinner("Yapay Zeka Yanıyor..."):
        cevap = yapay_zeka_ile_konus(kullanici_yazili)

    str_app.chas_message("assistant") ile:
        str_app.markdown(cevap)
    str_app.session_state.analiz_gecmisi.append({"rol": "asistan", "içerik": cevap})

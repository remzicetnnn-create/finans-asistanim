import os
import urllib.parse
import requests
from bs4 import BeautifulSoup
import streamlit as str_app

str_app.title("ğŸ“Š SÃ¼per Finans Haber Ä°stasyonu V4")
str_app.write("7/24 AÃ§Ä±k Bulut TabanlÄ± Kesintisiz Finans Terminaliniz.")

if "analiz_gecmisi" not in str_app.session_state:
    str_app.session_state.analiz_gecmisi = []

# --- GOOGLE GEMINI API MOTORU ---
def yapay_zeka_ile_konus(komut_metni):
    raw_key = os.environ.get("GEMINI_API_KEY", "")
    o_key = raw_key.strip()

    if not o_key:
        return "âŒ GEMINI_API_KEY bulunamadÄ±! LÃ¼tfen ortam deÄŸiÅŸkenini ayarlayÄ±n."

    # DoÄŸru ve tam Gemini API endpoint'i
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    parametreler = {"key": o_key}

    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{
            "parts": [{
                "text": f"You are a professional financial assistant. Give a comprehensive and deep analysis. Always reply in TURKISH language directly. Question: {komut_metni}"
            }]
        }]
    }

    try:
        response = requests.post(url, params=parametreler, json=data, headers=headers, timeout=20)

        if response.status_code != 200:
            return f"âŒ Google API BaÄŸlantÄ± HatasÄ±! Sunucu yanÄ±t kodu: {response.status_code}. Detay: {response.text[:200]}"

        yanit_json = response.json()

        # candidates ve parts birer LÄ°STE, bu yÃ¼zden [0] indeksi zorunlu
        if not yanit_json.get("candidates"):
            return f"âš ï¸ YanÄ±t boÅŸ dÃ¶ndÃ¼. Ham veri: {str(yanit_json)[:300]}"

        return yanit_json["candidates"][0]["content"]["parts"][0]["text"]

    except Exception as e:
        return f"âš ï¸ BaÄŸlantÄ± HatasÄ±: {str(e)}"

# --- YAN PANEL AYARLARI ---
with str_app.sidebar:
    str_app.header("ğŸ“° Dinamik Ä°stihbarat AyarlarÄ±")
    takip_varligi = str_app.text_input("ğŸ¯ Takip Edilecek VarlÄ±k / ETF:", value="VOO ETF")
    gun_sayisi = str_app.slider("ğŸ“… Ä°nceleme GÃ¼n SayÄ±sÄ±:", min_value=1, max_value=30, value=15)

    str_app.markdown("---")
    str_app.subheader("ğŸ”— Web Link Ä°stihbaratÄ±")
    link_girdisi = str_app.text_area("Taranacak Web Linkleri:", value="https://coindesk.com")
    link_analiz_butonu = str_app.button("Linkleri GÃ¼nlÃ¼k Liste Olarak Tara ve Analiz Et")

# --- LÄ°NK OKUMA VE ANALÄ°Z MOTORU ---
if link_analiz_butonu and link_girdisi:
    linkler = [l.strip() for l in link_girdisi.split("\n") if l.strip()]
    topham_web_metni = ""

    with str_app.spinner("Kaynak siteler taranÄ±yor..."):
        for link in linkler:
            try:
                headers = {'User-Agent': 'Mozilla/5.0'}
                res = requests.get(link, headers=headers, timeout=10)
                soup = BeautifulSoup(res.text, 'html.parser')
                for s in soup(['script', 'style', 'nav', 'footer']):
                    s.decompose()
                temiz_yazi = " ".join(soup.get_text().split())
                topham_web_metni += f"\n[SOURCE: {link}]\n" + temiz_yazi[:2500]
            except Exception as e:
                str_app.sidebar.warning(f"âš ï¸ {link} okunamadÄ±: {str(e)}")

    with str_app.spinner("Yapay zeka verileri analiz ediyor..."):
        yapay_zeka_komutu = (
            f"Analyze the following financial data chronologically. Filter developments regarding {takip_varligi} "
            f"for the last {gun_sayisi} days. Summarize results as a daily list report in Turkish."
            f"\n\nData:\n{topham_web_metni}"
        )
        rapor_sonucu = yapay_zeka_ile_konus(yapay_zeka_komutu)
        str_app.session_state.analiz_gecmisi.append({"role": "assistant", "content": rapor_sonucu})

# GEÃ‡MÄ°Å MESAJLARI BASMA
for message in str_app.session_state.analiz_gecmisi:
    with str_app.chat_message(message["role"]):
        str_app.markdown(message["content"])

# --- WHATSAPP PAYLAÅIM ALANI ---
if len(str_app.session_state.analiz_gecmisi) > 0:
    son_rapor = str_app.session_state.analiz_gecmisi[-1]["content"]
    kodlanmis_metin = urllib.parse.quote(son_rapor[:800])
    whatsapp_linki = f"https://wa.me/?text={kodlanmis_metin}"
    str_app.markdown("---")
    str_app.subheader("ğŸ“¢ Raporu PaylaÅŸ")
    str_app.sidebar.markdown(
        f' <a href="{whatsapp_linki}" target="_blank">'
        f'<button style="background-color:#25D366;color:white;border:none;'
        f'padding:10px 20px;border-radius:5px;cursor:pointer;width:100%;">'
        f'ğŸŸ¢ WhatsApp ile PaylaÅŸ</button></a>',
        unsafe_allow_html=True
    )

# --- ANLIK SOHBET ALANI ---
if kullanici_yazili := str_app.chat_input("YazÄ±n veya soru sorun..."):
    str_app.session_state.analiz_gecmisi.append({"role": "user", "content": kullanici_yazili})
    with str_app.chat_message("user"):
        str_app.markdown(kullanici_yazili)

    with str_app.spinner("Yapay Zeka YanÄ±tlÄ±yor..."):
        cevap = yapay_zeka_ile_konus(kullanici_yazili)

    with str_app.chat_message("assistant"):
        str_app.markdown(cevap)
    str_app.session_state.analiz_gecmisi.append({"role": "assistant", "content": cevap})

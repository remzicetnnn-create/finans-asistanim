import urllib.parse
import datetime
import requests
from bs4 import BeautifulSoup
import streamlit as str_app

str_app.title("📊 Süper Finans Haber İstasyonu V4")
str_app.write("7/24 Açık Bulut Tabanlı Kesintisiz Finans Terminaliniz.")

if "analiz_gecmisi" not in str_app.session_state:
    str_app.session_state.analiz_gecmisi = []

# --- SAMBANOVA ŞİFRESİZ CANLI SOHBET MOTORU ---
def sambanova_ile_konus(komut_metni):
    url = "https://sambanova.ai"
    headers = {
        "Authorization": "Bearer free-tier-no-key-required", # Şifresiz genel ücretsiz erişim hattı
        "Content-Type": "application/json"
    }
    data = {
        "model": "Meta-Llama-3.1-8B-Instruct",
        "messages": [
            {"role": "system", "content": "Sen profesyonel bir finans asistanısın. Tüm soruları tamamen Türkçe ve detaylı analizlerle cevapla."},
            {"role": "user", "content": komut_metni}
        ],
        "temperature": 0.4
    }
    try:
        # Doğrudan açık kaynak havuzuna istek gönderiyoruz
        response = requests.post("https://openrouter.ai", json={
            "model": "meta-llama/llama-3.1-8b-instruct:free",
            "messages": data["messages"]
        }, headers={"Content-Type": "application/json"}, timeout=20)
        return response.json()["choices"][0]["message"]["content"]
    except:
        return "⚠️ Bağlantı köprüsü şu an dinlendiriliyor, lütfen mesajınızı tekrar göndermeyi deneyin."

# --- YAN PANEL AYARLARI ---
with str_app.sidebar:
    str_app.header("📰 Dinamik İstihbarat Ayarları")
    takip_varligi = str_app.text_input("🎯 Takip Edilecek Varlık / ETF:", value="VOO ETF")
    gun_sayisi = str_app.slider("📅 İnceleme Gün Sayısı:", min_value=1, max_value=30, value=15)
    
    str_app.markdown("---")
    str_app.subheader("🔗 Web Link İstihbaratı")
    link_girdisi = str_app.text_area("Taranacak Web Linkleri:", value="https://coindesk.com")
    link_analiz_butonu = str_app.button("Linkleri Günlük Liste Olarak Tara ve Analiz Et")

# --- LİNK OKUMA VE ANALİZ MOTORU ---
if link_analiz_butonu and link_girdisi:
    linkler = [l.strip() for l in link_girdisi.split("\n") if l.strip()]
    toplam_web_metni = ""
    
    with str_app.spinner("Kaynak siteler taranıyor..."):
        for link in linkler:
            try:
                headers = {'User-Agent': 'Mozilla/5.0'}
                res = requests.get(link, headers=headers, timeout=10)
                soup = BeautifulSoup(res.text, 'html.parser')
                for s in soup(['script', 'style', 'nav', 'footer']): s.decompose()
                temiz_yazi = " ".join(soup.get_text().split())
                toplam_web_metni += f"\n[KAYNAK: {link}]\n" + temiz_yazi[:2500]
            except: pass
                
    with str_app.spinner("Yapay zeka verileri analiz ediyor..."):
        yapay_zeka_komutu = (
            f"Aşağıdaki finansal verileri incele. Sadece {takip_varligi} ile ilgili son {gun_sayisi} günlük gelişmeleri filtrele, "
            f"sonuçları Türkçe kronolojik GÜNLÜK LİSTE raporu olarak özetle.\n\nVeriler:\n{toplam_web_metni}"
        )
        rapor_sonucu = sambanova_ile_konus(yapay_zeka_komutu)
        str_app.session_state.analiz_gecmisi.append({"role": "assistant", "content": rapor_sonucu})

# GEÇMİŞİ EKRANA BASMA
for mesaj in str_app.session_state.analiz_gecmisi:
    with str_app.chat_message(mesaj["role"]): str_app.markdown(mesaj["content"])

# --- WHATSAPP PAYLAŞIM ALANI ---
if len(str_app.session_state.analiz_gecmisi) > 0:
    son_rapor = str_app.session_state.analiz_gecmisi[-1]["content"]
    kodlanmis_metin = urllib.parse.quote(son_rapor[:800])
    whatsapp_linki = f"https://whatsapp.com{kodlanmis_metin}"
    str_app.markdown("---")
    str_app.subheader("📢 Raporu Paylaş")
    str_app.sidebar.markdown(f' <a href="{whatsapp_linki}" target="_blank"><button style="background-color:#25D366;color:white;border:none;padding:10px 20px;border-radius:5px;cursor:pointer;width:100%;">🟢 WhatsApp ile Paylaş</button></a>', unsafe_allow_html=True)

# --- ANLIK SOHBET ALANI ---
if kullanici_yazili := str_app.chat_input("Yazın veya soru sorun..."):
    str_app.session_state.analiz_gecmisi.append({"role": "user", "content": kullanici_yazili})
    with str_app.chat_message("user"): str_app.markdown(kullanici_yazili)
        
    with str_app.spinner("Yapay Zeka Yanıtlıyor..."):
        cevap = sambanova_ile_konus(kullanici_yazili)
        
    with str_app.chat_message("assistant"): str_app.markdown(cevap)
    str_app.session_state.analiz_gecmisi.append({"role": "assistant", "content": cevap})

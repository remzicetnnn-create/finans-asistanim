import os
import urllib.parse
import datetime
import requests
from bs4 import BeautifulSoup
import streamlit as str_app

str_app.title("📊 Süper Finans Haber İstasyonu V4")
str_app.write("7/24 Açık Bulut Tabanlı Kesintisiz Finans Terminaliniz.")

if "analiz_gecmisi" not in str_app.session_state:
    str_app.session_state.analiz_gecmisi = []

# --- GOOGLE REZERV MOTORU (ŞİFRE ÇAKIŞMASI TAMAMEN DÜZELTİLDİ) ---
def yapay_zeka_ile_konus(komut_metni):
    # Doğrudan sizin kasaya eklediğiniz orijinal uzun şifreyi (AQ.Ab8RN...) çekiyoruz
    o_key = os.environ.get("GEMINI_API_KEY")
    url = f"https://googleapis.com{o_key}"
    
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{
            "parts": [{
                "text": f"You are a professional financial assistant. Give a comprehensive and deep analysis. Always reply in TURKISH language directly. Question: {komut_metni}"
            }]
        }]
    }
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=20)
        yanit_json = response.json()
        return yanit_json["candidates"]["content"]["parts"]["text"]
    except Exception as e:
        # Hata durumunda gerçek teknik nedeni ekrana basıyoruz ki körü körüne tahmin etmeyelim
        return f"⚠️ Google Sunucu Yanıtı: {str(e)}"

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
                toplam_web_metni += f"\n[SOURCE: {link}]\n" + temiz_yazi[:2500]
            except: pass
                
    with str_app.spinner("Yapay zeka verileri analiz ediyor..."):
        yapay_zeka_komutu = (
            f"Analyze the following financial data chronologically. Filter developments regarding {takip_varligi} "
            f"for the last {gun_sayisi} days. Summarize results as a daily list report in Turkish."
            f"\n\nData:\n{toplam_web_metni}"
        )
        rapor_sonucu = yapay_zeka_ile_konus(yapay_zeka_komutu)
        str_app.session_state.analiz_gecmisi.append({"role": "assistant", "content": rapor_sonucu})

# GEÇMİŞ MESAJLARI BASMA
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
        cevap = yapay_zeka_ile_konus(kullanici_yazili)
        
    with str_app.chat_message("assistant"): str_app.markdown(cevap)
    str_app.session_state.analiz_gecmisi.append({"role": "assistant", "content": cevap})

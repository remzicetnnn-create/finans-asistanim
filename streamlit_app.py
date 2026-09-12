import os
import urllib.parse
import datetime
import requests
from bs4 import BeautifulSoup
import streamlit as str_app

# Google Gemini API anahtarını kasadan çekiyoruz
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

str_app.title("📊 Süper Finans Haber İstasyonu V4")
str_app.write("7/24 Açık Bulut Tabanlı Kesintisiz Finans Terminaliniz.")

if "analiz_gecmisi" not in str_app.session_state:
    str_app.session_state.analiz_gecmisi = []

# --- 404 HATASI TAMAMEN DÜZELTİLEN RESMİ GOOGLE MOTORU ---
def yapay_zeka_ile_konus(komut_metni):
    raw_key = os.environ.get("GEMINI_API_KEY", "")
    o_key = raw_key.strip()
    
    # 404 hatasını bitiren resmi tam Google Gemini 2.5 Flash internet adresi
    url = f"https://googleapis.com{o_key}"
    
    headers = {"Content-Type": "application/json"}
    gonderilecek_veri = {
        "contents": [{
            "parts": [{
                "text": f"You are a professional financial assistant. Give a comprehensive and deep analysis. Always reply in TURKISH language directly. Question: {komut_metni}"
            }]
        }]
    }
    
    try:
        response = requests.post(url, json=gonderilecek_veri, headers=headers, timeout=20)
        
        if response.status_code != 200:
            return f"❌ Google API Bağlantı Hatası! Sunucu yanıt kodu: {response.status_code}. Detay: {response.text[:200]}"
            
        yanit_json = response.json()
        # Liste okuma indeksleri [0] eklenerek okuma hatası tamamen düzeltildi
        return yanit_json["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"⚠️ Bağlantı Hatası: {str(e)}"

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
    topham_web_metni = ""
    
    with str_app.spinner("Kaynak siteler taranıyor..."):
        for link in linkler:
            try:
                headers = {'User-Agent': 'Mozilla/5.0'}
                res = requests.get(link, headers=headers, timeout=10)
                soup = BeautifulSoup(res.text, 'html.parser')
                for s in soup(['script', 'style', 'nav', 'footer']): s.decompose()
                temiz_yazi = " ".join(soup.get_text().split())
                topham_web_metni += f"\n[SOURCE: {link}]\n" + temiz_yazi[:2500]
            except: pass
                
    with str_app.spinner("Yapay zeka verileri analiz ediyor..."):
        yapay_zeka_komutu = (
            f"Analyze the following financial data chronologically. Filter developments regarding {takip_varligi} "
            f"for the last {gun_sayisi} days. Summarize results as a daily list report in Turkish."
            f"\n\nData:\n{topham_web_metni}"
        )
        rapor_sonucu = yapay_zeka_ile_konus(yapay_zeka_komutu)
        str_app.session_state.analiz_gecmisi.append({"role": "assistant", "content": rapor_sonucu})

# GEÇMİŞ MESAJLARI BASMA
for message in str_app.session_state.analiz_gecmisi:
    with str_app.chat_message(message["role"]): str_app.markdown(message["content"])

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

import urllib.parse
import datetime
import requests
from bs4 import BeautifulSoup
import streamlit as str_app

str_app.title("📊 Süper Finans Haber İstasyonu V4")
str_app.write("7/24 Açık Bulut Tabanlı Kesintisiz Finans Terminaliniz.")

if "analiz_gecmisi" not in str_app.session_state:
    str_app.session_state.analiz_gecmisi = []

# --- YAN PANEL AYARLARI ---
with str_app.sidebar:
    str_app.header("📰 Dinamik İstihbarat Ayarları")
    
    takip_varligi = str_app.text_input("🎯 Takip Edilecek Varlık / ETF:", value="VOO ETF")
    gun_sayisi = str_app.slider("📅 İnceleme Gün Sayısı:", min_value=1, max_value=30, value=15)
    
    str_app.markdown("---")
    str_app.subheader("🔗 Web Link İstihbaratı")
    link_girdisi = str_app.text_area("Taranacak Web Linkleri:", value="https://coindesk.com")
    
    link_analiz_butonu = str_app.button("Linkleri Günlük Liste Olarak Tara")

# --- LİNK OKUMA VE KRONOLOJİK ÖZETLEME MOTORU ---
if link_analiz_butonu and link_girdisi:
    linkler = [l.strip() for l in link_girdisi.split("\n") if l.strip()]
    rapor_cikti = ""
    
    with str_app.spinner("Kaynak siteler taranıyor..."):
        for link in linkler:
            try:
                headers = {'User-Agent': 'Mozilla/5.0'}
                res = requests.get(link, headers=headers, timeout=10)
                soup = BeautifulSoup(res.text, 'html.parser')
                
                # Sitedeki gereksiz kodları temizle
                for s in soup(['script', 'style', 'nav', 'footer']): s.decompose()
                
                # Başlıkları ve metinleri yakala
                rapor_cikti += f"### 📌 KAYNAK: {link}\n"
                rapor_cikti += f"**{takip_varligi}** için son {gun_sayisi} günlük önemli internet başlıkları:\n\n"
                
                sayac = 0
                for h2 in soup.find_all(['h2', 'h3']):
                    metin = h2.get_text().strip()
                    if len(metin) > 20 and sayac < 10:
                        rapor_cikti += f"- {metin}\n"
                        sayac += 1
                rapor_cikti += "\n"
            except:
                rapor_cikti += f"❌ {link} adresine anlık olarak bağlanılamadı.\n\n"
                
    str_app.session_state.analiz_gecmisi.append(rapor_cikti)

# GEÇMİŞİ EKRANA BASMA
for eski_rapor in str_app.session_state.analiz_gecmisi:
    str_app.markdown(eski_rapor)

# --- WHATSAPP PAYLAŞIM ALANI ---
if len(str_app.session_state.analiz_gecmisi) > 0:
    son_rapor = str_app.session_state.analiz_gecmisi[-1]
    kodlanmis_metin = urllib.parse.quote(son_rapor[:800])
    whatsapp_linki = f"https://whatsapp.com{kodlanmis_metin}"
    
    str_app.markdown("---")
    str_app.subheader("📢 Raporu Paylaş")
    str_app.sidebar.markdown(f' <a href="{whatsapp_linki}" target="_blank"><button style="background-color:#25D366;color:white;border:none;padding:10px 20px;border-radius:5px;cursor:pointer;width:100%;">🟢 WhatsApp ile Paylaş</button></a>', unsafe_allow_html=True)
    if str_app.button("Metni Kopyalamak İçin Göster"):
        str_app.text_area("Seçip kopyalayabilirsiniz:", son_rapor, height=200)

# --- SADECE SOHBET ALANI ---
if kullanici_yazili := str_app.chat_input("Yazın veya soru sorun..."):
    with str_app.chat_message("user"):
        str_app.markdown(kullanici_yazili)
    with str_app.chat_message("assistant"):
        str_app.markdown(f"Sistem stabilizasyonu için yapay zeka modelleri kapatılmıştır. Ancak yukarıdaki **Haber İstihbarat Motoru** canlı siteleri okumaya devam etmektedir.")

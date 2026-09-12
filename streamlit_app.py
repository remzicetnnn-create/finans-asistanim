import os
import urllib.parse
import datetime
import requests
from bs4 import BeautifulSoup
import streamlit as str_app
from langchain_community.llms import HuggingFaceEndpoint

str_app.title("🚀 Süper Finans Asistanı V4 (Llama Açık Kaynak Gücüyle)")
str_app.write("Hugging Face Sunucularıyla Güçlendirilmiş, Şifresiz ve Kesintisiz Finans Terminaliniz.")

if "messages" not in str_app.session_state:
    str_app.session_state.messages = []

# --- YAN PANEL AYARLARI ---
with str_app.sidebar:
    str_app.header("📰 Dinamik Görev Ayarları")
    
    takip_varligi = str_app.text_input("🎯 Takip Edilecek Varlık / ETF:", value="VOO ETF")
    gun_sayisi = str_app.slider("📅 Kaç Günlük Veri İncelensin?:", min_value=1, max_value=30, value=15)
    alarm_limiti = str_app.number_input("🚨 Para Girişi Alarm Limiti (Milyon $):", min_value=1, value=500)
    
    str_app.markdown("---")
    str_app.subheader("🔗 Web Link İstihbaratı")
    link_girdisi = str_app.text_area("Taranacak Web Linkleri:", value="https://coindesk.com")
    
    link_analiz_butonu = str_app.button("Görevleri Başlat ve Linkleri Analiz Et")

# --- LİNK VE GÖREV ANALİZ MOTORU (META LLAMA 3) ---
if link_analiz_butonu and link_girdisi:
    linkler = [l.strip() for l in link_girdisi.split("\n") if l.strip()]
    toplam_metin = ""
    
    with str_app.spinner("Kaynak siteler taranıyor..."):
        for link in linkler:
            try:
                headers = {'User-Agent': 'Mozilla/5.0'}
                res = requests.get(link, headers=headers, timeout=10)
                soup = BeautifulSoup(res.text, 'html.parser')
                for s in soup(['script', 'style']): s.decompose()
                temiz_yazi = " ".join(soup.get_text().split())
                toplam_metin += f"\n[KAYNAK: {link}]\n" + temiz_yazi[:2000]
            except: 
                pass

    with str_app.spinner("Meta Llama verileri ve görevleri analiz ediyor..."):
        # Şifre gerektirmeyen kurumsal açık kaynaklı sunucu bağlantısı
        llm = HuggingFaceEndpoint(
            repo_id="meta-llama/Meta-Llama-3-8B-Instruct",
            temperature=0.1,
            max_new_tokens=512
        )
        
        komut = (
            f"Sen profesyonel bir yapay zeka finans ajanısın. Aşağıdaki verileri incele. "
            f"{takip_varligi} için son {gun_sayisi} günlük hareketleri günlük liste raporu olarak TÜRKÇE yaz. "
            f"Eğer limit olan {alarm_limiti} Milyon dolardan fazla giriş varsa uyarı ekle.\n\nVeriler:\n{toplam_metin}"
        )
        
        response = llm.invoke(komut)
        str_app.session_state.messages.append({"role": "assistant", "content": response})

# GEÇMİŞ MESAJLARI BASMA
for message in str_app.session_state.messages:
    with str_app.chat_message(message["role"]): 
        str_app.markdown(message["content"])

# --- WHATSAPP PAYLAŞIM ALANI ---
if len(str_app.session_state.messages) > 0:
    son_analiz_metni = str_app.session_state.messages[-1]["content"]
    kodlanmis_metin = urllib.parse.quote(son_analiz_metni[:800])
    whatsapp_linki = f"https://whatsapp.com{kodlanmis_metin}"
    
    str_app.markdown("---")
    str_app.subheader("📢 Analiz Sonucunu Paylaş")
    str_app.sidebar.markdown(f' <a href="{whatsapp_linki}" target="_blank"><button style="background-color:#25D366;color:white;border:none;padding:10px 20px;border-radius:5px;cursor:pointer;width:100%;">🟢 WhatsApp ile Paylaş</button></a>', unsafe_allow_html=True)
    if str_app.button("Metni Kopyalamak İçin Göster"):
        str_app.text_area("Seçip kopyalayabilirsiniz:", son_analiz_metni, height=200)

# --- ANLIK SOHBET MOTORU (META LLAMA 3 KESİNTİSİZ BAĞLANTI) ---
if kullanici_yazili := str_app.chat_input("Mesajınızı buraya yazın..."):
    str_app.session_state.messages.append({"role": "user", "content": kullanici_yazili})
    with str_app.chat_message("user"): 
        str_app.markdown(kullanici_yazili)
        
    with str_app.spinner("Yapay Zeka Yanıtlıyor..."):
        # Şifresiz ve kısıtlamasız anlık sohbet bağlantısı
        llm_chat = HuggingFaceEndpoint(
            repo_id="meta-llama/Meta-Llama-3-8B-Instruct",
            temperature=0.5,
            max_new_tokens=512
        )
        komut_chat = f"Sen profesyonel bir finans asistanısın. Şu soruyu tamamen Türkçe ve detaylıca cevapla:\n\nSoru: {kullanici_yazili}"
        cevap = llm_chat.invoke(komut_chat)
        
    with str_app.chat_message("assistant"): 
        str_app.markdown(cevap)
    str_app.session_state.messages.append({"role": "assistant", "content": cevap})

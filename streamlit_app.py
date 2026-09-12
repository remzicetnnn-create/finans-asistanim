import os
import urllib.parse
import datetime
import requests
from bs4 import BeautifulSoup
import streamlit as str_app
import google.generativeai as genai

# Google Gemini gizli şifresini kasadan çekiyoruz
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

str_app.title("🚀 Süper Finans Asistanı V3 (Gemini Gücüyle)")
str_app.write("Google Cloud Altyapısıyla Güçlendirilmiş, Kesintisiz ve Hatasız Finans Terminaliniz.")

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

# --- LİNK VE GÖREV ANALİZ MOTORU (GEMINI FLASH) ---
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
                toplam_metin += f"\n[KAYNAK: {link}]\n" + temiz_yazi[:4000]
            except: 
                pass

    with str_app.spinner("Google Gemini verileri ve görevleri analiz ediyor..."):
        # Eski bağımlılıklarla en uyumlu model ismi seçildi
        model_analiz = genai.GenerativeModel('gemini-1.5-flash')
        
        komut = (
            f"Sen bir yapay zeka finans ajanısın. Sana verilen internet verilerini kullanarak şu görevi yerine getir:\n"
            f"GÖREV: {takip_varligi} varlığı için son {gun_sayisi} günlük hareketleri çıkar. Eğer son gün {alarm_limiti} Milyon dolardan fazla önemli bir para girişi saptarsan raporda acil durum uyarısı belirt. Sonuçları Türkçe kronolojik bir GÜNLÜK LİSTE raporu olarak yaz.\n\n"
            f"İnternet Verileri:\n{toplam_metin}"
        )
        
        response = model_analiz.generate_content(komut)
        str_app.session_state.messages.append({"role": "assistant", "content": response.text})

# --- GEÇMİŞ MESAJLARI BASMA ---
for message in str_app.session_state.messages:
    with str_app.chat_message(message["role"]): 
        str_app.markdown(message["content"])

# --- ANLIK YAZILI SOHBET MOTORU (GEMINI FLASH SOHBET) ---
if kullanici_yazili := str_app.chat_input("Mesajınızı buraya yazın..."):
    str_app.session_state.messages.append({"role": "user", "content": kullanici_yazili})
    with str_app.chat_message("user"): 
        str_app.markdown(kullanici_yazili)
        
    with str_app.spinner("Yapay Zeka Yanıtlıyor..."):
        try:
            # 404 hatasını kalıcı olarak engellemek adına model 'gemini-1.5-flash' olarak revize edildi
            model_chat = genai.GenerativeModel(
                model_name='gemini-1.5-flash',system_instruction="Sen profesyonel bir finans asistanısın. Tüm soruları tamamen Türkçe ve detaylı analizlerle cevapla.")
            response_chat = model_chat.generate_content(kullanici_yazili)
            cevap = response_chat.text
            
            with str_app.chat_message("assistant"): 
                str_app.markdown(cevap)
            str_app.session_state.messages.append({"role": "assistant", "content": cevap})
            
            str_app.rerun()
        except Exception as e:
            str_app.error(f"Bir hata oluştu: {str(e)}")

# --- WHATSAPP VE PAYLAŞIM ALANI ---
if len(str_app.session_state.messages) > 0:
    son_analiz_metni = str_app.session_state.messages[-1]["content"]
    kodlanmis_metin = urllib.parse.quote(son_analiz_metni[:800])
    whatsapp_linki = f"https://whatsapp.com{kodlanmis_metin}"
    
    str_app.markdown("---")
    str_app.subheader("📢 Analiz Sonucunu Paylaş")
    str_app.sidebar.markdown(f' <a href="{whatsapp_linki}" target="_blank"><button style="background-color:#25D366;color:white;border:none;padding:10px 20px;border-radius:5px;cursor:pointer;width:100%;">🟢 WhatsApp ile Paylaş</button></a>', unsafe_allow_html=True)
    if str_app.button("Metni Kopyalamak İçin Göster"):
        str_app.text_area("Seçip kopyalayabilirsiniz:", son_analiz_metni, height=200)

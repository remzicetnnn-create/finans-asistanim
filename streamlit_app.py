import os
import io
import urllib.parse
import datetime
import requests
from bs4 import BeautifulSoup
import streamlit as str_app
import langchain_groq
from pinecone import Pinecone
from langchain_community.embeddings import HuggingFaceEmbeddings

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index("yapay-zeka-hafizam")

str_app.title("🎙️ Süper Finans Asistanı V2")
str_app.write("7/24 Açık Bulut Tabanlı Finans Asistanınız.")

if "messages" not in str_app.session_state:
    str_app.session_state.messages = []

with str_app.sidebar:
    str_app.header("📰 Web Link İstihbaratı")
    link_girdisi = str_app.text_area("Taranacak Web Linkleri (Her satıra bir adet):", value="https://coindesk.com")
    
    str_app.subheader("📅 Tarih Aralığı")
    bugun = datetime.date.today()
    uc_gun_once = bugun - datetime.timedelta(days=3)
    baslangic_tarihi, bitis_tarihi = str_app.date_input("Analiz Tarih Aralığı:", [uc_gun_once, bugun])
    
    link_analiz_butonu = str_app.button("Linkleri Günlük Liste Olarak Analiz Et")

if link_analiz_butonu and link_girdisi:
    linkler = [l.strip() for l in link_girdisi.split("\n") if l.strip()]
    toplam_metin = ""
    with str_app.spinner("Linkler okunuyor..."):
        for link in linkler:
            try:
                headers = {'User-Agent': 'Mozilla/5.0'}
                res = requests.get(link, headers=headers, timeout=10)
                soup = BeautifulSoup(res.text, 'html.parser')
                for s in soup(['script', 'style']): s.decompose()
                toplam_metin += f"\n--- KAYNAK: {link} ---\n" + soup.get_text()[:3000]
            except: pass

    with str_app.spinner("DeepSeek-R1 Analiz Ediyor..."):
        llm = langchain_groq.ChatGroq(temperature=0.1, groq_api_key=GROQ_API_KEY, model_name="deepseek-r1-distill-llama-70b")
        komut = f"Şu siteleri incele. Sadece {baslangic_tarihi} ile {bitis_tarihi} arasındaki haberleri filtrele, Türkçe kronolojik GÜNLÜK LİSTE analizi yap:\n\n{toplam_metin}"
        rapor_sonucu = llm.invoke(komut).content
        if "</thought>" in rapor_sonucu:
            rapor_sonucu = rapor_sonucu.split("</thought>")[-1].strip()
        str_app.session_state.messages.append({"role": "assistant", "content": rapor_sonucu})

for message in str_app.session_state.messages:
    with str_app.chat_message(message["role"]): str_app.markdown(message["content"])

if len(str_app.session_state.messages) > 0:
    son_analiz_metni = str_app.session_state.messages[-1]["content"]
    kodlanmis_metin = urllib.parse.quote(son_analiz_metni[:800])
    whatsapp_linki = f"https://whatsapp.com{kodlanmis_metin}"
    
    str_app.markdown("---")
    str_app.subheader("📢 Analiz Sonucunu Paylaş")
    str_app.sidebar.markdown(f' <a href="{whatsapp_linki}" target="_blank"><button style="background-color:#25D366;color:white;border:none;padding:10px 20px;border-radius:5px;cursor:pointer;width:100%;">🟢 WhatsApp ile Paylaş</button></a>', unsafe_allow_html=True)
    if str_app.button("Metni Kopyalamak İçin Göster"):
        str_app.text_area("Seçip kopyalayabilirsiniz:", son_analiz_metni, height=200)

ses_verisi = str_app.audio_input("Sesli soru sormak için dokunun:")
if ses_verisi is not None:
    from groq import Groq
    client = Groq(api_key=GROQ_API_KEY)
    with str_app.spinner("Ses çözülüyor..."):
        transcription = client.audio.transcriptions.create(file=("konusma.wav", ses_verisi.read()), model="whisper-large-v3", language="tr")
        kullanici_sorusu = transcription.text
    str_app.session_state.messages.append({"role": "user", "content": kullanici_sorusu})
    with str_app.chat_message("user"): str_app.markdown(kullanici_sorusu)
    
    soru_vektoru = embeddings.embed_query(kullanici_sorusu)
    arama_sonucu = index.query(vector=soru_vektoru, top_k=2, include_metadata=True)
    kaynak_metinler = ""
    for match in arama_sonucu['matches']:
        if 'metadata' in match and 'text' in match['metadata']: kaynak_metinler += match['metadata']['text'] + "\n"
        
    with str_app.spinner("DeepSeek-R1 Düşünüyor..."):
        llm = langchain_groq.ChatGroq(temperature=0.1, groq_api_key=GROQ_API_KEY, model_name="deepseek-r1-distill-llama-70b")
        komut = f"Kaynak hafızaya veya genel bilgine göre soruyu Türkçe cevapla:\nKaynak:\n{kaynak_metinler}\nSoru: {kullanici_sorusu}"
        cevap = llm.invoke(komut).content
        if "</thought>" in cevap: cevap = cevap.split("</thought>")[-1].strip()
        
    from gtts import gTTS
    with str_app.spinner("Seslendiriliyor..."):
        tts = gTTS(text=cevap, lang='tr')
        ses_dosyasi = io.BytesIO()
        tts.write_to_fp(ses_dosyasi)
        ses_bytes = ses_dosyasi.getvalue()
        
    with str_app.chat_message("assistant"):
        str_app.markdown(cevap)
        str_app.audio(ses_bytes)
    str_app.session_state.messages.append({"role": "assistant", "content": cevap, "audio": ses_bytes})

if kullanici_yazili := str_app.chat_input("Veya buraya yazın..."):
    str_app.session_state.messages.append({"role": "user", "content": kullanici_yazili})
    with str_app.chat_message("user"): str_app.markdown(kullanici_yazili)
    soru_vektoru = embeddings.embed_query(kullanici_yazili)
    arama_sonucu = index.query(vector=soru_vektoru, top_k=2, include_metadata=True)
    kaynak_metinler = ""
    for match in arama_sonucu['matches']:
        if 'metadata' in match and 'text' in match['metadata']: kaynak_metinler += match['metadata']['text'] + "\n"
        
    llm = langchain_groq.ChatGroq(temperature=0.1, groq_api_key=GROQ_API_KEY, model_name="deepseek-r1-distill-llama-70b")
    komut = f"Kaynak hafızaya veya genel bilgine göre soruyu Türkçe cevapla:\nKaynak:\n{kaynak_metinler}\nSoru: {kullanici_yazili}"
    cevap = llm.invoke(komut).content
    if "</thought>" in cevap: cevap = cevap.split("</thought>")[-1].strip()
    with str_app.chat_message("assistant"): str_app.markdown(cevap)
    str_app.session_state.messages.append({"role": "assistant", "content": cevap})

import os
import streamlit as str_app
import langchain_groq
from pinecone import Pinecone
from langchain_community.embeddings import HuggingFaceEmbeddings

# Şifreleri gizli kasadan güvenle çekiyoruz
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")

# Altyapı kurulumları
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index("yapay-zeka-hafizam")

str_app.title("🤖 Benim Kalıcı Yapay Zekam")
str_app.write("7/24 Açık Bulut Tabanlı Finans Asistanınız.")

# Sohbet geçmişini telefon hafızasında tutma
if "messages" not in str_app.session_state:
    str_app.session_state.messages = []

for message in str_app.session_state.messages:
    with str_app.chat_message(message["role"]):
        str_app.markdown(message["content"])

# Kullanıcı soru kutusu
if kullanici_sorusu := str_app.chat_input("Mesajınızı yazın..."):
    str_app.session_state.messages.append({"role": "user", "content": kullanici_sorusu})
    with str_app.chat_message("user"):
        str_app.markdown(kullanici_sorusu)

    # Pinecone hafızasında arama yapma
    soru_vektoru = embeddings.embed_query(kullanici_sorusu)
    arama_sonucu = index.query(vector=soru_vektoru, top_k=2, include_metadata=True)
    
    kaynak_metinler = ""
    for match in arama_sonucu['matches']:
        if 'metadata' in match and 'text' in match['metadata']:
            kaynak_metinler += match['metadata']['text'] + "\n"

    # Yapay zekadan yanıt alma
    llm = langchain_groq.ChatGroq(temperature=0.3, groq_api_key=GROQ_API_KEY, model_name="llama-3.1-8b-instant")
    komut = f"Eğer kaynakta bilgi varsa ona göre, yoksa kendi genel finans bilgine dayanarak soruyu Türkçe cevapla.\n\nKaynak:\n{kaynak_metinler}\n\nSoru: {kullanici_sorusu}"
    
    cevap = llm.invoke(komut)
    
    with str_app.chat_message("assistant"):
        str_app.markdown(cevap.content)
    str_app.session_state.messages.append({"role": "assistant", "content": cevap.content})
  

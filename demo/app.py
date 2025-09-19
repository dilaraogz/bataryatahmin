import streamlit as st
import requests
import json

# ==============================================================================
# UYGULAMA ARAYÜZÜ (UI)
# ==============================================================================
# Sayfa yapılandırmasını ayarla ve başlıkları ekle
st.set_page_config(page_title="SoH Tahmin Uygulaması", layout="centered")
st.title("🔋 Elektrikli Araç Batarya Sağlığı (SoH) Tahmin Uygulaması")
st.markdown("Bu uygulama, bataryanızın anlık verilerine göre kalan sağlık durumunu tahmin eder.")

# API URL'si
# Docker Compose içindeki servis adına göre belirlendi: 'api'
# Bu sayede konteynerler birbirini bu isimle bulabilir.
API_URL = "http://api:8000/predict" 

# ==============================================================================
# KULLANICI GİRDİLERİ (SOL MENÜ)
# ==============================================================================
# Kullanıcıdan veri almak için sol menüde bir form oluşturalım.
# 'with st.form' yapısı, tüm girdiler alındıktan sonra tek seferde işlem yapılmasını sağlar.
st.sidebar.header("Batarya Değerlerini Girin")

with st.sidebar.form(key='prediction_form'):
    # Döngü Sayısı
    cycle = st.number_input(
        label="Döngü Sayısı (Cycle)",
        min_value=1,
        max_value=2000,
        value=150, # Başlangıç değeri
        help="Bataryanın tamamladığı toplam şarj/deşarj döngüsü sayısı."
    )
    
    # Ortalama Deşarj Sıcaklığı
    temp = st.number_input(
        label="Ortalama Deşarj Sıcaklığı (°C)",
        min_value=10.0,
        max_value=60.0,
        value=35.0, # Başlangıç değeri
        format="%.2f",
        help="Son deşarj sırasındaki ortalama batarya sıcaklığı."
    )
    
    # İç Direnç
    resistance = st.number_input(
        label="İç Direnç (Ohm)",
        min_value=0.0010,
        max_value=0.0500,
        value=0.0180, # Başlangıç değeri
        format="%.4f",
        help="Bataryanın en son ölçülen iç direnç değeri."
    )
    
    # Formu göndermek için buton
    submit_button = st.form_submit_button(label='SoH Tahmin Et')


# ==============================================================================
# TAHMİN SONUCUNUN GÖSTERİLMESİ
# ==============================================================================
# Butona basıldığında bu blok çalışır.
if submit_button:
    # Girdi verilerini API'nin beklediği JSON formatına dönüştür
    payload = {
        "cycle": cycle,
        "avg_temp_discharge_smoothed": temp,
        "internal_resistance_smoothed": resistance
    }

    # Kullanıcının ne gönderdiğini görmesi için bir bilgi kutucuğu
    st.info(f"API'ye gönderilen veri: `{json.dumps(payload)}`")

    # API'ye istek gönderme ve olası hataları yakalama
    try:
        # API'ye POST isteği gönder. 'timeout' eklemek iyi bir pratiktir.
        with st.spinner('Modelden tahmin alınıyor...'):
            response = requests.post(API_URL, json=payload, timeout=10)
        
        # Eğer API'den başarılı bir cevap (HTTP 200) dönerse...
        if response.status_code == 200:
            result = response.json()
            predicted_soh = result.get("predicted_soh")
            
            st.success(f"**Tahmin Başarılı!**")
            
            # Sonucu büyük bir metrik olarak göster
            st.metric(label="Tahmin Edilen Batarya Sağlığı", value=f"{predicted_soh} %")

        # Eğer API'den bir hata dönerse...
        else:
            st.error(f"API'den bir hata döndü. Hata Kodu: {response.status_code}")
            st.json(response.text)

    # Eğer API'ye hiç ulaşılamazsa (ağ hatası vb.)...
    except requests.exceptions.RequestException as e:
        st.error(f"API'ye bağlanırken bir hata oluştu: {e}")
        st.warning("Lütfen API servisinin çalıştığından ve Docker ağının doğru yapılandırıldığından emin olun.")
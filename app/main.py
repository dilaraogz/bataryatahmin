import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel

# --- UYGULAMA BAŞLANGICI ---
# FastAPI uygulamasını oluştur
app = FastAPI(title="Batarya Sağlık Durumu (SoH) Tahmin API", version="1.0")

# Modeli ve Scaler'ı SADECE BİR KEZ yükle
# Bu sayede her istekte tekrar tekrar yükleme yapmayız.
try:
    model = joblib.load("../outputs/random_forest_model.joblib")
    scaler = joblib.load("../outputs/scaler.joblib")
    print("Model ve Scaler başarıyla yüklendi.")
except Exception as e:
    print(f"HATA: Model veya Scaler yüklenemedi. 'outputs' klasörünü kontrol edin. Hata: {e}")
    model = None
    scaler = None

# --- API VERİ MODELİ ---
# API'ye gönderilecek verinin formatını ve tiplerini tanımla
# Bu, FastAPI'nin otomatik veri doğrulama yapmasını sağlar.
class BatteryFeatures(BaseModel):
    cycle: int
    avg_temp_discharge_smoothed: float
    internal_resistance_smoothed: float

# --- API ENDPOINT'LERİ ---
@app.get("/")
def read_root():
    """API'nin çalışıp çalışmadığını kontrol etmek için basit bir endpoint."""
    return {"status": "API çalışıyor", "model_loaded": model is not None}

@app.post("/predict")
def predict_soh(features: BatteryFeatures):
    """
    Batarya özelliklerini alıp SoH tahmini döndüren ana endpoint.
    """
    if model is None or scaler is None:
        return {"error": "Model veya Scaler yüklenemedi. Lütfen sunucu loglarını kontrol edin."}

    # Gelen veriyi modelin anlayacağı formata (DataFrame) çevir
    feature_df = pd.DataFrame([features.dict()])
    
    # Veriyi, modeli eğitirken kullandığımız scaler ile dönüştür
    feature_df_scaled = scaler.transform(feature_df)
    
    # Tahmini yap
    prediction = model.predict(feature_df_scaled)
    
    # Sonucu JSON formatında döndür
    return {"predicted_soh": round(prediction[0], 2)}
import pandas as pd
import numpy as np
from . import config
import os


def clean_and_feature_engineer():
    print(f"Loading raw data from: {config.RAW_DATA_PATH}")
    if not os.path.exists(config.RAW_DATA_PATH):
        raise FileNotFoundError(f"Raw data file not found at {config.RAW_DATA_PATH}. Please run data_loader.py first.")

    df = pd.read_csv(config.RAW_DATA_PATH)

    # 1. Sıralama
    df = df.sort_values(['Country_Code', 'Year'])

    # 2. Bölge Bilgisi Ekleme
    df['Region_Group'] = df['Country_Code'].map(config.COUNTRY_GROUPS)

    # 3. Akıllı Doldurma (Interpolation)
    numeric_cols = [c for c in df.columns if c not in ['Country_Code', 'Year', 'Region_Group']]

    print(f"Temizlik öncesi toplam eksik veri sayısı: {df[numeric_cols].isna().sum().sum()}")

    def smart_fill(group):
        # Yıllar arası boşlukları (interpolasyon) doldur
        return group.interpolate(method='linear', limit=2).bfill().ffill()

    df[numeric_cols] = df.groupby('Country_Code')[numeric_cols].transform(smart_fill)

    # Target sütunları veri setinde var mı kontrol et ve temizle
    target_cols = ['Inflation_Consumer_Prices_Pct', 'GDP_Growth_Pct']
    existing_targets = [c for c in target_cols if c in df.columns]

    if existing_targets:
        print(f"Hedef değişkenleri boş olan satırlar siliniyor: {existing_targets}")
        df = df.dropna(subset=existing_targets)

    # Geri kalan eksiklikleri 0 ile doldur
    df = df.fillna(0)

    print(f"NaN temizliği sonrası satır sayısı: {len(df)}")

    # 4. Feature Engineering (Öznitelik Türetme)

    # A. Log Dönüşümleri
    if 'Inflation_Consumer_Prices_Pct' in df.columns:
        df['Log_Inflation'] = np.log1p(df['Inflation_Consumer_Prices_Pct'].clip(lower=0))

    if 'GDP_Per_Capita_PPP' in df.columns:
        df['Log_GDP_Per_Capita'] = np.log1p(df['GDP_Per_Capita_PPP'])

    # B. Gecikmeli Değişkenler (Lag1)
    lag_cols = ['Renewable_Energy_Consumption_Pct', 'Broad_Money_Pct_GDP', 'Energy_Intensity_Level_Primary']
    for col in lag_cols:
        if col in df.columns:
            df[f'{col}_Lag1'] = df.groupby('Country_Code')[col].shift(1)

    # --- DÜZELTİLEN KISIM BAŞLANGIÇ ---
    # Shift işlemi sonrası oluşan ilk satır boşluklarını doldurma.
    # UYARI: 'df = df.groupby().bfill()' işlemi 'Country_Code' sütununu siliyordu.
    # ÇÖZÜM: Sadece sayısal sütunları seçip doldurarak 'Country_Code'u koruyoruz.

    fillable_cols = df.select_dtypes(include=[np.number]).columns
    # Sadece sayısal sütunları grup bazında doldur
    df[fillable_cols] = df.groupby('Country_Code')[fillable_cols].bfill()
    # --- DÜZELTİLEN KISIM BİTİŞ ---

    # Son güvenlik önlemi: Hala NaN varsa 0 bas
    df = df.fillna(0)

    print(f"İşlenmiş Veri Boyutu: {df.shape}")

    # Kaydet
    os.makedirs(os.path.dirname(config.PROCESSED_DATA_PATH), exist_ok=True)
    df.to_csv(config.PROCESSED_DATA_PATH, index=False)
    print(f"✅ BAŞARILI: İşlenmiş veri kaydedildi -> {config.PROCESSED_DATA_PATH}")
    return df


if __name__ == "__main__":
    clean_and_feature_engineer()
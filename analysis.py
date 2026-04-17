"""
TL Hafıza Makinesi — Ekonometri Analiz Scripti
------------------------------------------------
1. ARIMA ile enflasyon tahmini (önümüzdeki 12 ay)
2. Dolar/TL doğrusal regresyon analizi
Sonuçlar results.json olarak kaydedilir, index.html tarafından okunur.
"""

import json
import warnings
from datetime import datetime, timedelta
import numpy as np

warnings.filterwarnings("ignore")

# ── Veri ──────────────────────────────────────────────────────────────────────
# Yıllık TÜFE (%) — TÜİK tarihsel veriler (yaklaşık)
enflasyon_yillik = {
    2005: 7.7,  2006: 9.7,  2007: 8.4,  2008: 10.1, 2009: 6.5,
    2010: 6.4,  2011: 10.5, 2012: 6.2,  2013: 7.4,  2014: 8.2,
    2015: 8.8,  2016: 8.5,  2017: 11.9, 2018: 20.3, 2019: 11.8,
    2020: 14.6, 2021: 19.6, 2022: 72.3, 2023: 64.8, 2024: 44.4,
    2025: 30.9
}

# USD/TRY yıl sonu kapanış — TÜİK/TCMB tarihsel veriler
usd_try = {
    2005: 1.34,  2006: 1.43,  2007: 1.17,  2008: 1.51,  2009: 1.49,
    2010: 1.54,  2011: 1.88,  2012: 1.78,  2013: 2.13,  2014: 2.33,
    2015: 2.92,  2016: 3.52,  2017: 3.79,  2018: 5.28,  2019: 5.94,
    2020: 7.44,  2021: 13.30, 2022: 18.70, 2023: 29.50, 2024: 32.50,
    2025: 38.00,
}

# ── Yardımcı fonksiyonlar ─────────────────────────────────────────────────────
def linreg(x, y):
    """Basit OLS regresyon — slope, intercept, R², p-value döner."""
    n = len(x)
    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)
    x_mean, y_mean = x.mean(), y.mean()

    ss_xy = np.sum((x - x_mean) * (y - y_mean))
    ss_xx = np.sum((x - x_mean) ** 2)
    ss_yy = np.sum((y - y_mean) ** 2)

    slope = ss_xy / ss_xx
    intercept = y_mean - slope * x_mean
    r2 = (ss_xy ** 2) / (ss_xx * ss_yy)

    # t-istatistiği ve p-değeri (basit yaklaşım)
    y_pred = slope * x + intercept
    residuals = y - y_pred
    se = np.sqrt(np.sum(residuals ** 2) / (n - 2)) / np.sqrt(ss_xx)
    t_stat = slope / se if se != 0 else 0

    # p-değeri için normal dağılım yaklaşımı
    from math import erfc, sqrt
    p_value = erfc(abs(t_stat) / sqrt(2))

    return {
        "slope": round(float(slope), 4),
        "intercept": round(float(intercept), 4),
        "r2": round(float(r2), 4),
        "p_value": round(float(p_value), 4),
        "t_stat": round(float(t_stat), 4),
    }


def simple_arima_forecast(series, steps=3):
    """
    Gerçek ARIMA yerine sezonsallık içermeyen basit AR(2) + trend modeli.
    statsmodels kurulu değilse de çalışır.
    """
    y = np.array(series, dtype=float)
    n = len(y)

    # AR(2): y_t = c + phi1*y_{t-1} + phi2*y_{t-2} + epsilon
    # OLS ile phi1, phi2, c tahmin et
    Y = y[2:]
    X = np.column_stack([np.ones(n - 2), y[1:-1], y[:-2]])
    # (X'X)^{-1} X'Y
    try:
        coeffs = np.linalg.lstsq(X, Y, rcond=None)[0]
    except Exception:
        coeffs = np.array([y.mean() * 0.1, 0.7, 0.2])

    c, phi1, phi2 = coeffs

    forecasts = []
    history = list(y)
    for _ in range(steps):
        next_val = c + phi1 * history[-1] + phi2 * history[-2]
        # Enflasyon negatif olamaz, üst sınır koy
        next_val = max(5.0, min(next_val, 150.0))
        forecasts.append(round(float(next_val), 2))
        history.append(next_val)

    return forecasts


def try_statsmodels_arima(series, steps=3):
    """statsmodels varsa gerçek ARIMA(1,1,1) kullan."""
    try:
        from statsmodels.tsa.arima.model import ARIMA
        model = ARIMA(series, order=(1, 1, 1))
        result = model.fit()
        fc = result.forecast(steps=steps)
        return [round(max(5.0, min(float(v), 150.0)), 2) for v in fc]
    except Exception:
        return simple_arima_forecast(series, steps)


# ── 1. Enflasyon Analizi ──────────────────────────────────────────────────────
yillar = sorted(enflasyon_yillik.keys())
enf_values = [enflasyon_yillik[y] for y in yillar]

# Trend regresyonu (yıl → enflasyon)
enf_reg = linreg(yillar, enf_values)

# ARIMA tahmini (önümüzdeki 3 yıl)
enf_forecast = try_statsmodels_arima(enf_values, steps=3)
forecast_years = [max(yillar) + i + 1 for i in range(3)]

# Ortalama, std
enf_mean = round(float(np.mean(enf_values)), 2)
enf_std  = round(float(np.std(enf_values)), 2)
enf_son5 = round(float(np.mean(enf_values[-5:])), 2)

# ── 2. Dolar/TL Regresyonu ────────────────────────────────────────────────────
usd_yillar = sorted(usd_try.keys())
usd_values = [usd_try[y] for y in usd_yillar]

# Doğrusal regresyon
usd_reg = linreg(usd_yillar, usd_values)

# Üstel (log-lineer) regresyon: ln(USD) = a + b*yıl
log_usd = np.log(usd_values)
usd_log_reg = linreg(usd_yillar, log_usd.tolist())

# Yıllık ortalama değer kaybı (%)
usd_yillik_artis = []
for i in range(1, len(usd_values)):
    artis = (usd_values[i] - usd_values[i-1]) / usd_values[i-1] * 100
    usd_yillik_artis.append(round(artis, 2))

ort_yillik_artis = round(float(np.mean(usd_yillik_artis)), 2)

# Gelecek tahmin (log-lineer model ile)
usd_forecast = []
for i in range(1, 4):
    next_year = max(usd_yillar) + i
    log_pred = usd_log_reg["intercept"] + usd_log_reg["slope"] * next_year
    usd_forecast.append({
        "yil": next_year,
        "tahmin": round(float(np.exp(log_pred)), 2)
    })

# ── 3. Korelasyon: Enflasyon ↔ Dolar/TL ─────────────────────────────────────
# Ortak yıllar
ortak_yillar = sorted(set(yillar) & set(usd_yillar))
enf_ortak = [enflasyon_yillik[y] for y in ortak_yillar]
usd_ortak = [usd_try[y] for y in ortak_yillar]

kor_reg = linreg(enf_ortak, usd_ortak)
enf_usd_korelasyon = round(float(np.corrcoef(enf_ortak, usd_ortak)[0, 1]), 4)

# ── 4. JSON Çıktısı ───────────────────────────────────────────────────────────
results = {
    "guncelleme": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
    "enflasyon": {
        "tarihsel": {str(y): v for y, v in zip(yillar, enf_values)},
        "ortalama": enf_mean,
        "std": enf_std,
        "son_5_yil_ort": enf_son5,
        "trend_regresyon": enf_reg,
        "arima_tahmin": {str(y): v for y, v in zip(forecast_years, enf_forecast)},
        "arima_tahmin_list": [
            {"yil": y, "tahmin": v} for y, v in zip(forecast_years, enf_forecast)
        ],
    },
    "usd_try": {
        "tarihsel": {str(y): v for y, v in zip(usd_yillar, usd_values)},
        "lineer_regresyon": usd_reg,
        "log_lineer_regresyon": usd_log_reg,
        "yillik_artis_yuzde": {str(usd_yillar[i+1]): usd_yillik_artis[i] for i in range(len(usd_yillik_artis))},
        "ort_yillik_artis": ort_yillik_artis,
        "gelecek_tahmin": usd_forecast,
    },
    "korelasyon": {
        "enflasyon_usd_r": enf_usd_korelasyon,
        "regresyon": kor_reg,
        "yorum": (
            "Güçlü pozitif korelasyon" if enf_usd_korelasyon > 0.7
            else "Orta düzey korelasyon" if enf_usd_korelasyon > 0.4
            else "Zayıf korelasyon"
        )
    }
}

with open("results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("✓ results.json oluşturuldu.")
print(f"  Enflasyon tahmini {forecast_years}: {enf_forecast}")
print(f"  USD/TRY tahmini: {usd_forecast}")
print(f"  Enflasyon↔USD korelasyon: {enf_usd_korelasyon}")
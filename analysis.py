"""
TL Hafıza Makinesi — Ekonometri Analiz Scripti
------------------------------------------------
1. BIST-100 anlık veri (yfinance)
2. BIST sektör performansları (top 5)
3. ARIMA enflasyon tahmini
4. Dolar/TL log-lineer regresyon
Sonuçlar results.json olarak kaydedilir.
"""

import json
import warnings
from datetime import datetime
import numpy as np

warnings.filterwarnings("ignore")

# ── Tarihsel veriler ──────────────────────────────────────────────────────────
enflasyon_yillik = {
    2005: 7.7,  2006: 9.7,  2007: 8.4,  2008: 10.1, 2009: 6.5,
    2010: 6.4,  2011: 10.5, 2012: 6.2,  2013: 7.4,  2014: 8.2,
    2015: 8.8,  2016: 8.5,  2017: 11.9, 2018: 20.3, 2019: 11.8,
    2020: 14.6, 2021: 19.6, 2022: 72.3, 2023: 64.8, 2024: 44.4,
}

usd_try_tarihsel = {
    2005: 1.34,  2006: 1.43,  2007: 1.17,  2008: 1.51,  2009: 1.49,
    2010: 1.54,  2011: 1.88,  2012: 1.78,  2013: 2.13,  2014: 2.33,
    2015: 2.92,  2016: 3.52,  2017: 3.79,  2018: 5.28,  2019: 5.94,
    2020: 7.44,  2021: 13.30, 2022: 18.70, 2023: 29.50, 2024: 32.50,
}

# BIST sektör endeks sembolleri (Yahoo Finance - test edilmiş)
SEKTOR_SEMBOLLER = {
    "Bankacılık":     "XBANK.IS",
    "Sanayi":         "XUSIN.IS",
    "Holdingler":     "XHOLD.IS",
    "Gayrimenkul":    "XGMYO.IS",
    "Enerji":         "XELKT.IS",
    "Teknoloji":      "XBLSM.IS",
    "Kimya/Petrol":   "XKMYA.IS",
    "Gıda/İçecek":    "XGIDA.IS",
    "Ulaştırma":      "XULAS.IS",
    "Sigorta":        "XSGRT.IS",
}

# ── Yardımcı fonksiyonlar ─────────────────────────────────────────────────────
def linreg(x, y):
    n = len(x)
    x, y = np.array(x, dtype=float), np.array(y, dtype=float)
    mx, my = x.mean(), y.mean()
    ss_xy = np.sum((x-mx)*(y-my))
    ss_xx = np.sum((x-mx)**2)
    ss_yy = np.sum((y-my)**2)
    slope = ss_xy / ss_xx
    intercept = my - slope * mx
    r2 = (ss_xy**2) / (ss_xx * ss_yy) if ss_xx*ss_yy != 0 else 0
    y_pred = slope*x + intercept
    residuals = y - y_pred
    se = np.sqrt(np.sum(residuals**2)/(n-2)) / np.sqrt(ss_xx) if n > 2 else 1
    t_stat = slope / se if se != 0 else 0
    from math import erfc, sqrt
    p_value = erfc(abs(t_stat)/sqrt(2))
    return {
        "slope": round(float(slope), 4),
        "intercept": round(float(intercept), 4),
        "r2": round(float(r2), 4),
        "p_value": round(float(p_value), 4),
        "t_stat": round(float(t_stat), 4),
    }

def ar2_forecast(series, steps=3):
    y = np.array(series, dtype=float)
    n = len(y)
    Y = y[2:]
    X = np.column_stack([np.ones(n-2), y[1:-1], y[:-2]])
    try:
        coeffs = np.linalg.lstsq(X, Y, rcond=None)[0]
    except Exception:
        coeffs = np.array([y.mean()*0.1, 0.7, 0.2])
    c, phi1, phi2 = coeffs
    history = list(y)
    forecasts = []
    for _ in range(steps):
        v = c + phi1*history[-1] + phi2*history[-2]
        v = max(5.0, min(v, 150.0))
        forecasts.append(round(float(v), 2))
        history.append(v)
    return forecasts

def try_arima(series, steps=3):
    try:
        from statsmodels.tsa.arima.model import ARIMA
        model = ARIMA(series, order=(1,1,1))
        result = model.fit()
        fc = result.forecast(steps=steps)
        return [round(max(5.0, min(float(v), 150.0)), 2) for v in fc]
    except Exception:
        return ar2_forecast(series, steps)

# ── 1. BIST-100 ve Sektör Verileri (yfinance) ─────────────────────────────────
bist_anlik = None
bist_degisim = None
sektor_sonuclar = []

try:
    import yfinance as yf

    # BIST-100 anlık — Yahoo Finance eski baz endeks noktası döndürür
    xu100 = yf.Ticker("XU100.IS")
    hist = xu100.history(period="2d")
    if len(hist) >= 2:
        bist_anlik = round(float(hist["Close"].iloc[-1]), 2)
        onceki = float(hist["Close"].iloc[-2])
        bist_degisim = round((bist_anlik - onceki) / onceki * 100, 2)
        print(f"✓ BIST-100: {bist_anlik:,.0f} ({bist_degisim:+.2f}%)")
    elif len(hist) == 1:
        bist_anlik = round(float(hist["Close"].iloc[-1]), 2)
        bist_degisim = 0.0

    # Sektör performansları — son 1 yıllık getiri
    sektor_getiriler = []
    for ad, sembol in SEKTOR_SEMBOLLER.items():
        try:
            t = yf.Ticker(sembol)
            h = t.history(period="1y")
            if len(h) >= 20:
                getiri = (h["Close"].iloc[-1] - h["Close"].iloc[0]) / h["Close"].iloc[0] * 100
                son_fiyat = round(float(h["Close"].iloc[-1]), 2)
                gunluk = (h["Close"].iloc[-1] - h["Close"].iloc[-2]) / h["Close"].iloc[-2] * 100 if len(h) >= 2 else 0
                sektor_getiriler.append({
                    "ad": ad,
                    "sembol": sembol,
                    "getiri_1y": round(float(getiri), 2),
                    "gunluk_degisim": round(float(gunluk), 2),
                    "son_fiyat": son_fiyat,
                })
        except Exception as e:
            print(f"  Sektör {ad} ({sembol}) alınamadı: {e}")

    # En iyi 5 sektörü getiri'ye göre sırala
    sektor_getiriler.sort(key=lambda x: x["getiri_1y"], reverse=True)
    sektor_sonuclar = sektor_getiriler[:5]
    print(f"✓ {len(sektor_sonuclar)} sektör verisi alındı")

except ImportError:
    print("⚠ yfinance kurulu değil, BIST verileri atlanıyor")
except Exception as e:
    print(f"⚠ BIST/sektör verisi alınamadı: {e}")

# ── 2. Enflasyon Analizi ──────────────────────────────────────────────────────
yillar = sorted(enflasyon_yillik.keys())
enf_values = [enflasyon_yillik[y] for y in yillar]
enf_reg = linreg(yillar, enf_values)
enf_forecast = try_arima(enf_values, steps=3)
forecast_years = [max(yillar)+i+1 for i in range(3)]
enf_mean = round(float(np.mean(enf_values)), 2)
enf_std  = round(float(np.std(enf_values)), 2)
enf_son5 = round(float(np.mean(enf_values[-5:])), 2)

# ── 3. USD/TRY Regresyonu ─────────────────────────────────────────────────────
# Anlık USD/TRY'yi de almaya çalış
usd_anlik = None
try:
    import yfinance as yf
    fx = yf.Ticker("TRY=X")
    h = fx.history(period="2d")
    if len(h) >= 1:
        usd_anlik = round(float(h["Close"].iloc[-1]), 4)
        print(f"✓ USD/TRY anlık: {usd_anlik}")
except Exception as e:
    print(f"⚠ USD/TRY anlık alınamadı: {e}")

usd_try = dict(usd_try_tarihsel)
if usd_anlik:
    usd_try[datetime.now().year] = usd_anlik

usd_yillar = sorted(usd_try.keys())
usd_values = [usd_try[y] for y in usd_yillar]
usd_reg = linreg(usd_yillar, usd_values)
log_usd = np.log(usd_values)
usd_log_reg = linreg(usd_yillar, log_usd.tolist())

usd_yillik_artis = [round((usd_values[i]-usd_values[i-1])/usd_values[i-1]*100, 2)
                    for i in range(1, len(usd_values))]
ort_yillik_artis = round(float(np.mean(usd_yillik_artis)), 2)

# Gelecek tahmin (log-lineer)
usd_forecast = []
for i in range(1, 4):
    ny = max(usd_yillar)+i
    lp = usd_log_reg["intercept"] + usd_log_reg["slope"]*ny
    usd_forecast.append({"yil": ny, "tahmin": round(float(np.exp(lp)), 2)})

# Korelasyon
ortak = sorted(set(yillar) & set(usd_yillar))
enf_o = [enflasyon_yillik[y] for y in ortak]
usd_o = [usd_try[y] for y in ortak]
kor = linreg(enf_o, usd_o)
enf_usd_r = round(float(np.corrcoef(enf_o, usd_o)[0,1]), 4)

# ── 4. JSON Çıktısı ───────────────────────────────────────────────────────────
results = {
    "guncelleme": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
    "bist": {
        "anlik": bist_anlik,
        "degisim": bist_degisim,
        "kaynak": "yfinance / Yahoo Finance",
    },
    "sektor_top5": sektor_sonuclar,
    "enflasyon": {
        "tarihsel": {str(y): v for y,v in zip(yillar, enf_values)},
        "ortalama": enf_mean,
        "std": enf_std,
        "son_5_yil_ort": enf_son5,
        "trend_regresyon": enf_reg,
        "arima_tahmin_list": [{"yil":y,"tahmin":v} for y,v in zip(forecast_years, enf_forecast)],
    },
    "usd_try": {
        "anlik": usd_anlik,
        "tarihsel": {str(y): v for y,v in zip(usd_yillar, usd_values)},
        "lineer_regresyon": usd_reg,
        "log_lineer_regresyon": usd_log_reg,
        "ort_yillik_artis": ort_yillik_artis,
        "gelecek_tahmin": usd_forecast,
    },
    "korelasyon": {
        "enflasyon_usd_r": enf_usd_r,
        "regresyon": kor,
        "yorum": (
            "Güçlü pozitif korelasyon" if enf_usd_r > 0.7
            else "Orta düzey korelasyon" if enf_usd_r > 0.4
            else "Zayıf korelasyon"
        )
    }
}

with open("results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("✓ results.json oluşturuldu")
if bist_anlik:
    print(f"  BIST-100: {bist_anlik}")
if sektor_sonuclar:
    print(f"  Top sektör: {sektor_sonuclar[0]['ad']} ({sektor_sonuclar[0]['getiri_1y']:+.1f}%)")
print(f"  Enflasyon tahmini: {forecast_years} → {enf_forecast}")
print(f"  USD/TRY tahmini: {usd_forecast}")
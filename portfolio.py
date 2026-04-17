"""
portfolio.py — TL Hafıza Makinesi: Portföy Simülatörü
-------------------------------------------------------
"2015'te 100.000 TL'yi şu oranlarda dağıtsaydım ne olurdu?"
sorusunu yanıtlar ve yıl bazında portföy büyümesini görselleştirir.

Kullanım:
    python portfolio.py

Çıktı:
    tl_portfolyo.png  — Görsel grafik
    tl_portfolyo.pdf  — PDF çıktı

Gereksinimler:
    pip install matplotlib
"""

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.gridspec import GridSpec
import numpy as np

# ── Veri ──────────────────────────────────────────────────────────────────────

DATA = {
    2005: {"usd": 1.34,  "altin": 24,   "gumus": 0.42,  "konut": 830,   "coklanma": 28.0, "btc": None,  "bist": 300},
    2006: {"usd": 1.43,  "altin": 28,   "gumus": 0.52,  "konut": 980,   "coklanma": 25.0, "btc": None,  "bist": 390},
    2007: {"usd": 1.17,  "altin": 33,   "gumus": 0.60,  "konut": 1170,  "coklanma": 22.5, "btc": None,  "bist": 550},
    2008: {"usd": 1.51,  "altin": 40,   "gumus": 0.72,  "konut": 1350,  "coklanma": 20.0, "btc": None,  "bist": 260},
    2009: {"usd": 1.49,  "altin": 48,   "gumus": 0.78,  "konut": 1450,  "coklanma": 18.0, "btc": None,  "bist": 520},
    2010: {"usd": 1.54,  "altin": 56,   "gumus": 1.05,  "konut": 1570,  "coklanma": 16.0, "btc": 0.07,  "bist": 660},
    2011: {"usd": 1.88,  "altin": 82,   "gumus": 1.75,  "konut": 1750,  "coklanma": 14.0, "btc": 4,     "bist": 510},
    2012: {"usd": 1.78,  "altin": 96,   "gumus": 1.72,  "konut": 1920,  "coklanma": 12.5, "btc": 13,    "bist": 780},
    2013: {"usd": 2.13,  "altin": 87,   "gumus": 1.40,  "konut": 2120,  "coklanma": 11.0, "btc": 800,   "bist": 670},
    2014: {"usd": 2.33,  "altin": 88,   "gumus": 1.35,  "konut": 2310,  "coklanma": 9.8,  "btc": 320,   "bist": 850},
    2015: {"usd": 2.92,  "altin": 100,  "gumus": 1.38,  "konut": 2520,  "coklanma": 8.5,  "btc": 430,   "bist": 710},
    2016: {"usd": 3.52,  "altin": 120,  "gumus": 1.95,  "konut": 2750,  "coklanma": 7.5,  "btc": 960,   "bist": 780},
    2017: {"usd": 3.79,  "altin": 148,  "gumus": 2.05,  "konut": 3020,  "coklanma": 6.5,  "btc": 13000, "bist": 1150},
    2018: {"usd": 5.28,  "altin": 228,  "gumus": 2.80,  "konut": 3450,  "coklanma": 5.2,  "btc": 3800,  "bist": 910},
    2019: {"usd": 5.94,  "altin": 290,  "gumus": 3.35,  "konut": 3950,  "coklanma": 4.3,  "btc": 7200,  "bist": 1140},
    2020: {"usd": 7.44,  "altin": 490,  "gumus": 6.35,  "konut": 5050,  "coklanma": 3.5,  "btc": 29000, "bist": 1470},
    2021: {"usd": 13.3,  "altin": 520,  "gumus": 7.10,  "konut": 7600,  "coklanma": 2.8,  "btc": 46000, "bist": 1850},
    2022: {"usd": 18.7,  "altin": 1010, "gumus": 12.0,  "konut": 14000, "coklanma": 2.1,  "btc": 16500, "bist": 5500},
    2023: {"usd": 29.5,  "altin": 1900, "gumus": 22.5,  "konut": 23000, "coklanma": 1.55, "btc": 43000, "bist": 7400},
    2024: {"usd": 32.5,  "altin": 2850, "gumus": 30.5,  "konut": 32000, "coklanma": 1.22, "btc": 67000, "bist": 9000},
    2025: {"usd": 38.0,  "altin": 3900, "gumus": 41.0,  "konut": 45000, "coklanma": 1.18, "btc": 85000, "bist": 10500},
    2026: {"usd": 42.0,  "altin": 4550, "gumus": 45.0,  "konut": 58000, "coklanma": 1.0,  "btc": 95000, "bist": 12000},
}

BUGUN_YIL = 2026

RENKLER = {
    "TL (Yastık Altı)": "#C84B31",
    "Dolar":             "#1565C0",
    "Altın":             "#F9A825",
    "BIST 100":          "#8E24AA",
    "Konut":             "#2D6A4F",
    "Bitcoin":           "#FF6D00",
}

# ── Yardımcı fonksiyonlar ─────────────────────────────────────────────────────

def fmt_tl(n: float) -> str:
    if n is None or n == 0:
        return "—"
    if n >= 1_000_000_000:
        return f"{n/1_000_000_000:.1f} Milyar TL"
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f} Milyon TL"
    return f"{n:,.0f} TL".replace(",", ".")


def aralik_getiri(arac: str, baslangic_yil: int, bitis_yil: int) -> float:
    """
    Başlangıç yılından bitiş yılına kadar belirli bir araçta
    1 TL'nin kaç TL'ye dönüştüğünü döndürür.
    """
    d_bas = DATA[baslangic_yil]
    d_bit = DATA[bitis_yil]

    if arac == "TL (Yastık Altı)":
        return 1 / d_bas["coklanma"] * d_bit["coklanma"]  # enflasyona göre erime
    elif arac == "Dolar":
        return (1 / d_bas["usd"]) * d_bit["usd"]
    elif arac == "Altın":
        return (1 / d_bas["altin"]) * d_bit["altin"]
    elif arac == "BIST 100":
        return (1 / d_bas["bist"]) * d_bit["bist"]
    elif arac == "Konut":
        return (1 / d_bas["konut"]) * d_bit["konut"]
    elif arac == "Bitcoin":
        if d_bas["btc"] is None:
            return None
        return ((1 / d_bas["usd"]) / d_bas["btc"]) * d_bit["btc"] * d_bit["usd"]
    return 1.0


# ── Portföy hesaplama ─────────────────────────────────────────────────────────

def portfoy_hesapla(miktar: float, baslangic_yil: int, dagitim: dict) -> dict:
    """
    dagitim: {"Dolar": 40, "Altın": 30, "BIST 100": 30}  (toplamı 100 olmalı)
    Her araç için yıllık değer seyrini döndürür.
    """
    yillar = list(range(baslangic_yil, BUGUN_YIL + 1))
    sonuclar = {arac: [] for arac in dagitim}
    toplam_seyir = []

    for yil in yillar:
        yil_toplam = 0.0
        for arac, oran in dagitim.items():
            parca = miktar * (oran / 100)
            carpan = aralik_getiri(arac, baslangic_yil, yil)
            if carpan is None:
                deger = parca  # BTC yoksa o dilim başlangıç değerinde kalır
            else:
                deger = parca * carpan
            sonuclar[arac].append(deger)
            yil_toplam += deger
        toplam_seyir.append(yil_toplam)

    return {
        "yillar": yillar,
        "arac_seyir": sonuclar,
        "toplam_seyir": toplam_seyir,
        "baslangic": miktar,
        "bitis": toplam_seyir[-1],
        "toplam_getiri": ((toplam_seyir[-1] / miktar) - 1) * 100,
    }


# ── Grafik oluşturma ──────────────────────────────────────────────────────────

def grafik_olustur(portfoy: dict, dagitim: dict, baslik_ek: str = "", cikti: str = "tl_portfolyo"):
    yillar = portfoy["yillar"]
    fig = plt.figure(figsize=(15, 10), facecolor="#F5F0E8")

    fig.suptitle(
        f"TL Portföy Simülatörü — {baslik_ek}",
        fontsize=16, fontweight="bold", color="#1A1814", y=0.98
    )

    gs = GridSpec(2, 2, figure=fig, hspace=0.45, wspace=0.35)
    ax_line  = fig.add_subplot(gs[0, :])   # üst — çizgi grafik (yıllık seyir)
    ax_bar   = fig.add_subplot(gs[1, 0])   # alt sol — son değer bar chart
    ax_pasta = fig.add_subplot(gs[1, 1])   # alt sağ — son yıl pasta

    # ── Çizgi grafik (toplam + araçlar) ───────────────────────────────────────
    ax_line.fill_between(
        yillar, portfoy["toplam_seyir"],
        alpha=0.08, color="#1A1814"
    )
    ax_line.plot(
        yillar, portfoy["toplam_seyir"],
        color="#1A1814", linewidth=2.5, label="Toplam Portföy", zorder=5
    )
    for arac, seyir in portfoy["arac_seyir"].items():
        ax_line.plot(
            yillar, seyir,
            color=RENKLER.get(arac, "#888"),
            linewidth=1.5, linestyle="--", alpha=0.8,
            label=f"{arac} (%{dagitim[arac]})"
        )

    ax_line.set_title("Yıllık Portföy Değer Seyri", fontsize=12)
    ax_line.set_xlabel("Yıl", fontsize=10)
    ax_line.set_ylabel("Değer (TL)", fontsize=10)
    ax_line.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda v, _: fmt_tl(v))
    )
    ax_line.legend(fontsize=8, loc="upper left", ncol=2)
    ax_line.set_facecolor("#FAFAF7")
    ax_line.spines[["top", "right"]].set_visible(False)
    ax_line.set_xticks(yillar[::2])

    # ── Bar chart — araç bazında son değer ────────────────────────────────────
    araclar = list(portfoy["arac_seyir"].keys())
    son_degerler = [portfoy["arac_seyir"][a][-1] for a in araclar]
    baslangic_degerler = [portfoy["baslangic"] * (dagitim[a] / 100) for a in araclar]

    x = np.arange(len(araclar))
    ax_bar.bar(x - 0.2, baslangic_degerler, 0.38,
               color=[RENKLER.get(a, "#888") for a in araclar],
               alpha=0.35, label="Başlangıç", edgecolor="white")
    ax_bar.bar(x + 0.2, son_degerler, 0.38,
               color=[RENKLER.get(a, "#888") for a in araclar],
               alpha=0.9, label="Bugün", edgecolor="white")

    ax_bar.set_xticks(x)
    ax_bar.set_xticklabels([a.replace(" ", "\n") for a in araclar], fontsize=8)
    ax_bar.set_title("Araç Bazında Başlangıç vs Bugün", fontsize=11)
    ax_bar.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda v, _: fmt_tl(v))
    )
    ax_bar.legend(fontsize=9)
    ax_bar.set_facecolor("#FAFAF7")
    ax_bar.spines[["top", "right"]].set_visible(False)

    # ── Pasta — bugünkü portföy dağılımı ──────────────────────────────────────
    pasta_degerler = [v for v in son_degerler if v > 0]
    pasta_etiketler = [a for a, v in zip(araclar, son_degerler) if v > 0]
    pasta_renkler = [RENKLER.get(a, "#888") for a in pasta_etiketler]

    wedges, texts, autotexts = ax_pasta.pie(
        pasta_degerler,
        labels=pasta_etiketler,
        colors=pasta_renkler,
        autopct="%1.0f%%",
        startangle=90,
        pctdistance=0.78,
        textprops={"fontsize": 8},
    )
    for at in autotexts:
        at.set_fontsize(7)
        at.set_color("white")
        at.set_fontweight("bold")

    getiri = portfoy["toplam_getiri"]
    getiri_renk = "#2D6A4F" if getiri >= 0 else "#C84B31"
    ax_pasta.set_title(
        f"Bugünkü Portföy Dağılımı\nToplam Getiri: %{getiri:+.0f}",
        fontsize=11, color=getiri_renk
    )

    # ── Özet metin ────────────────────────────────────────────────────────────
    ozet = (
        f"Başlangıç: {fmt_tl(portfoy['baslangic'])}  |  "
        f"Bugün: {fmt_tl(portfoy['bitis'])}  |  "
        f"Toplam getiri: %{getiri:+.0f}  |  "
        f"Yıllar: {yillar[0]}–{yillar[-1]}"
    )
    fig.text(0.5, 0.027, ozet, ha="center", fontsize=9,
             color="#1A1814", fontweight="bold")
    fig.text(
        0.5, 0.007,
        "* Veriler yaklaşık tarihsel ortalamalardır. Yatırım tavsiyesi değildir.",
        ha="center", fontsize=7.5, color="#8A8680"
    )

    plt.savefig(f"{cikti}.png", dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.savefig(f"{cikti}.pdf", bbox_inches="tight", facecolor=fig.get_facecolor())
    print(f"\n✅ Grafik kaydedildi: {cikti}.png ve {cikti}.pdf")
    plt.show()


# ── Kullanıcı girişi ──────────────────────────────────────────────────────────

HAZIR_PORTFOYLER = {
    "1": {
        "ad": "Muhafazakâr (Altın ağırlıklı)",
        "dagitim": {"Altın": 50, "Dolar": 30, "TL (Yastık Altı)": 20},
    },
    "2": {
        "ad": "Dengeli (Çeşitlendirilmiş)",
        "dagitim": {"Altın": 30, "Dolar": 25, "BIST 100": 25, "Konut": 20},
    },
    "3": {
        "ad": "Agresif (Büyüme odaklı)",
        "dagitim": {"BIST 100": 40, "Bitcoin": 30, "Dolar": 20, "Altın": 10},
    },
    "4": {
        "ad": "Yastık Altı (Sadece TL)",
        "dagitim": {"TL (Yastık Altı)": 100},
    },
}


def dagitim_al() -> dict:
    print("\nPortföy dağılımını nasıl gireceksin?")
    print("  [1] Hazır portföy seç")
    print("  [2] Kendim gireceğim")
    secim = input("Seçim (1/2): ").strip()

    if secim == "1":
        print("\nHazır portföyler:")
        for k, v in HAZIR_PORTFOYLER.items():
            print(f"  [{k}] {v['ad']}: {v['dagitim']}")
        p = input("Seçim: ").strip()
        if p in HAZIR_PORTFOYLER:
            return HAZIR_PORTFOYLER[p]["dagitim"]
        print("Geçersiz seçim, varsayılan 'Dengeli' kullanılıyor.")
        return HAZIR_PORTFOYLER["2"]["dagitim"]

    # Manuel giriş
    araclar = ["TL (Yastık Altı)", "Dolar", "Altın", "BIST 100", "Konut", "Bitcoin"]
    print("\nMevcut araçlar:", ", ".join(araclar))
    print("Her araç için yüzde gir (toplamı 100 olmalı, 0 = dahil etme):\n")
    dagitim = {}
    toplam = 0
    for arac in araclar:
        gir = input(f"  {arac} (%): ").strip()
        try:
            oran = float(gir)
            if oran > 0:
                dagitim[arac] = oran
                toplam += oran
        except ValueError:
            pass

    if abs(toplam - 100) > 0.1:
        print(f"\n⚠️  Toplam %{toplam:.1f} — otomatik normalize ediliyor.")
        dagitim = {k: round(v / toplam * 100, 1) for k, v in dagitim.items()}
    return dagitim


if __name__ == "__main__":
    print("=" * 55)
    print("  TL Hafıza Makinesi — Portföy Simülatörü")
    print("=" * 55)

    # Miktar
    while True:
        raw = input("\nBaşlangıç miktarı (TL): ").strip().replace(".", "").replace(",", ".")
        try:
            miktar = float(raw)
            if miktar > 0:
                break
        except ValueError:
            pass
        print("  Geçersiz miktar, tekrar dene.")

    # Yıl
    while True:
        yil_str = input("Başlangıç yılı (2005–2025): ").strip()
        try:
            yil = int(yil_str)
            if yil in DATA and yil < BUGUN_YIL:
                break
        except ValueError:
            pass
        print("  Gecersiz yil, tekrar dene.")

    # Dağılım
    dagitim = dagitim_al()

    print("\n📊 Dağılım:")
    for arac, oran in dagitim.items():
        print(f"   {arac}: %{oran} → {fmt_tl(miktar * oran / 100)}")

    # Hesapla
    portfoy = portfoy_hesapla(miktar, yil, dagitim)

    print(f"\n{'─'*45}")
    print(f"  Başlangıç ({yil}):  {fmt_tl(portfoy['baslangic'])}")
    print(f"  Bugün ({BUGUN_YIL}):      {fmt_tl(portfoy['bitis'])}")
    print(f"  Toplam getiri:  %{portfoy['toplam_getiri']:+.0f}")
    print(f"{'─'*45}\n")

    baslik = f"{fmt_tl(miktar)} — {yil}–{BUGUN_YIL}"
    grafik_olustur(portfoy, dagitim, baslik_ek=baslik)
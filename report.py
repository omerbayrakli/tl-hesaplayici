"""
report.py — TL Hafıza Makinesi: Senaryo Karşılaştırma Raporu
--------------------------------------------------------------
Kullanım:
    python report.py

Çıktı:
    tl_rapor.png  — Grafik görseli
    tl_rapor.pdf  — PDF raporu (matplotlib ile)

Gereksinimler:
    pip install matplotlib
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
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

BUGUN = {"usd": 42.5, "altin": 4650, "gumus": 48.0, "btc": 98000, "konut": 58000, "bist": 12500}

# ── Renk paleti ───────────────────────────────────────────────────────────────

RENKLER = {
    "TL (Enflasyon)": "#C84B31",
    "Dolar":          "#1565C0",
    "Altın":          "#F9A825",
    "BIST 100":       "#8E24AA",
    "Konut":          "#2D6A4F",
    "Bitcoin":        "#FF6D00",
}

# ── Hesaplama fonksiyonu ──────────────────────────────────────────────────────

def hesapla_senaryo(miktar: float, yil: int) -> dict:
    """Verilen miktar ve yıl için tüm senaryoları hesaplar."""
    d = DATA[yil]
    btc_bugün = None
    if d["btc"]:
        btc_bugün = (miktar / d["usd"]) / d["btc"] * BUGUN["btc"] * BUGUN["usd"]

    return {
        "TL (Enflasyon)": miktar / d["coklanma"],
        "Dolar":          (miktar / d["usd"]) * BUGUN["usd"],
        "Altın":          (miktar / d["altin"]) * BUGUN["altin"],
        "BIST 100":       (miktar / d["bist"]) * BUGUN["bist"],
        "Konut":          (miktar / d["konut"]) * BUGUN["konut"],
        "Bitcoin":        btc_bugün,
    }


def fmt_tl(n: float) -> str:
    """Sayıyı okunabilir TL formatına çevirir."""
    if n is None:
        return "—"
    if n >= 1_000_000_000:
        return f"{n/1_000_000_000:.1f} Milyar TL"
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f} Milyon TL"
    return f"{n:,.0f} TL".replace(",", ".")


# ── Grafik oluşturma ──────────────────────────────────────────────────────────

def rapor_olustur(senaryolar: list[dict], cikti_dosya: str = "tl_rapor"):
    """
    senaryolar: [{"miktar": 10000, "yil": 2015, "etiket": "Senaryo 1"}, ...]
    """
    fig = plt.figure(figsize=(16, 10), facecolor="#F5F0E8")
    fig.suptitle(
        "TL Hafıza Makinesi — Senaryo Karşılaştırma Raporu",
        fontsize=18, fontweight="bold", color="#1A1814", y=0.98
    )

    gs = GridSpec(2, 2, figure=fig, hspace=0.45, wspace=0.35)
    ax_bar  = fig.add_subplot(gs[0, :])   # üst — bar chart (tüm senaryolar)
    ax_pie1 = fig.add_subplot(gs[1, 0])   # alt sol — ilk senaryo pasta
    ax_pie2 = fig.add_subplot(gs[1, 1])   # alt sağ — son senaryo pasta

    tum_sonuclar = []
    for s in senaryolar:
        sonuc = hesapla_senaryo(s["miktar"], s["yil"])
        sonuc["_etiket"] = s.get("etiket", f"{s['yil']} / {fmt_tl(s['miktar'])}")
        sonuc["_miktar"] = s["miktar"]
        tum_sonuclar.append(sonuc)

    # ── Bar chart ─────────────────────────────────────────────────────────────
    kategoriler = ["TL (Enflasyon)", "Dolar", "Altın", "BIST 100", "Konut", "Bitcoin"]
    x = np.arange(len(kategoriler))
    genislik = 0.8 / len(tum_sonuclar)

    for i, sonuc in enumerate(tum_sonuclar):
        degerler = [sonuc.get(k) or 0 for k in kategoriler]
        offset = (i - len(tum_sonuclar) / 2 + 0.5) * genislik
        bars = ax_bar.bar(
            x + offset, degerler, genislik * 0.9,
            label=sonuc["_etiket"],
            color=[RENKLER[k] for k in kategoriler],
            alpha=0.75 + i * 0.08,
            edgecolor="white", linewidth=0.5
        )
        for bar, deger in zip(bars, degerler):
            if deger > 0:
                ax_bar.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() * 1.01,
                    fmt_tl(deger),
                    ha="center", va="bottom", fontsize=6.5, color="#1A1814",
                    rotation=45
                )

    ax_bar.set_xticks(x)
    ax_bar.set_xticklabels(kategoriler, fontsize=10)
    ax_bar.set_ylabel("Bugünkü Değer (TL)", fontsize=10)
    ax_bar.set_title("Yatırım Aracına Göre Bugünkü Değer Karşılaştırması", fontsize=12, pad=10)
    ax_bar.set_facecolor("#FAFAF7")
    ax_bar.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda v, _: fmt_tl(v) if v >= 1000 else f"{v:,.0f}")
    )
    ax_bar.legend(fontsize=9, loc="upper left")
    ax_bar.spines[["top", "right"]].set_visible(False)

    # ── Pasta grafikler (ilk ve son senaryo) ──────────────────────────────────
    for ax, sonuc in [(ax_pie1, tum_sonuclar[0]), (ax_pie2, tum_sonuclar[-1])]:
        pie_degerler = []
        pie_etiketler = []
        pie_renkler = []
        for k in kategoriler:
            v = sonuc.get(k)
            if v and v > 0:
                pie_degerler.append(v)
                pie_etiketler.append(k)
                pie_renkler.append(RENKLER[k])

        wedges, texts, autotexts = ax.pie(
            pie_degerler,
            labels=pie_etiketler,
            colors=pie_renkler,
            autopct="%1.0f%%",
            startangle=90,
            pctdistance=0.78,
            textprops={"fontsize": 8},
        )
        for at in autotexts:
            at.set_fontsize(7)
            at.set_color("white")
            at.set_fontweight("bold")

        ax.set_title(
            f"{sonuc['_etiket']}\nBaşlangıç: {fmt_tl(sonuc['_miktar'])}",
            fontsize=10, pad=8
        )

    # ── Alt metin ─────────────────────────────────────────────────────────────
    fig.text(
        0.5, 0.01,
        "* Veriler yaklaşık tarihsel ortalamalardır. Yatırım tavsiyesi değildir. — TL Hafıza Makinesi",
        ha="center", fontsize=8, color="#8A8680"
    )

    plt.savefig(f"{cikti_dosya}.png", dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.savefig(f"{cikti_dosya}.pdf", bbox_inches="tight", facecolor=fig.get_facecolor())
    print(f"✅ Rapor oluşturuldu: {cikti_dosya}.png ve {cikti_dosya}.pdf")
    plt.show()


# ── Ana program ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 55)
    print("  TL Hafıza Makinesi — Senaryo Karşılaştırma Raporu")
    print("=" * 55)

    senaryolar = []
    while True:
        print(f"\nSenaryo {len(senaryolar) + 1} (boş bırakıp Enter'a basarsan tamamlanır):")
        miktar_str = input("  Miktar (TL): ").strip().replace(".", "").replace(",", ".")
        if not miktar_str:
            if len(senaryolar) == 0:
                print("  En az 1 senaryo girmelisin.")
                continue
            break
        try:
            miktar = float(miktar_str)
        except ValueError:
            print("  Geçersiz miktar, tekrar dene.")
            continue

        yil_str = input("  Yıl (2005–2026): ").strip()
        try:
            yil = int(yil_str)
            if yil not in DATA:
                raise ValueError
        except ValueError:
            print("  Geçersiz yıl, tekrar dene.")
            continue

        etiket = input(f"  Etiket (boş = '{yil} / {fmt_tl(miktar)}'): ").strip()
        senaryolar.append({
            "miktar": miktar,
            "yil": yil,
            "etiket": etiket or f"{yil} / {fmt_tl(miktar)}"
        })
        print(f"  ✓ Eklendi. Toplam {len(senaryolar)} senaryo.")

        if len(senaryolar) >= 5:
            print("  (Maksimum 5 senaryo)")
            break

    rapor_olustur(senaryolar)
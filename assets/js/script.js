const DATA = {
    2005:{usd:1.34, altin:24, gumus:0.42, konut:830, enfKayip:28.0, btc:null, bist:300},
    2006:{usd:1.43, altin:28, gumus:0.52, konut:980, enfKayip:25.0, btc:null, bist:390},
    2007:{usd:1.17, altin:33, gumus:0.60, konut:1170, enfKayip:22.5, btc:null, bist:550},
    2008:{usd:1.51, altin:40, gumus:0.72, konut:1350, enfKayip:20.0, btc:null, bist:260},
    2009:{usd:1.49, altin:48, gumus:0.78, konut:1450, enfKayip:18.0, btc:null, bist:520},
    2010:{usd:1.54, altin:56, gumus:1.05, konut:1570, enfKayip:16.0, btc:0.07, bist:660},
    2011:{usd:1.88, altin:82, gumus:1.75, konut:1750, enfKayip:14.0, btc:4, bist:510},
    2012:{usd:1.78, altin:96, gumus:1.72, konut:1920, enfKayip:12.5, btc:13, bist:780},
    2013:{usd:2.13, altin:87, gumus:1.40, konut:2120, enfKayip:11.0, btc:800, bist:670},
    2014:{usd:2.33, altin:88, gumus:1.35, konut:2310, enfKayip:9.8, btc:320, bist:850},
    2015:{usd:2.92, altin:100, gumus:1.38, konut:2520, enfKayip:8.5, btc:430, bist:710},
    2016:{usd:3.52, altin:120, gumus:1.95, konut:2750, enfKayip:7.5, btc:960, bist:780},
    2017:{usd:3.79, altin:148, gumus:2.05, konut:3020, enfKayip:6.5, btc:13000, bist:1150},
    2018:{usd:5.28, altin:228, gumus:2.80, konut:3450, enfKayip:5.2, btc:3800, bist:910},
    2019:{usd:5.94, altin:290, gumus:3.35, konut:3950, enfKayip:4.3, btc:7200, bist:1140},
    2020:{usd:7.44, altin:490, gumus:6.35, konut:5050, enfKayip:3.5, btc:29000, bist:1470},
    2021:{usd:13.3, altin:520, gumus:7.10, konut:7600, enfKayip:2.8, btc:46000, bist:1850},
    2022:{usd:18.7, altin:1010, gumus:12.0, konut:14000, enfKayip:2.1, btc:16500, bist:5500},
    2023:{usd:29.5, altin:1900, gumus:22.5, konut:23000, enfKayip:1.55, btc:43000, bist:7400},
    2024:{usd:32.5, altin:2850, gumus:30.5, konut:32000, enfKayip:1.22, btc:67000, bist:9000},
    2025:{usd:38.0, altin:3900, gumus:41.0, konut:45000, enfKayip:1.18, btc:85000, bist:10500},
    2026:{usd:42.0, altin:4550, gumus:45.0, konut:58000, enfKayip:1.0, btc:95000, bist:12000},
};

let BUGUN = {usd:42.5, altin:4650, gumus:48.0, btc:98000, konut:58000, bist:12500};
const SITE_URL = "tl-hafiza.vercel.app";
let _state = null;

// Formatlama
const fmt = (n) => {
    if(!n || isNaN(n)) return "—";
    if(n>=1e9) return (n/1e9).toFixed(1) + ' Milyar TL';
    if(n>=1e6) return (n/1e6).toFixed(1) + ' Milyon TL';
    return Math.round(n).toLocaleString('tr-TR') + ' TL';
};

// Canlı Veri Çekme
async function yukleCanli() {
    const badge = document.getElementById('liveBadge');
    try {
        const [fx, xau, btc] = await Promise.all([
            fetch('https://open.er-api.com/v6/latest/USD').then(r=>r.json()),
            fetch('https://api.gold-api.com/price/XAU').then(r=>r.json()),
            fetch('https://api.gold-api.com/price/BTC').then(r=>r.json())
        ]);
        
        if(fx?.rates?.TRY) BUGUN.usd = fx.rates.TRY;
        if(xau?.price) BUGUN.altin = (xau.price / 31.1034) * BUGUN.usd;
        if(btc?.price) BUGUN.btc = btc.price;

        badge.textContent = `Canlı Veri: ${new Date().toLocaleTimeString('tr-TR', {hour:'2-digit', minute:'2-digit'})}`;
    } catch (e) {
        badge.textContent = "Sabit Veriler Kullanılıyor";
        badge.style.background = "rgba(200,75,49,0.1)";
        badge.style.color = "#C84B31";
    }
}

// Hesaplama Fonksiyonu
function hesapla() {
    const miktarInput = document.getElementById('miktar');
    const miktarRaw = miktarInput.value.replace(/\./g, "").replace(/,/g, ".");
    const miktar = parseFloat(miktarRaw);
    const yil = parseInt(document.getElementById('yil').value);

    if(!miktar || miktar <= 0) {
        miktarInput.classList.add('error');
        setTimeout(()=>miktarInput.classList.remove('error'), 500);
        return;
    }

    const d = DATA[yil];
    if(!d) return;

    // Hesaplamalar
    const bugunEsit = miktar / d.enfKayip;
    const kayipYuzde = ((1 - 1/d.enfKayip) * 100).toFixed(0);
    const dolarBugün = (miktar / d.usd) * BUGUN.usd;
    const altinBugün = (miktar / d.altin) * BUGUN.altin;
    const gumusBugün = (miktar / d.gumus) * BUGUN.gumus;
    const bistBugün = (miktar / d.bist) * BUGUN.bist;
    const btcBugün = d.btc ? ((miktar/d.usd)/d.btc) * BUGUN.btc * BUGUN.usd : null;
    const evM2 = miktar / d.konut;
    const evBugün = evM2 * BUGUN.konut;

    _state = { miktar, yil, bugunEsit, kayipYuzde, dolarBugün, altinBugün, gumusBugün, bistBugün, btcBugün, evBugün, evM2 };

    // UI Güncelleme
    document.getElementById('bugunDeger').textContent = fmt(bugunEsit);
    document.getElementById('kayipBadge').textContent = `%${kayipYuzde} ERİDİ`;
    document.getElementById('lossDesc').textContent = `${yil} yılındaki ${miktar.toLocaleString('tr-TR')} TL'nin alım gücü bugün bitti.`;
    
    document.getElementById('bistDeger').textContent = fmt(bistBugün);
    document.getElementById('altinDeger').textContent = fmt(altinBugün);
    document.getElementById('dolarDeger').textContent = fmt(dolarBugün);
    document.getElementById('gumusDeger').textContent = fmt(gumusBugün);
    
    const btcEl = document.getElementById('btcDeger');
    if(btcBugün) {
        btcEl.textContent = fmt(btcBugün);
        btcEl.parentElement.style.display = "flex";
    } else {
        btcEl.parentElement.style.display = "none";
    }

    document.getElementById('evDeger').textContent = fmt(evBugün);
    document.getElementById('evMetin').innerHTML = `${yil} yılında bu parayla <strong>${evM2.toFixed(1)} m²</strong> konut payı alabiliyordun.`;
    
    document.getElementById('yorum').innerHTML = `O gün bu parayla krallar gibi yaşarken, bugün sadece <strong>${fmt(bugunEsit)}</strong> değerinde bir alım gücün kalmış.`;
    
    const kayipTL = miktar - bugunEsit;
    const ipAdet = Math.floor(kayipTL/75000);
    document.getElementById('gercekHayat').innerHTML = ipAdet > 0 ? `Buhar olan bu parayla tam <strong>${ipAdet} tane iPhone</strong> alabilirdin.` : `Paran göz göre göre erimiş.`;

    document.getElementById('results').classList.add('show');
    document.getElementById('results').scrollIntoView({behavior:'smooth', block:'start'});
}

// Twitter Paylaşım
function paylas() {
    if(!_state) return;
    const msgs = [
        `${_state.yil} yılında ${_state.miktar.toLocaleString('tr-TR')} TL birikimim vardı. Bugün alım gücü sadece ${fmt(_state.bugunEsit)}. %${_state.kayipYuzde} erime... Şaka gibi.`,
        `O gün parayı ${_state.yil}'de kenara koyacağıma BIST'e koysaydım bugün ${fmt(_state.bistBugün)} param vardı. Biz yastık altına güvendik, enflasyon bizi yedi.`,
        "Ekonomi testi sonucum: %" + _state.kayipYuzde + " kayıp. Alım gücüm bitmiş. Detaylar burada: " + SITE_URL
    ];
    const text = msgs[Math.floor(Math.random()*msgs.length)];
    window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}`, '_blank');
}

// Başlatıcı
document.addEventListener('DOMContentLoaded', () => {
    yukleCanli();
    document.getElementById('lastUpdate').textContent = `Son Güncelleme: 13.04.2026 - 17:00`;
    
    const miktarInput = document.getElementById('miktar');
    miktarInput.addEventListener('input', (e) => {
        let val = e.target.value.replace(/\D/g, "");
        e.target.value = val ? Number(val).toLocaleString('tr-TR') : "";
    });

    document.getElementById('calcBtn').addEventListener('click', hesapla);
    document.getElementById('tweetAllBtn').addEventListener('click', paylas);
    document.querySelectorAll('.widget-share-btn').forEach(btn => btn.addEventListener('click', paylas));
});
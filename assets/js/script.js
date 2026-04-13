const DATA = {
    2005:{usd:1.34,altin:24,gumus:0.42,konut:830,enfKayip:28.0,btc:null},
    2006:{usd:1.43,altin:28,gumus:0.52,konut:980,enfKayip:25.0,btc:null},
    2007:{usd:1.17,altin:33,gumus:0.60,konut:1170,enfKayip:22.5,btc:null},
    2008:{usd:1.51,altin:40,gumus:0.72,konut:1350,enfKayip:20.0,btc:null},
    2009:{usd:1.49,altin:48,gumus:0.78,konut:1450,enfKayip:18.0,btc:null},
    2010:{usd:1.54,altin:56,gumus:1.05,konut:1570,enfKayip:16.0,btc:0.07},
    2011:{usd:1.88,altin:82,gumus:1.75,konut:1750,enfKayip:14.0,btc:4},
    2012:{usd:1.78,altin:96,gumus:1.72,konut:1920,enfKayip:12.5,btc:13},
    2013:{usd:2.13,altin:87,gumus:1.40,konut:2120,enfKayip:11.0,btc:800},
    2014:{usd:2.33,altin:88,gumus:1.35,konut:2310,enfKayip:9.8,btc:320},
    2015:{usd:2.92,altin:100,gumus:1.38,konut:2520,enfKayip:8.5,btc:430},
    2016:{usd:3.52,altin:120,gumus:1.95,konut:2750,enfKayip:7.5,btc:960},
    2017:{usd:3.79,altin:148,gumus:2.05,konut:3020,enfKayip:6.5,btc:13000},
    2018:{usd:5.28,altin:228,gumus:2.80,konut:3450,enfKayip:5.2,btc:3800},
    2019:{usd:5.94,altin:290,gumus:3.35,konut:3950,enfKayip:4.3,btc:7200},
    2020:{usd:7.44,altin:490,gumus:6.35,konut:5050,enfKayip:3.5,btc:29000},
    2021:{usd:13.3,altin:520,gumus:7.10,konut:7600,enfKayip:2.8,btc:46000},
    2022:{usd:18.7,altin:1010,gumus:12.0,konut:14000,enfKayip:2.1,btc:16500},
    2023:{usd:29.5,altin:1900,gumus:22.5,konut:23000,enfKayip:1.55,btc:43000},
    2024:{usd:32.5,altin:2850,gumus:30.5,konut:32000,enfKayip:1.22,btc:67000},
    2025:{usd:38.0,altin:3900,gumus:41.0,konut:45000,enfKayip:1.18,btc:85000},
    2026:{usd:42.0,altin:4550,gumus:45.0,konut:58000,enfKayip:1.0,btc:95000},
};

let BUGUN = {usd:42.0, altin:4550, gumus:45.0, btc:95000, konut:58000};
const STATIC_BUGUN = {...BUGUN};
const SITE_URL = window.location.href;
let _state = null;

// Formatter Helpers
const fmt = (n) => {
    if(n>=1e9) return (n/1e9).toFixed(1) + ' Milyar TL';
    if(n>=1e6) return (n/1e6).toFixed(1) + ' Milyon TL';
    return Math.round(n).toLocaleString('tr-TR') + ' TL';
};
const fmtKat = (n) => (!isFinite(n) ? '—' : 'x' + (n<10 ? n.toFixed(2) : Math.round(n).toLocaleString('tr-TR')) + ' kat');
const fmtBar = (n) => (!isFinite(n) ? '—' : (n<10 ? n.toFixed(2) : Math.round(n).toLocaleString('tr-TR')) + 'x');
const fmtM2 = (n) => n.toFixed(1) + ' m²';

const updateBadge = (msg, ok=true) => {
    const b = document.getElementById('liveBadge');
    if(b) { b.textContent = msg; b.classList.toggle('warn', !ok); }
};

async function yukleCanli() {
    updateBadge('Canlı veriler yükleniyor…', true);
    try {
        const [fx, xau, xag, btc] = await Promise.all([
            fetch('https://open.er-api.com/v6/latest/USD',{cache:'no-store'}).then(r=>r.json()).catch(()=>null),
            fetch('https://api.gold-api.com/price/XAU',{cache:'no-store'}).then(r=>r.json()).catch(()=>null),
            fetch('https://api.gold-api.com/price/XAG',{cache:'no-store'}).then(r=>r.json()).catch(()=>null),
            fetch('https://api.gold-api.com/price/BTC',{cache:'no-store'}).then(r=>r.json()).catch(()=>null),
        ]);
        const OTG = 31.1034768;
        if(fx?.rates?.TRY) BUGUN.usd = fx.rates.TRY;
        const xauUsd = xau?.price ?? xau?.price_usd ?? null;
        const xagUsd = xag?.price ?? xag?.price_usd ?? null;
        const btcUsd = btc?.price ?? btc?.price_usd ?? null;
        
        if(xauUsd) BUGUN.altin = xauUsd/OTG * BUGUN.usd;
        if(xagUsd) BUGUN.gumus = xagUsd/OTG * BUGUN.usd;
        if(btcUsd) BUGUN.btc = btcUsd;
        
        const ok = !!(fx && xauUsd && xagUsd && btcUsd);
        const s = new Date().toLocaleTimeString('tr-TR',{hour:'2-digit',minute:'2-digit'});
        updateBadge(ok ? `Canlı · ${s}` : 'Canlı veri kısmen geldi', ok);
        if(_state) hesapla();
    } catch(e) {
        BUGUN = {...STATIC_BUGUN};
        updateBadge('Canlı veri alınamadı · sabit değerler', false);
    }
}

function hesapla() {
    // Noktaları temizleyip sayıya çeviriyoruz
    const miktarRaw = document.getElementById('miktar').value.replace(/\./g, "");
    const miktar = parseFloat(miktarRaw);
    const yil = parseInt(document.getElementById('yil').value);
    
    if(!miktar || miktar <= 0) { document.getElementById('miktar').focus(); return; }
    
    const d = DATA[yil];
    if(!d) return;

    const bugunEsit = miktar / d.enfKayip;
    const kayip = ((1 - 1/d.enfKayip) * 100).toFixed(0);
    const dolarBugün = (miktar/d.usd) * BUGUN.usd;
    const altinBugün = (miktar/d.altin) * BUGUN.altin;
    const gumusBugün = (miktar/d.gumus) * BUGUN.gumus;
    const evM2 = miktar / d.konut;
    const evBugün = evM2 * BUGUN.konut;
    let btcBugün = null;
    if(d.btc) btcBugün = ((miktar/d.usd)/d.btc) * BUGUN.btc * BUGUN.usd;

    const sec = [{ad:'Dolar',deger:dolarBugün},{ad:'Altın',deger:altinBugün},{ad:'Gümüş',deger:gumusBugün},{ad:'Konut',deger:evBugün}];
    if(btcBugün) sec.push({ad:'BTC',deger:btcBugün});
    const enIyi = sec.reduce((a,b) => b.deger > a.deger ? b : a);
    const kayipTL = miktar - bugunEsit;

    _state = {miktar, yil, bugunEsit, kayip, dolarBugün, altinBugün, gumusBugün, btcBugün, evBugün, evM2, kayipTL, enIyi};

    document.getElementById('bugunDeger').textContent = fmt(bugunEsit);
    document.getElementById('kayipBadge').textContent = `%${kayip} eridi`;
    document.getElementById('lossDesc').textContent = `${yil} yılında ${miktar.toLocaleString('tr-TR')} TL olan birikimin, bugün sadece ${fmt(bugunEsit)} değerinde.`;
    
    document.getElementById('dolarDeger').textContent = fmt(dolarBugün);
    document.getElementById('dolarKat').textContent = fmtKat(dolarBugün/miktar);
    document.getElementById('altinDeger').textContent = fmt(altinBugün);
    document.getElementById('altinKat').textContent = fmtKat(altinBugün/miktar);
    document.getElementById('gumusDeger').textContent = fmt(gumusBugün);
    document.getElementById('gumusKat').textContent = fmtKat(gumusBugün/miktar);

    if(btcBugün) {
        document.getElementById('btcDeger').textContent = fmt(btcBugün);
        document.getElementById('btcKat').textContent = fmtKat(btcBugün/miktar);
        document.getElementById('btcBarRow').style.display = 'flex';
    } else {
        document.getElementById('btcDeger').textContent = 'N/A';
        document.getElementById('btcKat').textContent = yil < 2010 ? 'BTC yoktu' : '—';
        document.getElementById('btcBarRow').style.display = 'none';
    }

    document.getElementById('evDeger').textContent = fmt(evBugün);
    document.getElementById('evKat').textContent = fmtKat(evBugün/miktar);
    document.getElementById('evMetin').innerHTML = `${yil} yılında bu parayla yaklaşık <strong>${fmtM2(evM2)}</strong> konut payı alabiliyordun. Aynı pay bugün yaklaşık <strong>${fmt(evBugün)}</strong> ediyor.`;

    const maxVal = Math.max(1/d.enfKayip, dolarBugün/miktar, altinBugün/miktar, gumusBugün/miktar, evBugün/miktar, btcBugün ? btcBugün/miktar : 0);
    setTimeout(() => {
        const s = (id, tid, val) => {
            const el = document.getElementById(id);
            const tel = document.getElementById(tid);
            if(el) { el.style.width = Math.max(2, val/maxVal * 100) + '%'; tel.textContent = fmtBar(val); }
        };
        s('bTL','bTLt',1/d.enfKayip); s('bUSD','bUSDt',dolarBugün/miktar); s('bGold','bGoldt',altinBugün/miktar);
        s('bSilver','bSilvert',gumusBugün/miktar); if(btcBugün) s('bBTC','bBTCt',btcBugün/miktar);
    }, 80);

    document.getElementById('yorum').innerHTML = `${yil} yılındaki <strong>${miktar.toLocaleString('tr-TR')} TL</strong>'nin satın alma gücünün <strong>%${kayip}'si</strong> eridi. En iyi sonuç <strong>${enIyi.ad}</strong> olurdu.`;
    
    const kiraAdet = Math.floor(kayipTL/15000), ipAdet = Math.floor(kayipTL/70000), tatAdet = Math.floor(kayipTL/20000);
    const p = [];
    if(kiraAdet > 0) p.push(`<strong>${kiraAdet} kira</strong>`);
    if(ipAdet > 0) p.push(`<strong>${ipAdet} iPhone</strong>`);
    if(tatAdet > 0) p.push(`<strong>${tatAdet} tatil</strong>`);
    
    document.getElementById('gercekHayat').innerHTML = p.length 
        ? `Bu erimeyle yaklaşık <strong>${fmt(kayipTL)}</strong> kaybettin. Bu parayla bugün ${p.join(', ')} alabilirdin.` 
        : `Bu erimeyle yaklaşık <strong>${fmt(kayipTL)}</strong> kaybettin.`;

    document.getElementById('results').classList.add('show');
    setTimeout(() => document.getElementById('results').scrollIntoView({behavior:'smooth', block:'start'}), 50);
}

function buildTweet(wid) {
    if(!_state) return "";
    const {miktar, yil, kayip, bugunEsit, dolarBugün, altinBugün, evBugün, btcBugün, enIyi} = _state;
    const base = `${SITE_URL}\n#TL #Enflasyon #Ekonomi`;
    if(!wid) return `${yil}'te ${miktar.toLocaleString('tr-TR')} TL birikimim vardı.\n\nBugün değeri: ${fmt(bugunEsit)} (%${kayip} eridi).\n\nEn iyi: ${enIyi.ad}\n\n${base}`;
    return `TL Hafıza Makinesi Sonuçları\n${base}`;
}

async function shareWidget(wid) {
    if(!_state) return;
    const note = document.getElementById('shareNote');
    const tweet = buildTweet(wid);
    const el = document.getElementById(wid);
    note.textContent = 'Görsel oluşturuluyor…';
    
    try {
        const canvas = await html2canvas(el, {
            backgroundColor: null, scale: 2, useCORS: true, logging: false,
            ignoreElements: n => n.classList && (n.classList.contains('widget-share-btn') || n.classList.contains('share-row') || n.classList.contains('card-share-row'))
        });
        
        if(/iPhone|iPad|iPod|Android/i.test(navigator.userAgent) && navigator.share) {
            canvas.toBlob(async blob => {
                const file = new File([blob], 'tl-hafiza.png', {type: 'image/png'});
                await navigator.share({files: [file], text: tweet});
                note.textContent = 'Paylaşım açıldı.';
            });
        } else {
            const dataUrl = canvas.toDataURL('image/png');
            const a = document.createElement('a');
            a.href = dataUrl; a.download = `tl-hafiza-${_state.yil}.png`;
            document.body.appendChild(a); a.click(); document.body.removeChild(a);
            note.textContent = '✓ Görsel indirildi! X açılıyor…';
            setTimeout(() => window.open('https://twitter.com/intent/tweet?text=' + encodeURIComponent(tweet), '_blank'), 700);
        }
    } catch(err) { window.open('https://twitter.com/intent/tweet?text=' + encodeURIComponent(tweet), '_blank'); }
}

// Binlik Ayırıcı Maskesi ve Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    yukleCanli();
    
    const miktarInput = document.getElementById('miktar');
    
    // Yazarken formatlama
    miktarInput.addEventListener('input', function(e) {
        let value = e.target.value.replace(/\D/g, "");
        if (value !== "") {
            e.target.value = Number(value).toLocaleString('tr-TR');
        } else {
            e.target.value = "";
        }
    });

    document.getElementById('calcBtn').addEventListener('click', hesapla);
    document.getElementById('tweetAllBtn').addEventListener('click', () => {
        if(_state) window.open('https://twitter.com/intent/tweet?text=' + encodeURIComponent(buildTweet(null)), '_blank');
    });

    document.querySelectorAll('.widget-share-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const wid = e.currentTarget.getAttribute('data-widget');
            shareWidget(wid);
        });
    });

    miktarInput.addEventListener('keydown', e => { if(e.key === 'Enter') hesapla(); });
});
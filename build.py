"""reckfulshop.uz - Reckful vitrina sayti (statik). Mahsulotlar lifesportpit.uz feed'idan olinadi,
"Sotib olish" tugmasi lifesportpit.uz dagi mahsulot sahifasiga olib boradi.

    python build.py            # feed'ni yuklab, site/index.html ni yangilaydi
    python build.py feed.csv   # lokal fayldan
"""
import csv
import html
import io
import json
import sys
import urllib.request
from pathlib import Path

FEED = "https://lifesportpit.uz/meta-feed.csv?brend=Reckful"
SHOP = "https://lifesportpit.uz"
DOMAIN = "reckfulshop.uz"
UTM = "utm_source=reckfulshop&utm_medium=referral"
OUT = Path(__file__).parent / "site"


def load(src=None):
    if src:
        text = Path(src).read_text(encoding="utf-8")
    else:
        req = urllib.request.Request(FEED, headers={"User-Agent": "reckfulshop-build"})
        text = urllib.request.urlopen(req, timeout=60).read().decode("utf-8")
    rows = list(csv.DictReader(io.StringIO(text)))
    if len(rows) < 5:  # bo'sh feed bilan saytni bo'shatib qo'ymaslik
        raise SystemExit(f"feed juda kam: {len(rows)} ta")
    return rows


def som(v):
    n = int("".join(c for c in v if c.isdigit()) or 0)
    return f"{n:,}".replace(",", " ")


def card(r):
    e = html.escape
    title = r["title"].strip()
    name = title[8:] if title.lower().startswith("reckful ") else title
    img = r["image_link"].replace("/media/", "/img/800/")
    link = r["link"] + ("&" if "?" in r["link"] else "?") + UTM
    cat = r["product_type"] or "Boshqa"
    sale = r["sale_price"]
    price = (f'<s>{som(r["price"])}</s> <b>{som(sale)} so\'m</b>' if sale else f'<b>{som(r["price"])} so\'m</b>')
    return (f'<a class="card" href="{e(link)}" data-cat="{e(cat)}" data-name="{e(title.lower())}">'
            f'<span class="ph"><img src="{e(img)}" alt="{e(title)}" loading="lazy" width="400" height="400"></span>'
            f'<span class="cat">{e(cat)}</span><span class="name">{e(name)}</span>'
            f'<span class="price">{price}</span><span class="buy">Sotib olish</span></a>')


def build(rows):
    cats = []
    for r in rows:
        c = r["product_type"] or "Boshqa"
        if c not in cats:
            cats.append(c)
    cats.sort(key=lambda c: (c == "Boshqa", c))
    chips = '<button class="chip on" data-cat="">Hammasi</button>' + "".join(
        f'<button class="chip" data-cat="{html.escape(c)}">{html.escape(c)}</button>' for c in cats)
    ld = {"@context": "https://schema.org", "@type": "ItemList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": r["title"], "url": r["link"]}
        for i, r in enumerate(rows)]}
    page = TEMPLATE
    for k, v in {"@@CHIPS@@": chips, "@@CARDS@@": "\n".join(card(r) for r in rows), "@@N@@": str(len(rows)),
                 "@@LD@@": json.dumps(ld, ensure_ascii=False), "@@SHOP@@": SHOP, "@@UTM@@": UTM,
                 "@@DOMAIN@@": DOMAIN}.items():
        page = page.replace(k, v)
    OUT.mkdir(exist_ok=True)
    (OUT / "index.html").write_text(page, encoding="utf-8")
    (OUT / "CNAME").write_text(DOMAIN + "\n", encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: https://{DOMAIN}/sitemap.xml\n",
                                    encoding="utf-8")
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f"<url><loc>https://{DOMAIN}/</loc></url></urlset>\n", encoding="utf-8")
    print(f"{len(rows)} ta mahsulot -> {OUT / 'index.html'}")


TEMPLATE = r"""<!doctype html>
<html lang="uz">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Reckful O'zbekistonda — pre-workout, kreatin, protein | reckfulshop.uz</title>
<meta name="description" content="Reckful sport ozuqalari Toshkentda: pre-workout, kreatin, protein, vitaminlar. @@N@@ ta mahsulot, narxlar so'mda. Xarid LIFESPORT (lifesportpit.uz) orqali — 11 filial va yetkazib berish.">
<link rel="canonical" href="https://@@DOMAIN@@/">
<meta property="og:title" content="Reckful O'zbekistonda — reckfulshop.uz">
<meta property="og:description" content="Reckful mahsulotlari LIFESPORT do'konlarida. Narxlar so'mda, yetkazib berish bor.">
<meta property="og:type" content="website">
<meta name="theme-color" content="#0b0812">
<script type="application/ld+json">@@LD@@</script>
<style>
:root{--bg:#0b0812;--bg2:#15101f;--line:#2a2140;--tx:#f4f1fa;--mut:#a79fba;--ac:#8b3dff;--ac2:#b98cff;--ok:#c8ff3d}
*{box-sizing:border-box;margin:0}
html{scroll-behavior:smooth}
body{background:var(--bg);color:var(--tx);font:16px/1.45 "Segoe UI",Roboto,Arial,sans-serif;-webkit-font-smoothing:antialiased}
a{color:inherit;text-decoration:none}
.wrap{max-width:1180px;margin:0 auto;padding:0 16px}
.tick{background:var(--ac);overflow:hidden;white-space:nowrap;font-size:12px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;padding:7px 0}
.tick span{display:inline-block;padding-right:48px;animation:mq 28s linear infinite}
@keyframes mq{to{transform:translateX(-100%)}}
header{position:sticky;top:0;z-index:5;background:rgba(11,8,18,.92);backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}
header .wrap{display:flex;align-items:center;gap:16px;height:60px}
.logo{font-weight:900;letter-spacing:.32em;font-size:18px}
.logo i{font-style:normal;color:var(--ac2);letter-spacing:.2em;font-size:11px;margin-left:6px}
header nav{margin-left:auto;display:flex;gap:18px;font-size:14px;color:var(--mut)}
header nav a:hover{color:var(--tx)}
.btn{display:inline-block;background:var(--ac);color:#fff;font-weight:800;text-transform:uppercase;letter-spacing:.06em;font-size:13px;padding:13px 22px;border:1px solid var(--ac);transition:.15s}
.btn:hover{background:transparent;color:var(--ac2)}
.btn.ghost{background:transparent;border-color:var(--line);color:var(--tx)}
.btn.ghost:hover{border-color:var(--ac2)}
.hero{position:relative;overflow:hidden;border-bottom:1px solid var(--line);background:radial-gradient(900px 420px at 85% 0,#3a1a78 0,transparent 60%),linear-gradient(180deg,#120c1e,#0b0812)}
.hero .wrap{padding:64px 16px 56px;position:relative}
.hero .big{position:absolute;right:-10px;top:8px;font-size:clamp(70px,17vw,210px);font-weight:900;letter-spacing:.06em;color:transparent;-webkit-text-stroke:1px rgba(185,140,255,.18);pointer-events:none;user-select:none;line-height:1}
.tag{display:inline-block;border:1px solid var(--ac2);color:var(--ac2);font-size:11px;font-weight:700;letter-spacing:.2em;text-transform:uppercase;padding:5px 10px;margin-bottom:18px}
h1{font-size:clamp(30px,6vw,60px);line-height:1.02;font-weight:900;text-transform:uppercase;max-width:760px}
h1 em{font-style:normal;background:var(--tx);color:var(--bg);padding:0 .15em}
.hero p{color:var(--mut);max-width:560px;margin:18px 0 26px;font-size:17px}
.hero .row{display:flex;gap:12px;flex-wrap:wrap}
.feat{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:var(--line);border-bottom:1px solid var(--line)}
.feat div{background:var(--bg);padding:20px 16px;font-size:14px;color:var(--mut)}
.feat b{display:block;color:var(--tx);font-size:15px;text-transform:uppercase;letter-spacing:.04em;margin-bottom:4px}
section{padding:44px 0}
h2{font-size:clamp(22px,4vw,34px);font-weight:900;text-transform:uppercase;letter-spacing:.02em;margin-bottom:18px}
.tools{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-bottom:20px}
.chip{background:transparent;color:var(--mut);border:1px solid var(--line);padding:9px 14px;font:inherit;font-size:13px;font-weight:600;cursor:pointer}
.chip.on,.chip:hover{color:#fff;border-color:var(--ac);background:rgba(139,61,255,.18)}
#q{flex:1 1 220px;min-width:0;background:var(--bg2);border:1px solid var(--line);color:var(--tx);padding:10px 14px;font:inherit;font-size:14px;outline:0}
#q:focus{border-color:var(--ac)}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}
.card{display:flex;flex-direction:column;background:var(--bg2);border:1px solid var(--line);padding:12px;transition:.15s}
.card:hover{border-color:var(--ac);transform:translateY(-3px)}
.ph{display:block;background:#fff;aspect-ratio:1;overflow:hidden;margin-bottom:12px}
.ph img{width:100%;height:100%;object-fit:contain;display:block}
.cat{font-size:11px;color:var(--ac2);text-transform:uppercase;letter-spacing:.1em;font-weight:700}
.name{font-weight:800;text-transform:uppercase;font-size:14px;line-height:1.25;margin:6px 0 10px;flex:1}
.price{font-size:17px;margin-bottom:12px}
.price s{color:var(--mut);font-size:13px}
.buy{display:block;text-align:center;background:var(--ac);font-weight:800;text-transform:uppercase;font-size:12px;letter-spacing:.08em;padding:11px}
.card:hover .buy{background:var(--ok);color:#111}
#empty{display:none;color:var(--mut);padding:30px 0}
.how{background:var(--bg2);border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
.steps{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
.steps div{border:1px solid var(--line);padding:20px;color:var(--mut);font-size:15px}
.steps b{display:block;color:var(--ac2);font-size:34px;font-weight:900;line-height:1;margin-bottom:10px}
.steps strong{color:var(--tx);display:block;text-transform:uppercase;margin-bottom:4px}
footer{padding:34px 0 46px;color:var(--mut);font-size:14px}
footer .wrap{display:flex;gap:24px;flex-wrap:wrap;justify-content:space-between}
footer a{color:var(--tx);border-bottom:1px solid var(--line)}
footer small{display:block;margin-top:10px;max-width:560px;font-size:12px}
@media(max-width:900px){.grid{grid-template-columns:repeat(3,1fr)}.feat{grid-template-columns:repeat(2,1fr)}}
@media(max-width:640px){.grid{grid-template-columns:repeat(2,1fr);gap:10px}.steps{grid-template-columns:1fr}header nav a.hide{display:none}.card{padding:8px}.name{font-size:12.5px}.price{font-size:15px}.hero .wrap{padding:44px 16px 40px}}
@media(prefers-reduced-motion:reduce){.tick span{animation:none}html{scroll-behavior:auto}}
</style>
</head>
<body>
<div class="tick" aria-hidden="true"><span>Reckful O'zbekistonda • narxlar so'mda • Toshkent bo'ylab yetkazib berish • viloyatlarga BTS • 11 filialdan olib ketish •</span><span>Reckful O'zbekistonda • narxlar so'mda • Toshkent bo'ylab yetkazib berish • viloyatlarga BTS • 11 filialdan olib ketish •</span><span>Reckful O'zbekistonda • narxlar so'mda • Toshkent bo'ylab yetkazib berish • viloyatlarga BTS • 11 filialdan olib ketish •</span></div>
<header><div class="wrap">
<a class="logo" href="#top">RECKFUL<i>SHOP.UZ</i></a>
<nav><a href="#katalog">Katalog</a><a class="hide" href="#qanday">Qanday xarid qilinadi</a><a href="@@SHOP@@/katalog?brend=Reckful&@@UTM@@">LIFESPORT</a></nav>
</div></header>

<div class="hero" id="top"><div class="wrap">
<div class="big" aria-hidden="true">RECKFUL</div>
<span class="tag">LIFESPORT do'koni</span>
<h1>Reckful — endi <em>O'zbekistonda</em></h1>
<p>Pre-workout, kreatin, protein va vitaminlar. @@N@@ ta mahsulot sotuvda. Xarid LIFESPORT sayti orqali: tanlang, bosing, buyurtma bering.</p>
<div class="row"><a class="btn" href="#katalog">Katalogni ko'rish</a><a class="btn ghost" href="@@SHOP@@/katalog?brend=Reckful&@@UTM@@">lifesportpit.uz da ochish</a></div>
</div></div>

<div class="feat">
<div><b>Sertifikatlangan</b>Mahsulotlar sertifikat bilan</div>
<div><b>11 filial</b>Toshkentda olib ketish</div>
<div><b>Yetkazib berish</b>Toshkent va viloyatlar</div>
<div><b>Ball tizimi</b>Har xariddan ball yig'iladi</div>
</div>

<section id="katalog"><div class="wrap">
<h2>Katalog</h2>
<div class="tools">@@CHIPS@@<input id="q" type="search" placeholder="Qidirish: kreatin, whey, pump…" aria-label="Mahsulot qidirish"></div>
<div class="grid" id="grid">
@@CARDS@@
</div>
<p id="empty">Hech narsa topilmadi.</p>
</div></section>

<section class="how" id="qanday"><div class="wrap">
<h2>Qanday xarid qilinadi</h2>
<div class="steps">
<div><b>01</b><strong>Mahsulotni tanlang</strong>Katalogdan keraklisini toping.</div>
<div><b>02</b><strong>«Sotib olish» ni bosing</strong>LIFESPORT saytidagi mahsulot sahifasi ochiladi.</div>
<div><b>03</b><strong>Buyurtma bering</strong>Savatga qo'shing, yetkazib berish yoki filialdan olib ketishni tanlang.</div>
</div>
</div></section>

<footer><div class="wrap">
<div><b style="color:var(--tx);letter-spacing:.2em">RECKFUL SHOP.UZ</b>
<small>Bu sayt LIFESPORT sport ozuqalari do'konining Reckful mahsulotlari vitrinasi. Barcha buyurtmalar va to'lovlar lifesportpit.uz saytida amalga oshiriladi. Narxlar va qoldiq o'sha saytda yangilanadi.</small></div>
<div>Buyurtma va savollar:<br><a href="tel:+998555169916">55 516 99 16</a><br><br><a href="@@SHOP@@/?@@UTM@@">lifesportpit.uz</a></div>
</div></footer>

<script>
(function(){
var cards=[].slice.call(document.querySelectorAll('.card')),chips=[].slice.call(document.querySelectorAll('.chip')),
q=document.getElementById('q'),empty=document.getElementById('empty'),cat='';
function run(){var s=q.value.trim().toLowerCase(),n=0;
cards.forEach(function(c){var ok=(!cat||c.dataset.cat===cat)&&(!s||c.dataset.name.indexOf(s)>-1);c.style.display=ok?'':'none';if(ok)n++});
empty.style.display=n?'none':'block'}
chips.forEach(function(b){b.onclick=function(){cat=b.dataset.cat;chips.forEach(function(x){x.classList.toggle('on',x===b)});run()}});
q.oninput=run})();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    build(load(sys.argv[1] if len(sys.argv) > 1 else None))

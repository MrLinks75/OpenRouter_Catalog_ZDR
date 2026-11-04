#!/usr/bin/env python3
"""Régénère l'infographie depuis models.json.
Usage :
  python3 scripts/build.py data/models.json site --page     -> site/index.html (GitHub Pages)
  python3 scripts/build.py data/models.json OUT_DIR          -> OUT_DIR/Main.dc.html + canvas.json (canevas Claude)"""
import json, html, sys, os
args = [a for a in sys.argv[1:] if not a.startswith("--")]
PAGE = "--page" in sys.argv
DATA = json.load(open(args[0], encoding="utf-8"))
OUT = args[1] if len(args) > 1 else "."
os.makedirs(OUT, exist_ok=True)
C = {"V": ("#14532D", "#D7F0DF", "#1F8A4C"), "O": ("#7C2D12", "#FDE6C8", "#D97706"), "R": ("#7F1D1D", "#FADADA", "#DC2626")}
BUD = {"V": "Vert · c'est parti mon kiki", "O": "Orange · assez consommateur", "R": "Rouge · à vos risques et périls"}
USE = {"V": "Vert · tous les jours", "O": "Orange · cas d'usage précis", "R": "Rouge · à éviter / dernier recours"}
BUD_S = {"V": "Budget léger", "O": "Budget modéré", "R": "Budget lourd"}
USE_S = {"V": "Quotidien", "O": "Cas précis", "R": "Dernier recours"}

EU = [(m["vendor"], m["model"], m["hosts"], m["price_in"], m["price_out"], m["intel"], m["coding_agent"],
       None if m["swe"] is None else (m["swe"]["value"], m["swe"]["kind"]),
       None if m["mmmu"] is None else (m["mmmu"]["value"], m["mmmu"]["kind"]),
       m["speed"], m["budget"], m["usage"], m["note"], m.get("discount") or 0) for m in DATA["models"]]
W, H = 1600, 1320 + 82 * len(DATA["models"])
EU.sort(key=lambda r: ((3*r[3]+r[4])/4, r[3]))
from datetime import date as _d
def frdate(iso):
    mois = ['janvier','février','mars','avril','mai','juin','juillet','août','septembre','octobre','novembre','décembre']
    y, mo, da = map(int, iso.split('-'))
    return f'{da} {mois[mo-1]} {y}'


def fp(x):
    if x >= 10:
        return f"{x:.0f}"
    return (f"{x:.2f}" if x >= 0.1 or round(x, 2) == x else f"{x:.3f}").replace(".", ",")

cols = "215px 175px 78px 78px 112px 112px 112px 104px 66px 130px 186px"
GAP = 12
INK, MUTED, LINE, NAVY = "#111827", "#4B5563", "#E5E7EB", "#1E3A5F"

def esc(s): return html.escape(str(s), quote=True)

def bar(v, maxv=100, color=NAVY):
    if v is None:
        return f'<span style="font-size: 13px; color: #6B7280">n.d.</span>'
    w = max(2, round(v / maxv * 100))
    txt = (f"{v:.1f}".replace(".", ",") if isinstance(v, float) and v != int(v) else str(int(v)))
    return (f'<div style="display: flex; flex-direction: column; gap: 4px">'
            f'<span style="font-size: 17px; font-weight: 700; color: {INK}">{txt}</span>'
            f'<div style="height: 6px; background: #EEF1F5; border-radius: 3px; width: 100%"><div style="height: 6px; border-radius: 3px; background: {color}; width: {w}%"></div></div></div>')

def tagval(t):
    if t is None:
        return '<span style="font-size: 13px; color: #6B7280">n.d.</span>'
    v, k = t
    if v == "texte":
        return '<span style="font-size: 12px; color: #6B7280">texte seul</span>'
    suf = ""
    if k == "P": suf = '<span style="font-size: 11px; color: #4B5563; margin-left: 4px">Pro</span>'
    elif k == "V": suf = '<span style="font-size: 11px; color: #4B5563; margin-left: 4px">Verified</span>'
    elif k == "°": suf = '<span style="font-size: 11px; color: #4B5563; margin-left: 4px">effort normal</span>'
    return f'<span style="font-size: 17px; font-weight: 700; color: {INK}">{v}<span style="font-size: 12px">%</span></span>{suf}'

def chip(code, label):
    fg, bg, dot = C[code]
    return (f'<span style="display: inline-flex; align-items: center; gap: 6px; padding: 5px 10px; border-radius: 999px; background: {bg}; color: {fg}; font-size: 13px; font-weight: 700; white-space: nowrap">'
            f'<span style="width: 10px; height: 10px; border-radius: 5px; background: {dot}"></span>{esc(label)}</span>')

def header_row():
    heads = ["Modèle", "Hébergeurs", "Entrée<br>$/M tokens", "Sortie<br>$/M tokens", "Intelligence<br>AA Index v5", "Codage avancé<br>AA Coding Agent", "Codage standard<br>SWE-bench", "Multimodal<br>MMMU-Pro", "Vitesse<br>tok/s", "Budget", "Utilisation"]
    cells = "".join(f'<div style="font-size: 12px; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase; color: {MUTED}; line-height: 1.35">{h}</div>' for h in heads)
    return f'<div style="display: grid; grid-template-columns: {cols}; column-gap: {GAP}px; padding: 12px 20px; border-bottom: 2px solid {INK}; align-items: end">{cells}</div>'

def row(r, dim=False):
    v, m, host, pin, pout, intel, cadv, cstd, mm, spd, b, u, note, disc = r
    spd_s = f'<span style="font-size: 15px; font-weight: 600; color: {INK}">{spd}</span>' if spd else '<span style="font-size: 13px; color: #6B7280">n.d.</span>'
    def pr(x):
        badge = f'<span style="display: block; font-size: 11px; font-weight: 600; color: #7C2D12">promo -{round(disc*100)} %</span>' if disc else ''
        return f'<span style="font-size: 17px; font-weight: 700; color: {INK}">{fp(x)} $</span>{badge}'
    return (f'<div style="display: grid; grid-template-columns: {cols}; column-gap: {GAP}px; padding: 14px 20px; border-bottom: 1px solid {LINE}; align-items: center; background: #FFFFFF">'
            f'<div style="display: flex; flex-direction: column; gap: 2px"><span style="font-size: 12px; font-weight: 600; color: {MUTED}; text-transform: uppercase; letter-spacing: 0.05em">{esc(v)}</span><span style="font-family: Space Grotesk, sans-serif; font-size: 19px; font-weight: 700; color: {INK}">{esc(m)}</span></div>'
            f'<div style="font-size: 13px; color: #374151; line-height: 1.3">{esc(host)}</div>'
            f'<div>{pr(pin)}</div>'
            f'<div>{pr(pout)}</div>'
            f'<div>{bar(intel, 70)}</div>'
            f'<div>{bar(cadv, 70)}</div>'
            f'<div>{tagval(cstd)}</div>'
            f'<div>{tagval(mm)}</div>'
            f'<div>{spd_s}</div>'
            f'<div>{chip(b, BUD_S[b])}</div>'
            f'<div style="display: flex; flex-direction: column; gap: 6px; align-items: flex-start">{chip(u, USE_S[u])}<span style="font-size: 12px; color: {MUTED}; line-height: 1.3">{esc(note)}</span></div>'
            f'</div>')

def legend_block(title, d):
    items = "".join(f'<div style="display: flex; align-items: center; gap: 10px">{chip(k, ("Léger" if title=="Budget" else "Quotidien") if k=="V" else ("Modéré" if title=="Budget" else "Cas précis") if k=="O" else ("Lourd" if title=="Budget" else "Dernier recours"))}<span style="font-size: 14px; color: #374151">{esc(d[k].split(" · ")[1])}</span></div>' for k in "VOR")
    return f'<div style="display: flex; flex-direction: column; gap: 10px; flex: 1"><span style="font-size: 13px; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; color: {INK}">{title}</span>{items}</div>'

def section_title(t, sub, color):
    return (f'<div style="display: flex; align-items: baseline; gap: 16px; margin-top: 8px">'
            f'<span style="font-family: \'Space Grotesk\', sans-serif; font-size: 28px; font-weight: 700; color: {color}">{t}</span>'
            f'<span style="font-size: 15px; color: {MUTED}">{sub}</span></div>')

def reco(title, code, names, text):
    fg, bg, dot = C[code]
    return (f'<div style="flex: 1; border-radius: 14px; background: {bg}; padding: 20px 22px; display: flex; flex-direction: column; gap: 8px">'
            f'<span style="font-size: 13px; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; color: {fg}">{title}</span>'
            f'<span style="font-family: \'Space Grotesk\', sans-serif; font-size: 22px; font-weight: 700; color: {INK}">{names}</span>'
            f'<span style="font-size: 14px; color: #1F2937; line-height: 1.45">{text}</span></div>')

notes = [(n["title"], n["text"]) for n in DATA["notes"]]
notes_html = "".join(f'<div style="flex: 1; display: flex; flex-direction: column; gap: 6px"><span style="font-size: 13px; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; color: {NAVY}">{t}</span><span style="font-size: 14px; color: #374151; line-height: 1.5">{esc(x)}</span></div>' for t, x in notes)

ROOT = "max-width: 1600px; margin: 0 auto;" if PAGE else f"width: {W}px; height: {H}px;"
body = f'''<div style="{ROOT} box-sizing: border-box; padding: 56px 40px 48px; background: #FFFFFF; font-family: Inter, system-ui, sans-serif; color: {INK}; display: flex; flex-direction: column; gap: 28px">
<div style="display: flex; justify-content: space-between; align-items: flex-end; gap: 40px">
<div style="display: flex; flex-direction: column; gap: 12px">
<span style="font-size: 14px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: {NAVY}">OpenRouter · prix au {esc(frdate(DATA.get("prices_checked", "2026-11-04")))} · scores au {esc(frdate(DATA.get("scores_checked", "2026-11-04")))}</span>
<h1 style="margin: 0; font-family: 'Space Grotesk', sans-serif; font-size: 60px; line-height: 1.02; font-weight: 700; letter-spacing: -0.02em">Quel modèle pour quel usage ?</h1>
<p style="margin: 0; font-size: 19px; color: #374151; max-width: 920px; line-height: 1.45">Les grands modèles Google, OpenAI, Anthropic, Mistral, Kimi, GLM et DeepSeek servis via OpenRouter par des hébergeurs européens (Amazon Bedrock, Azure, Google Vertex, Inceptron, Mistral), en Zero Data Retention, sans entraînement ni partage des prompts.</p>
</div>
<div style="display: flex; gap: 8px; flex-wrap: wrap; justify-content: flex-end; max-width: 420px">
<span style="padding: 8px 14px; border: 1.5px solid {NAVY}; border-radius: 999px; font-size: 14px; font-weight: 600; color: {NAVY}">ZDR</span>
<span style="padding: 8px 14px; border: 1.5px solid {NAVY}; border-radius: 999px; font-size: 14px; font-weight: 600; color: {NAVY}">Hébergeurs EU</span>
<span style="padding: 8px 14px; border: 1.5px solid {NAVY}; border-radius: 999px; font-size: 14px; font-weight: 600; color: {NAVY}">No training</span>
<span style="padding: 8px 14px; border: 1.5px solid {NAVY}; border-radius: 999px; font-size: 14px; font-weight: 600; color: {NAVY}">No sharing</span>
</div>
</div>
<div style="display: flex; gap: 48px; padding: 24px 28px; border: 1px solid {LINE}; border-radius: 16px">
{legend_block("Budget", BUD)}
{legend_block("Utilisation", USE)}
<div style="display: flex; flex-direction: column; gap: 8px; flex: 1.2"><span style="font-size: 13px; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; color: {INK}">Comment c'est noté</span>
<span style="font-size: 14px; color: #374151; line-height: 1.5"><b>Budget</b> = prix de sortie par million de tokens : vert jusqu’à 2,50 $, orange de 2,50 à 8 $, rouge au-delà.</span>
<span style="font-size: 14px; color: #374151; line-height: 1.5"><b>Utilisation</b> = scores aux benchmarks rapportés au prix, comparés aux autres modèles de la liste.</span></div>
</div>
<div style="display: flex; gap: 16px">
{"".join(reco(esc(r["title"]), r["code"], esc(r["names"]), esc(r["text"])) for r in DATA["recos"])}
</div>
{section_title(f"{len(EU)} modèles, du moins cher au plus cher", "Tri par prix moyen pondéré (3 tokens en entrée pour 1 en sortie)", NAVY)}
<div style="border: 1px solid {LINE}; border-radius: 16px; overflow-x: auto"><div style="min-width: 1520px">
{header_row()}
{"".join(row(r) for r in EU)}
</div></div>
<div style="display: flex; gap: 32px; padding-top: 20px; border-top: 2px solid {INK}">{notes_html}</div>
<div style="font-size: 12px; color: #4B5563">Sources : {esc(DATA["sources"])}</div>
</div>'''

doc = f'''<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<title>Modèles OpenRouter ZDR + EU</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&amp;family=Space+Grotesk:wght@600;700&amp;display=swap" rel="stylesheet">
<style>
body{{margin:0}}
a{{color:{NAVY}}}a:hover{{color:#0F2440}}
</style>
</helmet>
{body}
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":{W},"height":{H}}}}}'>
class Component extends DCLogic {{
renderVals() {{
return {{}};
}}
}}
</script>
</body>
</html>
'''
if PAGE:
    page = f'''<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Quel modèle pour quel usage ? · OpenRouter, hébergeurs européens</title>
<meta name="description" content="Grands modèles d'IA servis via OpenRouter par Bedrock, Azure, Vertex, Inceptron et Mistral : prix, benchmarks, budget et usage recommandé.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&amp;family=Space+Grotesk:wght@600;700&amp;display=swap" rel="stylesheet">
<style>body{{margin:0;background:#FFFFFF}} @media (max-width: 900px) {{ h1{{font-size:40px !important}} }}</style>
</head>
<body>
{body}
</body>
</html>
'''
    open(f"{OUT}/index.html", "w", encoding="utf-8").write(page)
    print(f"{OUT}/index.html", len(page))
    sys.exit(0)
open(f"{OUT}/Main.dc.html", "w", encoding="utf-8").write(doc)
canvas = {"v":3,"createdOnFiles":{"v":1,"at":"2026-11-02T12:00:00Z"},"title":"Infographie modèles OpenRouter — ZDR + EU","launch":{"view":"focused","file":"Main.dc.html"},"pages":[],"boards":{"Main.dc.html":{"x":0,"y":0,"w":W,"h":H,"title":"Modèles ZDR + EU"}},"order":["Main.dc.html"],"notes":{},"designSystems":[]}
json.dump(canvas, open(f"{OUT}/canvas.json","w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(doc))

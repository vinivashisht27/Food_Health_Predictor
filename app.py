import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
import re

# ============================================================================
# PAGE CONFIG  (must be first Streamlit call)
# ============================================================================
st.set_page_config(
    page_title="PureLabel — Nutrition Intelligence",
    page_icon="🥑",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================================
# SESSION STATE
# ============================================================================
_defaults = {
    'view':         'home',
    'product':      None,
    'dark_mode':    True,
    'compare_list': [],
    'favourites':   [],
    'smart_filter': 'All',
    'search_page':  0,
}
for _k, _v in _defaults.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

dark = st.session_state.dark_mode

# ============================================================================
# THEME
# ============================================================================
T = {
    "bg_primary":    "#0B0C10" if dark else "#F4F1EA",
    "bg_secondary":  "#13151B" if dark else "#E8E3D8",
    "bg_card":       "#1A1D26" if dark else "#FFFFFF",
    "bg_card_alt":   "#20232E" if dark else "#FAF7F2",
    "text_primary":  "#F2EFE6" if dark else "#1C1814",
    "text_secondary":"#8E8B84" if dark else "#4A4540",
    "text_muted":    "#4E4C47" if dark else "#9A9590",
    "accent":        "#C9A84C",
    "accent_light":  "#E0BF6A",
    "accent_pale":   "rgba(201,168,76,0.12)" if dark else "rgba(201,168,76,0.10)",
    "accent_border": "rgba(201,168,76,0.25)" if dark else "rgba(201,168,76,0.35)",
    "border":        "rgba(255,255,255,0.07)" if dark else "rgba(28,24,20,0.12)",
    "border_strong": "rgba(255,255,255,0.13)" if dark else "rgba(28,24,20,0.22)",
    "red":           "#D95F5F",
    "red_pale":      "rgba(217,95,95,0.12)",
    "green":         "#4FA882",
    "green_pale":    "rgba(79,168,130,0.12)",
    "blue":          "#5B8FD4",
    "blue_pale":     "rgba(91,143,212,0.12)",
    "yellow":        "#D4A843",
    "yellow_pale":   "rgba(212,168,67,0.12)",
    "chart_grid":    "rgba(255,255,255,0.05)" if dark else "rgba(0,0,0,0.05)",
    "shadow":        "rgba(0,0,0,0.35)"        if dark else "rgba(0,0,0,0.10)",
}
# Keep THEME alias for CSS f-strings from original code
THEME = T

# ============================================================================
# CSS
# ============================================================================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,400&family=DM+Mono:wght@400;500&display=swap');

*, *::before, *::after {{ box-sizing: border-box; margin: 0; }}
html, body, .stApp {{
    background-color: {T['bg_primary']} !important;
    color: {T['text_primary']} !important;
    font-family: 'DM Sans', sans-serif !important;
}}
.stApp {{ transition: background-color 0.35s ease; }}
#MainMenu, footer, header, .stDeployButton {{ visibility: hidden !important; }}
.stDecoration {{ display: none !important; }}
section[data-testid="stSidebar"] {{ display: none !important; }}
[data-testid="stToolbar"] {{ display: none !important; }}
.block-container {{ max-width: 1280px !important; padding: 1.5rem 2.5rem 5rem !important; }}

.pl-wordmark {{
    font-family: 'DM Serif Display', serif;
    font-size: clamp(2.4rem, 4vw, 3.8rem);
    font-weight: 400;
    color: {T['text_primary']};
    letter-spacing: -0.025em;
    line-height: 1.0;
}}
.pl-wordmark em {{ color: {T['accent']}; font-style: italic; }}
.pl-eyebrow {{
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: {T['accent']};
    margin-bottom: 0.4rem;
    display: block;
}}
.pl-section-title {{
    font-family: 'DM Serif Display', serif;
    font-size: 1.75rem;
    font-weight: 400;
    color: {T['text_primary']};
    letter-spacing: -0.01em;
    margin: 2.5rem 0 1.25rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid {T['border']};
}}
.pl-label {{
    font-family: 'DM Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: {T['accent']};
    display: block;
    margin-bottom: 0.35rem;
}}
.pl-value {{
    font-family: 'DM Serif Display', serif;
    font-size: 2.1rem;
    color: {T['text_primary']};
    line-height: 1.1;
}}
.pl-sub {{ font-size: 0.8rem; color: {T['text_muted']}; margin-top: 0.25rem; }}
p, li {{ color: {T['text_secondary']}; line-height: 1.75; font-size: 0.93rem; }}
b, strong {{ color: {T['text_primary']}; }}
small {{ color: {T['text_muted']}; font-size: 0.78rem; }}

.pl-divider {{
    height: 1px;
    background: linear-gradient(90deg, {T['accent']} 0%, transparent 55%);
    margin: 1.25rem 0 1.75rem;
    border: none;
    opacity: 0.7;
}}

.pl-card {{
    background: {T['bg_card']};
    border: 1px solid {T['border_strong']};
    border-radius: 18px;
    padding: 1.5rem 1.75rem;
    margin-bottom: 1rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.25s, transform 0.25s, box-shadow 0.25s;
}}
.pl-card::after {{
    content: '';
    position: absolute;
    inset: 0;
    border-radius: 18px;
    background: linear-gradient(135deg, rgba(201,168,76,0.03), transparent 60%);
    pointer-events: none;
}}
.pl-card:hover {{
    border-color: {T['accent_border']};
    transform: translateY(-2px);
    box-shadow: 0 12px 36px {T['shadow']};
}}
.pl-card-gold   {{ border-left: 3px solid {T['accent']}; }}
.pl-card-red    {{ border-left: 3px solid {T['red']};    background: {T['red_pale']};    border-color: rgba(217,95,95,0.25) !important; }}
.pl-card-green  {{ border-left: 3px solid {T['green']};  background: {T['green_pale']};  border-color: rgba(79,168,130,0.25) !important; }}
.pl-card-blue   {{ border-left: 3px solid {T['blue']};   background: {T['blue_pale']};   border-color: rgba(91,143,212,0.25) !important; }}
.pl-card-yellow {{ border-left: 3px solid {T['yellow']}; background: {T['yellow_pale']}; border-color: rgba(212,168,67,0.25) !important; }}

.stat-tile {{
    background: {T['bg_card']};
    border: 1px solid {T['border_strong']};
    border-radius: 16px;
    padding: 1.25rem 1.5rem;
    text-align: center;
    transition: transform 0.2s, box-shadow 0.2s;
}}
.stat-tile:hover {{ transform: translateY(-3px); box-shadow: 0 8px 24px {T['shadow']}; }}
.stat-tile .st-number {{
    font-family: 'DM Serif Display', serif;
    font-size: 1.9rem;
    color: {T['text_primary']};
    line-height: 1;
}}
.stat-tile .st-unit {{
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    color: {T['accent']};
    letter-spacing: 0.1em;
    text-transform: uppercase;
}}
.stat-tile .st-label {{ font-size: 0.78rem; color: {T['text_muted']}; margin-top: 0.2rem; }}

.nt {{ width: 100%; border-collapse: collapse; font-size: 0.88rem; }}
.nt tr {{ border-bottom: 1px solid {T['border']}; transition: background 0.15s; }}
.nt tr:last-child {{ border-bottom: none; }}
.nt tr:hover {{ background: {T['accent_pale']}; }}
.nt td {{ padding: 0.6rem 0.2rem; color: {T['text_secondary']}; vertical-align: middle; }}
.nt td.nt-val {{ text-align: right; font-family: 'DM Mono', monospace; font-size: 0.84rem; font-weight: 500; color: {T['text_primary']}; }}
.nt td.nt-accent {{ text-align: right; font-family: 'DM Mono', monospace; font-weight: 600; color: {T['accent']}; }}
.nt td.nt-head {{ font-weight: 600; color: {T['text_primary']}; font-size: 0.82rem; padding-top: 1rem; }}
.nt td.nt-indent {{ padding-left: 1.2rem; color: {T['text_muted']}; font-size: 0.84rem; }}

.mb-wrap {{ margin-bottom: 0.9rem; }}
.mb-top {{ display: flex; justify-content: space-between; font-size: 0.8rem; color: {T['text_secondary']}; margin-bottom: 0.3rem; }}
.mb-top span:last-child {{ font-family: 'DM Mono', monospace; font-size: 0.78rem; color: {T['text_primary']}; }}
.mb-track {{ height: 5px; background: {T['border_strong']}; border-radius: 100px; overflow: hidden; }}
.mb-fill {{ height: 100%; border-radius: 100px; transition: width 0.5s ease; }}

.chip {{
    display: inline-block;
    background: {T['accent_pale']};
    color: {T['accent']};
    border: 1px solid {T['accent_border']};
    border-radius: 100px;
    padding: 0.18rem 0.7rem;
    font-size: 0.68rem;
    font-family: 'DM Mono', monospace;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin: 0.15rem 0.25rem 0.15rem 0;
}}
.chip-red   {{ background: {T['red_pale']};   color: {T['red']};   border-color: rgba(217,95,95,0.3); }}
.chip-green {{ background: {T['green_pale']}; color: {T['green']}; border-color: rgba(79,168,130,0.3); }}
.chip-blue  {{ background: {T['blue_pale']};  color: {T['blue']};  border-color: rgba(91,143,212,0.3); }}

.stButton > button {{
    background: transparent !important;
    border: 1px solid {T['border_strong']} !important;
    border-radius: 100px !important;
    color: {T['text_secondary']} !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.04em !important;
    padding: 0.45rem 1.1rem !important;
    transition: all 0.22s ease !important;
}}
.stButton > button:hover {{
    background: {T['accent_pale']} !important;
    border-color: {T['accent']} !important;
    color: {T['accent']} !important;
    box-shadow: 0 0 18px rgba(201,168,76,0.18) !important;
    transform: translateY(-1px) !important;
}}
.stButton > button:active {{ transform: scale(0.97) !important; }}

.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div > div,
.stTextArea textarea {{
    background: {T['bg_card']} !important;
    border: 1px solid {T['border_strong']} !important;
    border-radius: 12px !important;
    color: {T['text_primary']} !important;
    font-family: 'DM Sans', sans-serif !important;
    padding: 0.7rem 1rem !important;
    transition: border-color 0.2s !important;
}}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stTextArea textarea:focus {{
    border-color: {T['accent']} !important;
    box-shadow: 0 0 0 3px {T['accent_pale']} !important;
    outline: none !important;
}}
.stTextInput label, .stNumberInput label, .stSelectbox label, .stTextArea label, .stSlider label {{
    color: {T['text_secondary']} !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.68rem !important;
    letter-spacing: 0.18em !important;
    text-transform: uppercase !important;
}}
div[data-baseweb="select"] > div {{
    background: {T['bg_card']} !important;
    border: 1px solid {T['border_strong']} !important;
    border-radius: 12px !important;
}}
div[data-baseweb="select"] span {{ color: {T['text_primary']} !important; font-family: 'DM Sans', sans-serif !important; }}
.stSlider > div > div > div {{ background: {T['border_strong']} !important; }}
.stSlider [data-testid="stThumbValue"] {{
    background: {T['accent']} !important;
    color: white !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.7rem !important;
}}
.stTabs [data-baseweb="tab-list"] {{ gap: 0.5rem; background: transparent !important; border-bottom: 1px solid {T['border']} !important; }}
.stTabs [data-baseweb="tab"] {{
    background: transparent !important;
    border: none !important;
    color: {T['text_muted']} !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.85rem !important;
    padding: 0.5rem 1rem !important;
    border-bottom: 2px solid transparent !important;
    transition: all 0.2s !important;
}}
.stTabs [aria-selected="true"] {{ color: {T['accent']} !important; border-bottom: 2px solid {T['accent']} !important; }}
[data-baseweb="tag"] {{ background: {T['accent_pale']} !important; border-color: {T['accent_border']} !important; }}
[data-baseweb="tag"] span {{ color: {T['accent']} !important; }}
details summary {{ color: {T['text_secondary']} !important; font-family: 'DM Sans', sans-serif !important; font-size: 0.88rem !important; }}
details {{ background: {T['bg_card_alt']} !important; border: 1px solid {T['border_strong']} !important; border-radius: 12px !important; padding: 0.75rem 1rem !important; }}
.stPlotlyChart iframe, .stPlotlyChart {{ background: transparent !important; }}
[data-testid="stFormSubmitButton"] > button {{
    background: {T['accent_pale']} !important;
    border-color: {T['accent']} !important;
    color: {T['accent']} !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
}}
[data-testid="stFormSubmitButton"] > button:hover {{
    background: {T['accent']} !important;
    color: {T['bg_primary']} !important;
}}
.stCheckbox label {{ color: {T['text_secondary']} !important; font-size: 0.88rem !important; }}
.stAlert {{ background: {T['bg_card']} !important; border: 1px solid {T['border_strong']} !important; border-radius: 12px !important; color: {T['text_secondary']} !important; }}
.pl-footer {{
    text-align: center;
    font-size: 0.72rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: {T['text_muted']};
    border-top: 1px solid {T['border']};
    margin-top: 4rem;
    padding-top: 1.5rem;
    font-family: 'DM Mono', monospace;
}}
.pl-disclaimer {{
    text-align: center;
    font-size: 0.75rem;
    color: {T['text_muted']};
    padding: 1.25rem;
    border-top: 1px solid {T['border']};
    margin-top: 2rem;
    font-style: italic;
    line-height: 1.6;
}}
</style>
""", unsafe_allow_html=True)


# ============================================================================
# ── ALL PURE FUNCTIONS DEFINED HERE, BEFORE ANY UI OR DATA LOADING ──────────
# ============================================================================

def calc_energy(row):
    """Atwater 4·4·9 energy (kcal per 100g)."""
    try:
        p = float(row['proteins_100g']      or 0)
        c = float(row['carbohydrates_100g'] or 0)
        f = float(row['fat_100g']           or 0)
        return p * 4 + c * 4 + f * 9
    except Exception:
        return 0.0


def hex_to_rgba(hex_color, alpha=0.12):
    try:
        h = hex_color.lstrip('#')
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return f"rgba({r},{g},{b},{alpha})"
    except Exception:
        return f"rgba(201,168,76,{alpha})"


def macro_bar_html(label, val, max_val, color):
    try:
        val     = float(val     or 0)
        max_val = float(max_val or 1)
    except Exception:
        val, max_val = 0.0, 1.0
    pct = min(int(val / max_val * 100), 100)
    return (
        f'<div class="mb-wrap">'
        f'<div class="mb-top"><span>{label}</span>'
        f'<span>{val:.1f}g &nbsp;·&nbsp; {pct}%</span></div>'
        f'<div class="mb-track"><div class="mb-fill" style="width:{pct}%;background:{color};"></div></div>'
        f'</div>'
    )


def fsa_color(nutrient, value):
    thresholds = {
        "fat":    (3.0, 17.5),
        "sugar":  (5.0, 22.5),
        "salt":   (0.3,  1.5),
        "fiber":  (3.0,  6.0),
        "protein":(10.0, 20.0),
    }
    lo, hi = thresholds.get(nutrient, (None, None))
    if lo is None:
        return T['accent']
    try:
        value = float(value or 0)
    except Exception:
        value = 0.0
    if nutrient in ("fiber", "protein"):
        return T['green'] if value >= hi else (T['yellow'] if value >= lo else T['red'])
    return T['green'] if value <= lo else (T['yellow'] if value <= hi else T['red'])


def nutrition_score(row):
    """Return (score 0-100, label str, color hex)."""
    try:
        pro = float(row['proteins_100g']      or 0)
        fib = float(row['fiber_100g']         or 0)
        sug = float(row['sugars_100g']        or 0)
        fat = float(row['fat_100g']           or 0)
        slt = float(row['salt_100g']          or 0)
    except Exception:
        pro = fib = sug = fat = slt = 0.0

    score = 50
    if pro >= 20:   score += 15
    elif pro >= 12: score += 8
    if fib >= 6:    score += 15
    elif fib >= 3:  score += 7
    if sug > 22.5:  score -= 20
    elif sug > 12:  score -= 10
    if fat > 17.5:  score -= 10
    if slt > 1.5:   score -= 15
    elif slt > 0.6: score -= 7
    score = max(0, min(100, score))

    if score >= 70: return score, "EXCELLENT", T['green']
    if score >= 55: return score, "GOOD",      T['blue']
    if score >= 40: return score, "MODERATE",  T['yellow']
    return score, "CAUTION", T['red']


def nutrient_notes(row):
    notes = []
    cal       = calc_energy(row)
    cal_label = float(row.get('energy_100g', 0) or 0)
    delta     = abs(cal - cal_label) / cal_label * 100 if cal_label else 0

    try:
        sug = float(row['sugars_100g']   or 0)
        fat = float(row['fat_100g']      or 0)
        fib = float(row['fiber_100g']    or 0)
        slt = float(row['salt_100g']     or 0)
        pro = float(row['proteins_100g'] or 0)
    except Exception:
        sug = fat = fib = slt = pro = 0.0

    if sug > 22.5:
        notes.append(("⚠ High Sugar",
                       f"{sug:.1f}g/100g exceeds the UK FSA high-sugar threshold (22.5g).",
                       "pl-card-red"))
    elif sug <= 5:
        notes.append(("✓ Low Sugar",
                       f"{sug:.1f}g/100g — below the low-sugar threshold (5g).",
                       "pl-card-green"))

    if fat > 17.5:
        notes.append(("⚠ High Fat",
                       f"Total fat {fat:.1f}g/100g exceeds FSA high threshold (17.5g).",
                       "pl-card-red"))
    elif fat <= 3:
        notes.append(("✓ Low Fat",
                       f"Total fat {fat:.1f}g/100g — below the low-fat threshold (3g).",
                       "pl-card-green"))

    if fib >= 6:
        notes.append(("✓ High Fibre",
                       f"{fib:.1f}g/100g — qualifies as high-fibre (EU Reg. 1924/2006, ≥6g).",
                       "pl-card-green"))

    if slt > 1.5:
        notes.append(("⚠ High Salt",
                       f"{slt:.2f}g/100g exceeds FSA high threshold (1.5g). WHO recommends <5g/day total.",
                       "pl-card-red"))
    elif slt <= 0.3:
        notes.append(("✓ Low Salt",
                       f"{slt:.2f}g/100g — below the low-salt threshold (0.3g).",
                       "pl-card-green"))

    if pro >= 20:
        notes.append(("✓ High Protein",
                       f"{pro:.1f}g/100g qualifies as a high-protein source (EU Reg. 1924/2006, ≥20g).",
                       "pl-card-green"))
    elif pro >= 12:
        notes.append(("↑ Source of Protein",
                       f"{pro:.1f}g/100g qualifies as a 'source of protein' (≥12g/100g).",
                       "pl-card-blue"))

    if delta > 10:
        notes.append(("ℹ Label Variance",
                       f"Calculated energy ({cal:.0f} kcal) differs from label ({cal_label:.0f} kcal) "
                       f"by {delta:.1f}%. May reflect rounding or fatty-acid composition.",
                       "pl-card-yellow"))

    if not notes:
        notes.append(("✓ Within All Thresholds",
                       "This product does not exceed any standard FSA nutrient thresholds.",
                       "pl-card-green"))
    return notes


# Smart-filter predicates — defined here so they can reference calc_energy safely
SMART_FILTERS = {
    "All":            lambda r: True,
    "🥩 High Protein": lambda r: float(r['proteins_100g']      or 0) >= 15,
    "🌾 High Fibre":   lambda r: float(r['fiber_100g']         or 0) >= 5,
    "🍬 Low Sugar":    lambda r: float(r['sugars_100g']        or 0) <= 5,
    "🧈 Low Fat":      lambda r: float(r['fat_100g']           or 0) <= 5,
    "🔥 High Calorie": lambda r: calc_energy(r) >= 400,
    "🥗 Low Calorie":  lambda r: calc_energy(r) <= 120,
    "🧂 Low Salt":     lambda r: float(r['salt_100g']          or 0) <= 0.3,
}


# ============================================================================
# DATA LOADING
# ============================================================================

# French-to-English word map (applied to product names from OFf that aren't English)
_FR_EN = {
    "lait":"milk","beurre":"butter","fromage":"cheese","yaourt":"yogurt",
    "yaourts":"yogurts","pain":"bread","farine":"flour","sucre":"sugar",
    "sel":"salt","huile":"oil","viande":"meat","poulet":"chicken",
    "boeuf":"beef","porc":"pork","poisson":"fish","oeuf":"egg","oeufs":"eggs",
    "legumes":"vegetables","fruits":"fruits","jus":"juice","eau":"water",
    "cafe":"coffee","the":"tea","vin":"wine","biere":"beer",
    "chocolat":"chocolate","carottes":"carrots","tomates":"tomatoes",
    "pommes":"apples","fraises":"strawberries","riz":"rice","pates":"pasta",
    "soupe":"soup","confiture":"jam","miel":"honey","creme":"cream",
    "lentilles":"lentils","haricots":"beans","petits pois":"peas",
    "epinards":"spinach","brocoli":"broccoli","avocat":"avocado",
    "noix":"walnuts","amandes":"almonds","noisettes":"hazelnuts",
    "saucisse":"sausage","jambon":"ham","saumon":"salmon","thon":"tuna",
    "sardines":"sardines","crevettes":"shrimp","frites":"fries",
    "chips":"chips","biscuits":"biscuits","gateaux":"cakes","cereales":"cereals",
    "flocons d'avoine":"oat flakes","poudre de cacao":"cocoa powder",
    "extrait de vanille":"vanilla extract","huile d'olive":"olive oil",
    "huile de tournesol":"sunflower oil","lait entier":"whole milk",
    "lait demi-ecreme":"semi-skimmed milk","beurre doux":"unsalted butter",
    "pain complet":"wholegrain bread","pain de mie":"sandwich bread",
    "yaourt nature":"plain yogurt",
}

def _translate_name(name: str) -> str:
    """Apply French→English word substitutions, return title-cased result."""
    s = str(name).lower().strip()
    # Longest matches first
    for fr, en in sorted(_FR_EN.items(), key=lambda x: -len(x[0])):
        s = s.replace(fr, en)
    return s.title()

def _is_mostly_ascii(text: str, threshold=0.85) -> bool:
    if not text or len(text) < 2:
        return False
    ascii_chars = sum(1 for c in text if ord(c) < 128)
    return ascii_chars / len(text) >= threshold

def _safe_float(v, lo=0.0, hi=9999.0, default=0.0):
    try:
        f = float(v)
        return f if lo <= f <= hi else default
    except Exception:
        return default

_CAT_KEYWORDS = {
    "Nuts & Seeds":    ["almond","cashew","walnut","pistachio","pecan","hazelnut",
                        "macadamia","peanut","chia","flax","hemp","pumpkin seed",
                        "sunflower seed","sesame","pine nut","brazil nut"],
    "Dairy & Eggs":    ["milk","cheese","yogurt","yoghurt","butter","cream","egg",
                        "whey","cheddar","mozzarella","brie","gouda","parmesan",
                        "skimmed","kefir","quark","cottage","ricotta","ghee","skyr"],
    "Grains & Legumes":["oat","wheat","rice","bread","pasta","noodle","barley",
                        "rye","corn","maize","quinoa","chickpea","lentil","bean",
                        "pea","soy","flour","cereal","muesli","granola","tortilla",
                        "couscous","farro","bulgur","spelt","millet","buckwheat"],
    "Proteins":        ["chicken","beef","pork","lamb","turkey","salmon","tuna",
                        "cod","shrimp","prawn","sardine","mackerel","herring",
                        "tofu","tempeh","seitan","protein powder","sausage",
                        "bacon","ham","venison","duck","tilapia","trout","crab"],
    "Fruits & Veg":    ["apple","banana","orange","mango","berry","strawberry",
                        "blueberry","raspberry","grape","peach","pear","cherry",
                        "watermelon","melon","pineapple","kiwi","lemon","lime",
                        "avocado","tomato","potato","carrot","broccoli","spinach",
                        "kale","lettuce","cucumber","pepper","onion","garlic",
                        "mushroom","zucchini","courgette","eggplant","cauliflower",
                        "asparagus","celery","beetroot","sweet potato","pumpkin"],
    "Sweets & Snacks": ["chocolate","biscuit","cookie","cake","candy","sweet",
                        "chips","crisp","wafer","brownie","muffin","donut",
                        "lollipop","jelly","gummy","toffee","caramel","popcorn",
                        "pretzel","ice cream","gelato","bar","fudge","pudding",
                        "custard","tart","pastry"],
    "Oils & Condiments":["olive oil","vegetable oil","coconut oil","sunflower oil",
                         "rapeseed","ketchup","mustard","mayonnaise","sauce",
                         "vinegar","soy sauce","hummus","pesto","jam","marmalade",
                         "honey","syrup","dressing","spread","margarine","tahini",
                         "miso","relish","chutney","salsa"],
    "Beverages":       ["juice","smoothie","coffee","tea","water","soda","cola",
                        "lemonade","energy drink","sports drink","shake","cocoa",
                        "kombucha","beer","wine","cider","milk drink"],
    "Prepared & Ready":["soup","stew","curry","pizza","burger","sandwich","wrap",
                        "salad","ready meal","frozen","lasagna","casserole",
                        "stir fry","instant","canned","preserved","pot noodle"],
}

def _assign_category(name: str, ingredients: str) -> str:
    text = (str(name) + " " + str(ingredients)).lower()
    best_cat, best_score = "Other", 0
    for cat, kws in _CAT_KEYWORDS.items():
        score = sum(1 for kw in kws if kw in text)
        if score > best_score:
            best_score, best_cat = score, cat
    return best_cat


@st.cache_data(show_spinner="Loading database…")
def load_data():
    """
    Try to load Open Food Facts CSV.  Fall back to built-in 200-product set.
    Returns (DataFrame, loaded_from_csv: bool)
    """
    # ── Locations to probe for the Kaggle CSV ────────────────────────────────
    candidates = [
        "en.openfoodfacts.org.products.csv",
        "en.openfoodfacts.org.products.tsv",
        "open-food-facts-initial-filter.csv",
        "cleaned_food_data.csv",
        os.path.join(os.path.dirname(__file__), "en.openfoodfacts.org.products.csv"),
    ]

    needed = ['product_name','ingredients_text','energy_100g','proteins_100g',
              'fat_100g','carbohydrates_100g','sugars_100g','fiber_100g','salt_100g']

    for path in candidates:
        if not os.path.exists(path):
            continue
        try:
            # Read in chunks; stop after we have enough rows
            sep = '\t' if path.endswith('.tsv') or 'openfoodfacts' in path else None
            chunks = []
            reader = pd.read_csv(
                path,
                sep=sep if sep else '\t',   # OFF files are TSV
                encoding='utf-8',
                low_memory=False,
                usecols=lambda c: c in needed or c in
                        ['main_category_en','pnns_groups_1','categories_en','countries_en'],
                on_bad_lines='skip',
                chunksize=100_000,
            )
            for chunk in reader:
                chunks.append(chunk)
                if sum(len(c) for c in chunks) >= 1_500_000:
                    break

            if not chunks:
                continue

            raw = pd.concat(chunks, ignore_index=True)

            # ── Keep only rows with a product name ───────────────────────────
            raw = raw.dropna(subset=['product_name'])
            raw['product_name'] = raw['product_name'].astype(str).str.strip()
            raw = raw[raw['product_name'].str.len() >= 2]

            # ── Numeric columns ───────────────────────────────────────────────
            num_cols = ['energy_100g','proteins_100g','fat_100g',
                        'carbohydrates_100g','sugars_100g','fiber_100g','salt_100g']
            for col in num_cols:
                if col not in raw.columns:
                    raw[col] = 0.0
                raw[col] = pd.to_numeric(raw[col], errors='coerce').fillna(0.0).clip(0, 9999)

            raw['ingredients_text'] = raw.get('ingredients_text', pd.Series('', index=raw.index)).fillna('')

            # ── English / translatable name filter ────────────────────────────
            def make_display_name(name):
                name = str(name).strip()
                if _is_mostly_ascii(name):
                    # Already English-ish — title-case if all lower
                    return name.title() if name == name.lower() else name
                # Try translating from French
                translated = _translate_name(name)
                if _is_mostly_ascii(translated):
                    return translated
                # Still non-ASCII — skip
                return None

            raw['display_name'] = raw['product_name'].apply(make_display_name)
            raw = raw.dropna(subset=['display_name'])
            raw = raw[raw['display_name'].str.len() >= 3]

            # ── De-duplicate ─────────────────────────────────────────────────
            raw = raw.drop_duplicates(subset=['display_name'])

            # ── Category ─────────────────────────────────────────────────────
            cat_src = next(
                (raw[c].fillna('') for c in ['main_category_en','pnns_groups_1','categories_en']
                 if c in raw.columns and raw[c].notna().any()),
                pd.Series('', index=raw.index)
            )
            raw['category'] = cat_src.apply(
                lambda c: c.split(',')[0].strip().title() if isinstance(c, str) and c.strip() else ''
            )
            # Re-assign blank or unmapped categories via keyword
            valid_cats = set(_CAT_KEYWORDS.keys())
            def final_cat(row2):
                c = row2['category']
                if c and c in valid_cats:
                    return c
                return _assign_category(row2['display_name'], row2['ingredients_text'])
            raw['category'] = raw.apply(final_cat, axis=1)

            out_cols = ['display_name','category','energy_100g','proteins_100g',
                        'fat_100g','carbohydrates_100g','sugars_100g','fiber_100g',
                        'salt_100g','ingredients_text']
            out = raw[out_cols].reset_index(drop=True)

            if len(out) > 50:
                return out, True

        except Exception:
            continue   # try next path

    # ── Built-in database (200+ products, English only) ──────────────────────
    records = [
        # Nuts & Seeds
        {"category":"Nuts & Seeds","display_name":"Organic Almonds","energy_100g":579,"proteins_100g":21.2,"fat_100g":49.9,"carbohydrates_100g":21.6,"sugars_100g":4.4,"fiber_100g":12.5,"salt_100g":0.00,"ingredients_text":"Organic almonds."},
        {"category":"Nuts & Seeds","display_name":"Raw Cashews","energy_100g":553,"proteins_100g":18.2,"fat_100g":43.9,"carbohydrates_100g":30.2,"sugars_100g":5.9,"fiber_100g":3.3,"salt_100g":0.01,"ingredients_text":"Raw cashew nuts."},
        {"category":"Nuts & Seeds","display_name":"Walnuts","energy_100g":654,"proteins_100g":15.2,"fat_100g":65.2,"carbohydrates_100g":13.7,"sugars_100g":2.6,"fiber_100g":6.7,"salt_100g":0.00,"ingredients_text":"Walnuts."},
        {"category":"Nuts & Seeds","display_name":"Chia Seeds","energy_100g":486,"proteins_100g":16.5,"fat_100g":30.7,"carbohydrates_100g":42.1,"sugars_100g":0.0,"fiber_100g":34.4,"salt_100g":0.02,"ingredients_text":"Chia seeds (Salvia hispanica)."},
        {"category":"Nuts & Seeds","display_name":"Ground Flaxseeds","energy_100g":534,"proteins_100g":18.3,"fat_100g":42.2,"carbohydrates_100g":28.9,"sugars_100g":1.6,"fiber_100g":27.3,"salt_100g":0.03,"ingredients_text":"Ground golden flaxseeds."},
        {"category":"Nuts & Seeds","display_name":"Pumpkin Seeds","energy_100g":559,"proteins_100g":30.2,"fat_100g":49.1,"carbohydrates_100g":10.7,"sugars_100g":1.4,"fiber_100g":6.0,"salt_100g":0.01,"ingredients_text":"Raw pumpkin seeds."},
        {"category":"Nuts & Seeds","display_name":"Sunflower Seeds","energy_100g":584,"proteins_100g":20.8,"fat_100g":51.5,"carbohydrates_100g":20.0,"sugars_100g":2.6,"fiber_100g":8.6,"salt_100g":0.00,"ingredients_text":"Sunflower seeds."},
        {"category":"Nuts & Seeds","display_name":"Hemp Seeds Hulled","energy_100g":553,"proteins_100g":31.6,"fat_100g":48.7,"carbohydrates_100g":8.7,"sugars_100g":1.5,"fiber_100g":4.0,"salt_100g":0.00,"ingredients_text":"Hulled hemp seeds."},
        {"category":"Nuts & Seeds","display_name":"Roasted Pistachios","energy_100g":562,"proteins_100g":20.2,"fat_100g":45.3,"carbohydrates_100g":27.5,"sugars_100g":7.7,"fiber_100g":10.3,"salt_100g":0.01,"ingredients_text":"Dry roasted pistachios."},
        {"category":"Nuts & Seeds","display_name":"Brazil Nuts","energy_100g":656,"proteins_100g":14.3,"fat_100g":66.4,"carbohydrates_100g":11.7,"sugars_100g":2.3,"fiber_100g":7.5,"salt_100g":0.00,"ingredients_text":"Brazil nuts."},
        {"category":"Nuts & Seeds","display_name":"Hazelnuts","energy_100g":628,"proteins_100g":15.0,"fat_100g":60.8,"carbohydrates_100g":16.7,"sugars_100g":4.3,"fiber_100g":9.7,"salt_100g":0.00,"ingredients_text":"Whole hazelnuts."},
        {"category":"Nuts & Seeds","display_name":"Macadamia Nuts","energy_100g":718,"proteins_100g":7.9,"fat_100g":75.8,"carbohydrates_100g":13.8,"sugars_100g":4.6,"fiber_100g":8.6,"salt_100g":0.00,"ingredients_text":"Macadamia nuts."},
        {"category":"Nuts & Seeds","display_name":"Pecan Nuts","energy_100g":691,"proteins_100g":9.2,"fat_100g":72.0,"carbohydrates_100g":13.9,"sugars_100g":3.8,"fiber_100g":9.6,"salt_100g":0.00,"ingredients_text":"Pecan nuts."},
        {"category":"Nuts & Seeds","display_name":"Pine Nuts","energy_100g":673,"proteins_100g":13.7,"fat_100g":68.4,"carbohydrates_100g":13.1,"sugars_100g":3.6,"fiber_100g":3.7,"salt_100g":0.00,"ingredients_text":"Pine nuts."},
        {"category":"Nuts & Seeds","display_name":"Sesame Seeds","energy_100g":573,"proteins_100g":17.7,"fat_100g":49.7,"carbohydrates_100g":23.5,"sugars_100g":0.3,"fiber_100g":11.8,"salt_100g":0.02,"ingredients_text":"Sesame seeds."},
        {"category":"Nuts & Seeds","display_name":"Unsalted Mixed Nuts","energy_100g":607,"proteins_100g":15.9,"fat_100g":55.3,"carbohydrates_100g":21.8,"sugars_100g":4.8,"fiber_100g":7.0,"salt_100g":0.00,"ingredients_text":"Almonds, cashews, walnuts, brazil nuts, hazelnuts."},
        {"category":"Nuts & Seeds","display_name":"Salted Peanuts","energy_100g":585,"proteins_100g":25.8,"fat_100g":49.5,"carbohydrates_100g":16.1,"sugars_100g":4.0,"fiber_100g":8.5,"salt_100g":1.10,"ingredients_text":"Peanuts, salt."},
        {"category":"Nuts & Seeds","display_name":"Almond Flour","energy_100g":571,"proteins_100g":21.4,"fat_100g":50.6,"carbohydrates_100g":19.1,"sugars_100g":3.7,"fiber_100g":10.7,"salt_100g":0.00,"ingredients_text":"Blanched ground almonds."},
        # Dairy & Eggs
        {"category":"Dairy & Eggs","display_name":"Greek Yogurt 0% Fat","energy_100g":59,"proteins_100g":10.0,"fat_100g":0.4,"carbohydrates_100g":3.6,"sugars_100g":3.2,"fiber_100g":0.0,"salt_100g":0.10,"ingredients_text":"Pasteurised skimmed milk, live active cultures."},
        {"category":"Dairy & Eggs","display_name":"Full Fat Cottage Cheese","energy_100g":98,"proteins_100g":11.1,"fat_100g":4.5,"carbohydrates_100g":3.4,"sugars_100g":2.7,"fiber_100g":0.0,"salt_100g":0.73,"ingredients_text":"Pasteurised whole milk, cream, salt, cultures."},
        {"category":"Dairy & Eggs","display_name":"Free Range Whole Eggs","energy_100g":143,"proteins_100g":12.6,"fat_100g":9.5,"carbohydrates_100g":0.7,"sugars_100g":0.4,"fiber_100g":0.0,"salt_100g":0.37,"ingredients_text":"Free-range whole eggs."},
        {"category":"Dairy & Eggs","display_name":"Grated Parmesan","energy_100g":431,"proteins_100g":38.5,"fat_100g":29.0,"carbohydrates_100g":3.2,"sugars_100g":0.0,"fiber_100g":0.0,"salt_100g":1.84,"ingredients_text":"Pasteurised cow milk, salt, rennet."},
        {"category":"Dairy & Eggs","display_name":"Whole Milk 3.5%","energy_100g":61,"proteins_100g":3.2,"fat_100g":3.5,"carbohydrates_100g":4.8,"sugars_100g":4.8,"fiber_100g":0.0,"salt_100g":0.10,"ingredients_text":"Whole pasteurised milk."},
        {"category":"Dairy & Eggs","display_name":"Semi Skimmed Milk 1.5%","energy_100g":46,"proteins_100g":3.3,"fat_100g":1.5,"carbohydrates_100g":5.0,"sugars_100g":5.0,"fiber_100g":0.0,"salt_100g":0.10,"ingredients_text":"Semi-skimmed pasteurised milk."},
        {"category":"Dairy & Eggs","display_name":"Skimmed Milk 0%","energy_100g":34,"proteins_100g":3.4,"fat_100g":0.1,"carbohydrates_100g":5.0,"sugars_100g":5.0,"fiber_100g":0.0,"salt_100g":0.11,"ingredients_text":"Skimmed pasteurised milk."},
        {"category":"Dairy & Eggs","display_name":"Cheddar Cheese","energy_100g":403,"proteins_100g":25.0,"fat_100g":33.1,"carbohydrates_100g":0.1,"sugars_100g":0.1,"fiber_100g":0.0,"salt_100g":1.74,"ingredients_text":"Pasteurised cow milk, starter culture, salt, rennet."},
        {"category":"Dairy & Eggs","display_name":"Fresh Mozzarella","energy_100g":280,"proteins_100g":19.9,"fat_100g":22.4,"carbohydrates_100g":2.2,"sugars_100g":0.5,"fiber_100g":0.0,"salt_100g":0.58,"ingredients_text":"Pasteurised cow milk, lactic starter, salt, rennet."},
        {"category":"Dairy & Eggs","display_name":"Brie Cheese","energy_100g":334,"proteins_100g":20.0,"fat_100g":27.7,"carbohydrates_100g":0.5,"sugars_100g":0.5,"fiber_100g":0.0,"salt_100g":1.65,"ingredients_text":"Cow milk, cream, salt, rennet, cultures."},
        {"category":"Dairy & Eggs","display_name":"Gouda Cheese","energy_100g":356,"proteins_100g":25.0,"fat_100g":27.4,"carbohydrates_100g":2.2,"sugars_100g":0.0,"fiber_100g":0.0,"salt_100g":1.70,"ingredients_text":"Cow milk, salt, rennet, cultures."},
        {"category":"Dairy & Eggs","display_name":"Full Fat Cream Cheese","energy_100g":342,"proteins_100g":6.2,"fat_100g":34.1,"carbohydrates_100g":3.4,"sugars_100g":2.7,"fiber_100g":0.0,"salt_100g":0.79,"ingredients_text":"Cream, skimmed milk, salt, cultures."},
        {"category":"Dairy & Eggs","display_name":"Unsalted Butter","energy_100g":717,"proteins_100g":0.9,"fat_100g":81.1,"carbohydrates_100g":0.1,"sugars_100g":0.1,"fiber_100g":0.0,"salt_100g":0.02,"ingredients_text":"Pasteurised cream."},
        {"category":"Dairy & Eggs","display_name":"Sour Cream 18%","energy_100g":195,"proteins_100g":2.7,"fat_100g":19.9,"carbohydrates_100g":3.4,"sugars_100g":3.4,"fiber_100g":0.0,"salt_100g":0.08,"ingredients_text":"Cream, lactic cultures."},
        {"category":"Dairy & Eggs","display_name":"Full Fat Greek Yogurt","energy_100g":133,"proteins_100g":5.7,"fat_100g":10.0,"carbohydrates_100g":4.7,"sugars_100g":4.7,"fiber_100g":0.0,"salt_100g":0.11,"ingredients_text":"Whole milk, live cultures."},
        {"category":"Dairy & Eggs","display_name":"Ricotta Cheese","energy_100g":174,"proteins_100g":11.3,"fat_100g":13.0,"carbohydrates_100g":3.0,"sugars_100g":0.3,"fiber_100g":0.0,"salt_100g":0.40,"ingredients_text":"Whey, milk, salt."},
        {"category":"Dairy & Eggs","display_name":"Skyr Icelandic Yogurt","energy_100g":63,"proteins_100g":11.0,"fat_100g":0.2,"carbohydrates_100g":4.0,"sugars_100g":4.0,"fiber_100g":0.0,"salt_100g":0.07,"ingredients_text":"Skimmed milk, active cultures."},
        {"category":"Dairy & Eggs","display_name":"Whey Protein Concentrate","energy_100g":373,"proteins_100g":78.0,"fat_100g":4.5,"carbohydrates_100g":9.0,"sugars_100g":6.5,"fiber_100g":0.5,"salt_100g":0.40,"ingredients_text":"Whey protein concentrate, soy lecithin."},
        # Grains & Legumes
        {"category":"Grains & Legumes","display_name":"Rolled Oats","energy_100g":389,"proteins_100g":16.9,"fat_100g":6.9,"carbohydrates_100g":66.3,"sugars_100g":1.0,"fiber_100g":10.6,"salt_100g":0.00,"ingredients_text":"Whole grain rolled oats."},
        {"category":"Grains & Legumes","display_name":"Cooked Quinoa","energy_100g":120,"proteins_100g":4.4,"fat_100g":1.9,"carbohydrates_100g":21.3,"sugars_100g":0.9,"fiber_100g":2.8,"salt_100g":0.01,"ingredients_text":"Quinoa, water."},
        {"category":"Grains & Legumes","display_name":"Cooked Chickpeas","energy_100g":164,"proteins_100g":8.9,"fat_100g":2.6,"carbohydrates_100g":27.4,"sugars_100g":4.8,"fiber_100g":7.6,"salt_100g":0.24,"ingredients_text":"Chickpeas, water, salt."},
        {"category":"Grains & Legumes","display_name":"Cooked Red Lentils","energy_100g":116,"proteins_100g":9.0,"fat_100g":0.4,"carbohydrates_100g":20.1,"sugars_100g":1.8,"fiber_100g":7.9,"salt_100g":0.01,"ingredients_text":"Red lentils, water."},
        {"category":"Grains & Legumes","display_name":"Cooked Brown Rice","energy_100g":111,"proteins_100g":2.6,"fat_100g":0.9,"carbohydrates_100g":23.0,"sugars_100g":0.3,"fiber_100g":1.8,"salt_100g":0.00,"ingredients_text":"Whole grain brown rice, water."},
        {"category":"Grains & Legumes","display_name":"Sourdough Bread","energy_100g":259,"proteins_100g":8.8,"fat_100g":1.2,"carbohydrates_100g":50.5,"sugars_100g":2.3,"fiber_100g":5.4,"salt_100g":0.98,"ingredients_text":"Whole wheat flour, water, salt, sourdough starter."},
        {"category":"Grains & Legumes","display_name":"Wholemeal Bread","energy_100g":247,"proteins_100g":9.4,"fat_100g":2.1,"carbohydrates_100g":44.0,"sugars_100g":4.5,"fiber_100g":7.4,"salt_100g":1.00,"ingredients_text":"Wholemeal wheat flour, water, yeast, salt."},
        {"category":"Grains & Legumes","display_name":"White Bread","energy_100g":265,"proteins_100g":8.0,"fat_100g":2.9,"carbohydrates_100g":49.0,"sugars_100g":5.2,"fiber_100g":2.7,"salt_100g":1.00,"ingredients_text":"Wheat flour, water, yeast, salt, sugar."},
        {"category":"Grains & Legumes","display_name":"Dry Spaghetti","energy_100g":371,"proteins_100g":13.0,"fat_100g":1.5,"carbohydrates_100g":74.7,"sugars_100g":3.4,"fiber_100g":3.2,"salt_100g":0.00,"ingredients_text":"Durum wheat semolina."},
        {"category":"Grains & Legumes","display_name":"Wholemeal Pasta Dry","energy_100g":352,"proteins_100g":13.4,"fat_100g":2.5,"carbohydrates_100g":67.0,"sugars_100g":2.7,"fiber_100g":8.1,"salt_100g":0.00,"ingredients_text":"Whole wheat semolina."},
        {"category":"Grains & Legumes","display_name":"Basmati Rice Dry","energy_100g":356,"proteins_100g":7.4,"fat_100g":0.7,"carbohydrates_100g":80.0,"sugars_100g":0.2,"fiber_100g":1.4,"salt_100g":0.00,"ingredients_text":"Long grain basmati rice."},
        {"category":"Grains & Legumes","display_name":"Cooked Black Beans","energy_100g":132,"proteins_100g":8.9,"fat_100g":0.5,"carbohydrates_100g":23.7,"sugars_100g":0.3,"fiber_100g":8.7,"salt_100g":0.00,"ingredients_text":"Black beans, water."},
        {"category":"Grains & Legumes","display_name":"Kidney Beans Canned","energy_100g":127,"proteins_100g":8.7,"fat_100g":0.5,"carbohydrates_100g":22.8,"sugars_100g":0.3,"fiber_100g":7.4,"salt_100g":0.60,"ingredients_text":"Kidney beans, water, salt."},
        {"category":"Grains & Legumes","display_name":"Edamame Beans","energy_100g":122,"proteins_100g":11.9,"fat_100g":5.2,"carbohydrates_100g":8.9,"sugars_100g":2.2,"fiber_100g":5.2,"salt_100g":0.00,"ingredients_text":"Edamame soy beans."},
        {"category":"Grains & Legumes","display_name":"Steel Cut Oats","energy_100g":380,"proteins_100g":14.0,"fat_100g":6.9,"carbohydrates_100g":67.7,"sugars_100g":0.5,"fiber_100g":11.0,"salt_100g":0.00,"ingredients_text":"Whole grain steel cut oats."},
        {"category":"Grains & Legumes","display_name":"Corn Tortilla","energy_100g":218,"proteins_100g":5.7,"fat_100g":3.0,"carbohydrates_100g":45.9,"sugars_100g":0.7,"fiber_100g":6.7,"salt_100g":0.90,"ingredients_text":"Whole grain corn masa flour, water, salt."},
        {"category":"Grains & Legumes","display_name":"Rye Bread","energy_100g":259,"proteins_100g":8.5,"fat_100g":3.3,"carbohydrates_100g":48.0,"sugars_100g":3.8,"fiber_100g":5.8,"salt_100g":1.30,"ingredients_text":"Rye flour, water, yeast, salt."},
        {"category":"Grains & Legumes","display_name":"Buckwheat Groats","energy_100g":343,"proteins_100g":13.3,"fat_100g":3.4,"carbohydrates_100g":71.5,"sugars_100g":0.0,"fiber_100g":10.0,"salt_100g":0.00,"ingredients_text":"Whole buckwheat groats."},
        {"category":"Grains & Legumes","display_name":"Cooked Couscous","energy_100g":112,"proteins_100g":3.8,"fat_100g":0.2,"carbohydrates_100g":23.2,"sugars_100g":0.1,"fiber_100g":1.4,"salt_100g":0.00,"ingredients_text":"Durum wheat semolina, water."},
        {"category":"Grains & Legumes","display_name":"Plain Rice Cakes","energy_100g":387,"proteins_100g":7.5,"fat_100g":2.8,"carbohydrates_100g":81.5,"sugars_100g":0.3,"fiber_100g":1.2,"salt_100g":0.60,"ingredients_text":"Whole grain rice, salt."},
        # Proteins
        {"category":"Proteins","display_name":"Atlantic Salmon Raw","energy_100g":208,"proteins_100g":20.4,"fat_100g":13.4,"carbohydrates_100g":0.0,"sugars_100g":0.0,"fiber_100g":0.0,"salt_100g":0.06,"ingredients_text":"Atlantic salmon (Salmo salar)."},
        {"category":"Proteins","display_name":"Chicken Breast Raw","energy_100g":120,"proteins_100g":22.5,"fat_100g":2.6,"carbohydrates_100g":0.0,"sugars_100g":0.0,"fiber_100g":0.0,"salt_100g":0.08,"ingredients_text":"Free-range chicken breast."},
        {"category":"Proteins","display_name":"Canned Tuna In Water","energy_100g":103,"proteins_100g":22.9,"fat_100g":1.0,"carbohydrates_100g":0.0,"sugars_100g":0.0,"fiber_100g":0.0,"salt_100g":0.55,"ingredients_text":"Skipjack tuna, spring water, salt."},
        {"category":"Proteins","display_name":"Lean Beef Mince 5% Fat","energy_100g":137,"proteins_100g":20.8,"fat_100g":5.0,"carbohydrates_100g":0.0,"sugars_100g":0.0,"fiber_100g":0.0,"salt_100g":0.07,"ingredients_text":"Lean beef (95% lean)."},
        {"category":"Proteins","display_name":"Firm Tofu","energy_100g":76,"proteins_100g":8.1,"fat_100g":4.2,"carbohydrates_100g":1.9,"sugars_100g":0.5,"fiber_100g":0.3,"salt_100g":0.02,"ingredients_text":"Water, soybean curds, calcium sulfate."},
        {"category":"Proteins","display_name":"Turkey Breast Skinless","energy_100g":135,"proteins_100g":29.9,"fat_100g":1.6,"carbohydrates_100g":0.0,"sugars_100g":0.0,"fiber_100g":0.0,"salt_100g":0.09,"ingredients_text":"Turkey breast, skinless."},
        {"category":"Proteins","display_name":"Cod Fillet Raw","energy_100g":82,"proteins_100g":17.8,"fat_100g":0.7,"carbohydrates_100g":0.0,"sugars_100g":0.0,"fiber_100g":0.0,"salt_100g":0.26,"ingredients_text":"Atlantic cod (Gadus morhua)."},
        {"category":"Proteins","display_name":"Lean Pork Loin","energy_100g":121,"proteins_100g":21.4,"fat_100g":3.7,"carbohydrates_100g":0.0,"sugars_100g":0.0,"fiber_100g":0.0,"salt_100g":0.08,"ingredients_text":"Lean pork loin."},
        {"category":"Proteins","display_name":"Smoked Mackerel","energy_100g":305,"proteins_100g":18.9,"fat_100g":25.1,"carbohydrates_100g":0.0,"sugars_100g":0.0,"fiber_100g":0.0,"salt_100g":1.35,"ingredients_text":"Mackerel, salt, smoke."},
        {"category":"Proteins","display_name":"Sardines In Tomato Sauce","energy_100g":159,"proteins_100g":17.4,"fat_100g":9.0,"carbohydrates_100g":1.5,"sugars_100g":1.2,"fiber_100g":0.0,"salt_100g":0.98,"ingredients_text":"Sardines, tomato sauce, salt."},
        {"category":"Proteins","display_name":"Tempeh","energy_100g":193,"proteins_100g":18.5,"fat_100g":10.8,"carbohydrates_100g":9.4,"sugars_100g":0.0,"fiber_100g":4.7,"salt_100g":0.01,"ingredients_text":"Fermented soybeans."},
        {"category":"Proteins","display_name":"Seitan Wheat Gluten","energy_100g":370,"proteins_100g":75.0,"fat_100g":1.9,"carbohydrates_100g":13.8,"sugars_100g":0.0,"fiber_100g":0.6,"salt_100g":1.30,"ingredients_text":"Vital wheat gluten, water, soy sauce."},
        {"category":"Proteins","display_name":"Cooked King Prawns","energy_100g":99,"proteins_100g":22.6,"fat_100g":0.9,"carbohydrates_100g":0.0,"sugars_100g":0.0,"fiber_100g":0.0,"salt_100g":1.66,"ingredients_text":"Cooked king prawns, salt."},
        {"category":"Proteins","display_name":"Beef Sirloin Steak","energy_100g":222,"proteins_100g":25.0,"fat_100g":13.6,"carbohydrates_100g":0.0,"sugars_100g":0.0,"fiber_100g":0.0,"salt_100g":0.08,"ingredients_text":"Beef sirloin."},
        {"category":"Proteins","display_name":"Rainbow Trout Fillet","energy_100g":149,"proteins_100g":20.8,"fat_100g":6.6,"carbohydrates_100g":0.0,"sugars_100g":0.0,"fiber_100g":0.0,"salt_100g":0.10,"ingredients_text":"Rainbow trout fillet."},
        # Fruits & Veg
        {"category":"Fruits & Veg","display_name":"Avocado","energy_100g":160,"proteins_100g":2.0,"fat_100g":14.7,"carbohydrates_100g":8.5,"sugars_100g":0.7,"fiber_100g":6.7,"salt_100g":0.01,"ingredients_text":"Hass avocado."},
        {"category":"Fruits & Veg","display_name":"Fresh Blueberries","energy_100g":57,"proteins_100g":0.7,"fat_100g":0.3,"carbohydrates_100g":14.5,"sugars_100g":9.9,"fiber_100g":2.4,"salt_100g":0.00,"ingredients_text":"Fresh blueberries."},
        {"category":"Fruits & Veg","display_name":"Raw Broccoli","energy_100g":34,"proteins_100g":2.8,"fat_100g":0.4,"carbohydrates_100g":6.6,"sugars_100g":1.7,"fiber_100g":2.6,"salt_100g":0.04,"ingredients_text":"Fresh broccoli."},
        {"category":"Fruits & Veg","display_name":"Raw Sweet Potato","energy_100g":86,"proteins_100g":1.6,"fat_100g":0.1,"carbohydrates_100g":20.1,"sugars_100g":4.2,"fiber_100g":3.0,"salt_100g":0.07,"ingredients_text":"Sweet potato."},
        {"category":"Fruits & Veg","display_name":"Banana","energy_100g":89,"proteins_100g":1.1,"fat_100g":0.3,"carbohydrates_100g":22.8,"sugars_100g":12.2,"fiber_100g":2.6,"salt_100g":0.00,"ingredients_text":"Fresh banana."},
        {"category":"Fruits & Veg","display_name":"Raw Spinach","energy_100g":23,"proteins_100g":2.9,"fat_100g":0.4,"carbohydrates_100g":3.6,"sugars_100g":0.4,"fiber_100g":2.2,"salt_100g":0.20,"ingredients_text":"Fresh baby spinach."},
        {"category":"Fruits & Veg","display_name":"Fresh Apple","energy_100g":52,"proteins_100g":0.3,"fat_100g":0.2,"carbohydrates_100g":13.8,"sugars_100g":10.4,"fiber_100g":2.4,"salt_100g":0.00,"ingredients_text":"Fresh apple."},
        {"category":"Fruits & Veg","display_name":"Fresh Orange","energy_100g":47,"proteins_100g":0.9,"fat_100g":0.1,"carbohydrates_100g":11.8,"sugars_100g":9.4,"fiber_100g":2.4,"salt_100g":0.00,"ingredients_text":"Fresh orange."},
        {"category":"Fruits & Veg","display_name":"Fresh Strawberries","energy_100g":32,"proteins_100g":0.7,"fat_100g":0.3,"carbohydrates_100g":7.7,"sugars_100g":4.9,"fiber_100g":2.0,"salt_100g":0.00,"ingredients_text":"Fresh strawberries."},
        {"category":"Fruits & Veg","display_name":"Fresh Mango","energy_100g":60,"proteins_100g":0.8,"fat_100g":0.4,"carbohydrates_100g":15.0,"sugars_100g":13.7,"fiber_100g":1.6,"salt_100g":0.00,"ingredients_text":"Fresh mango."},
        {"category":"Fruits & Veg","display_name":"Raw Kale","energy_100g":49,"proteins_100g":4.3,"fat_100g":0.9,"carbohydrates_100g":8.8,"sugars_100g":2.3,"fiber_100g":3.6,"salt_100g":0.10,"ingredients_text":"Fresh kale leaves."},
        {"category":"Fruits & Veg","display_name":"Raw Carrots","energy_100g":41,"proteins_100g":0.9,"fat_100g":0.2,"carbohydrates_100g":9.6,"sugars_100g":4.7,"fiber_100g":2.8,"salt_100g":0.08,"ingredients_text":"Fresh carrots."},
        {"category":"Fruits & Veg","display_name":"Raw Tomatoes","energy_100g":18,"proteins_100g":0.9,"fat_100g":0.2,"carbohydrates_100g":3.9,"sugars_100g":2.6,"fiber_100g":1.2,"salt_100g":0.01,"ingredients_text":"Fresh tomatoes."},
        {"category":"Fruits & Veg","display_name":"Raw Cucumber","energy_100g":16,"proteins_100g":0.7,"fat_100g":0.1,"carbohydrates_100g":3.6,"sugars_100g":1.7,"fiber_100g":0.5,"salt_100g":0.00,"ingredients_text":"Fresh cucumber."},
        {"category":"Fruits & Veg","display_name":"Red Bell Pepper","energy_100g":31,"proteins_100g":1.0,"fat_100g":0.3,"carbohydrates_100g":6.0,"sugars_100g":4.2,"fiber_100g":2.1,"salt_100g":0.00,"ingredients_text":"Fresh red bell pepper."},
        {"category":"Fruits & Veg","display_name":"White Mushrooms","energy_100g":22,"proteins_100g":3.1,"fat_100g":0.3,"carbohydrates_100g":3.3,"sugars_100g":2.0,"fiber_100g":1.0,"salt_100g":0.01,"ingredients_text":"White button mushrooms."},
        {"category":"Fruits & Veg","display_name":"Fresh Pineapple","energy_100g":50,"proteins_100g":0.5,"fat_100g":0.1,"carbohydrates_100g":13.1,"sugars_100g":9.9,"fiber_100g":1.4,"salt_100g":0.00,"ingredients_text":"Fresh pineapple."},
        {"category":"Fruits & Veg","display_name":"Kiwi Fruit","energy_100g":61,"proteins_100g":1.1,"fat_100g":0.5,"carbohydrates_100g":14.7,"sugars_100g":8.9,"fiber_100g":3.0,"salt_100g":0.00,"ingredients_text":"Fresh kiwi fruit."},
        {"category":"Fruits & Veg","display_name":"Raw Cauliflower","energy_100g":25,"proteins_100g":1.9,"fat_100g":0.3,"carbohydrates_100g":5.0,"sugars_100g":1.9,"fiber_100g":2.0,"salt_100g":0.03,"ingredients_text":"Fresh cauliflower florets."},
        {"category":"Fruits & Veg","display_name":"Fresh Asparagus","energy_100g":20,"proteins_100g":2.2,"fat_100g":0.1,"carbohydrates_100g":3.9,"sugars_100g":1.9,"fiber_100g":2.1,"salt_100g":0.00,"ingredients_text":"Fresh asparagus spears."},
        {"category":"Fruits & Veg","display_name":"Frozen Garden Peas","energy_100g":77,"proteins_100g":6.0,"fat_100g":0.4,"carbohydrates_100g":13.5,"sugars_100g":5.9,"fiber_100g":5.5,"salt_100g":0.03,"ingredients_text":"Garden peas."},
        {"category":"Fruits & Veg","display_name":"Cooked Beetroot","energy_100g":44,"proteins_100g":1.7,"fat_100g":0.2,"carbohydrates_100g":9.6,"sugars_100g":7.9,"fiber_100g":2.0,"salt_100g":0.08,"ingredients_text":"Cooked beetroot."},
        {"category":"Fruits & Veg","display_name":"Medjool Dates","energy_100g":282,"proteins_100g":2.5,"fat_100g":0.4,"carbohydrates_100g":75.0,"sugars_100g":66.5,"fiber_100g":6.7,"salt_100g":0.00,"ingredients_text":"Medjool dates."},
        {"category":"Fruits & Veg","display_name":"Dried Apricots","energy_100g":241,"proteins_100g":3.4,"fat_100g":0.5,"carbohydrates_100g":62.6,"sugars_100g":53.4,"fiber_100g":7.3,"salt_100g":0.01,"ingredients_text":"Dried apricots."},
        # Sweets & Snacks
        {"category":"Sweets & Snacks","display_name":"Dark Chocolate 85%","energy_100g":598,"proteins_100g":12.1,"fat_100g":43.3,"carbohydrates_100g":34.0,"sugars_100g":23.0,"fiber_100g":10.9,"salt_100g":0.02,"ingredients_text":"Cocoa mass, cocoa butter, sugar, vanilla extract."},
        {"category":"Sweets & Snacks","display_name":"Milk Chocolate","energy_100g":535,"proteins_100g":7.7,"fat_100g":30.0,"carbohydrates_100g":59.2,"sugars_100g":56.9,"fiber_100g":1.5,"salt_100g":0.19,"ingredients_text":"Sugar, cocoa butter, whole milk powder, cocoa mass, vanilla."},
        {"category":"Sweets & Snacks","display_name":"Honey Oat Granola Bar","energy_100g":418,"proteins_100g":8.2,"fat_100g":15.0,"carbohydrates_100g":64.0,"sugars_100g":28.0,"fiber_100g":4.2,"salt_100g":0.30,"ingredients_text":"Oats, honey, brown sugar, sunflower oil, almonds, salt."},
        {"category":"Sweets & Snacks","display_name":"Salted Caramel Popcorn","energy_100g":459,"proteins_100g":4.2,"fat_100g":18.0,"carbohydrates_100g":72.0,"sugars_100g":35.0,"fiber_100g":4.7,"salt_100g":1.20,"ingredients_text":"Popcorn corn, sugar, butter, salt, caramel flavour."},
        {"category":"Sweets & Snacks","display_name":"Salted Potato Crisps","energy_100g":536,"proteins_100g":6.5,"fat_100g":33.6,"carbohydrates_100g":53.3,"sugars_100g":0.5,"fiber_100g":3.8,"salt_100g":1.40,"ingredients_text":"Potatoes, sunflower oil, salt."},
        {"category":"Sweets & Snacks","display_name":"Digestive Biscuits","energy_100g":471,"proteins_100g":7.4,"fat_100g":20.9,"carbohydrates_100g":63.6,"sugars_100g":16.5,"fiber_100g":3.0,"salt_100g":0.85,"ingredients_text":"Wholemeal wheat flour, vegetable oil, sugar, oatmeal."},
        {"category":"Sweets & Snacks","display_name":"Plain Oat Biscuits","energy_100g":440,"proteins_100g":8.2,"fat_100g":17.4,"carbohydrates_100g":66.7,"sugars_100g":11.3,"fiber_100g":6.2,"salt_100g":0.78,"ingredients_text":"Oat flour, butter, sugar, salt."},
        {"category":"Sweets & Snacks","display_name":"Chocolate Chip Cookies","energy_100g":488,"proteins_100g":5.9,"fat_100g":22.4,"carbohydrates_100g":67.9,"sugars_100g":39.8,"fiber_100g":2.4,"salt_100g":0.59,"ingredients_text":"Wheat flour, sugar, butter, chocolate chips, eggs, vanilla, salt."},
        {"category":"Sweets & Snacks","display_name":"Plain Croissant","energy_100g":406,"proteins_100g":8.2,"fat_100g":21.0,"carbohydrates_100g":47.7,"sugars_100g":9.2,"fiber_100g":2.2,"salt_100g":1.10,"ingredients_text":"Wheat flour, butter, water, sugar, yeast, salt, skimmed milk."},
        {"category":"Sweets & Snacks","display_name":"Fruit Gummies","energy_100g":339,"proteins_100g":6.0,"fat_100g":0.0,"carbohydrates_100g":78.0,"sugars_100g":46.0,"fiber_100g":0.0,"salt_100g":0.10,"ingredients_text":"Glucose syrup, sugar, gelatin, citric acid, fruit juice, colours."},
        # Oils & Condiments
        {"category":"Oils & Condiments","display_name":"Extra Virgin Olive Oil","energy_100g":884,"proteins_100g":0.0,"fat_100g":100.0,"carbohydrates_100g":0.0,"sugars_100g":0.0,"fiber_100g":0.0,"salt_100g":0.00,"ingredients_text":"Cold-pressed extra virgin olive oil."},
        {"category":"Oils & Condiments","display_name":"Natural Peanut Butter","energy_100g":588,"proteins_100g":25.1,"fat_100g":49.9,"carbohydrates_100g":20.1,"sugars_100g":5.0,"fiber_100g":5.9,"salt_100g":0.01,"ingredients_text":"Dry roasted peanuts."},
        {"category":"Oils & Condiments","display_name":"Classic Hummus","energy_100g":166,"proteins_100g":7.9,"fat_100g":9.6,"carbohydrates_100g":14.3,"sugars_100g":0.4,"fiber_100g":6.0,"salt_100g":0.64,"ingredients_text":"Chickpeas, tahini, lemon juice, garlic, olive oil, salt."},
        {"category":"Oils & Condiments","display_name":"Virgin Coconut Oil","energy_100g":892,"proteins_100g":0.0,"fat_100g":99.1,"carbohydrates_100g":0.0,"sugars_100g":0.0,"fiber_100g":0.0,"salt_100g":0.00,"ingredients_text":"Cold-pressed virgin coconut oil."},
        {"category":"Oils & Condiments","display_name":"Sunflower Oil","energy_100g":884,"proteins_100g":0.0,"fat_100g":100.0,"carbohydrates_100g":0.0,"sugars_100g":0.0,"fiber_100g":0.0,"salt_100g":0.00,"ingredients_text":"Refined sunflower oil."},
        {"category":"Oils & Condiments","display_name":"Tomato Ketchup","energy_100g":101,"proteins_100g":1.4,"fat_100g":0.1,"carbohydrates_100g":24.0,"sugars_100g":20.1,"fiber_100g":0.9,"salt_100g":1.90,"ingredients_text":"Tomatoes, vinegar, sugar, salt, spices."},
        {"category":"Oils & Condiments","display_name":"Yellow Mustard","energy_100g":66,"proteins_100g":4.4,"fat_100g":3.3,"carbohydrates_100g":6.4,"sugars_100g":3.3,"fiber_100g":3.1,"salt_100g":1.50,"ingredients_text":"Mustard seed, vinegar, water, salt, turmeric."},
        {"category":"Oils & Condiments","display_name":"Full Fat Mayonnaise","energy_100g":680,"proteins_100g":1.0,"fat_100g":75.0,"carbohydrates_100g":0.9,"sugars_100g":0.5,"fiber_100g":0.0,"salt_100g":1.40,"ingredients_text":"Sunflower oil, water, egg yolk, mustard, vinegar, salt."},
        {"category":"Oils & Condiments","display_name":"Soy Sauce","energy_100g":53,"proteins_100g":5.6,"fat_100g":0.0,"carbohydrates_100g":8.0,"sugars_100g":1.7,"fiber_100g":0.5,"salt_100g":15.50,"ingredients_text":"Soybean, wheat, salt, water."},
        {"category":"Oils & Condiments","display_name":"Almond Butter","energy_100g":614,"proteins_100g":21.0,"fat_100g":55.5,"carbohydrates_100g":18.8,"sugars_100g":4.4,"fiber_100g":10.3,"salt_100g":0.03,"ingredients_text":"Dry roasted almonds."},
        {"category":"Oils & Condiments","display_name":"Sesame Tahini","energy_100g":595,"proteins_100g":17.0,"fat_100g":53.8,"carbohydrates_100g":21.2,"sugars_100g":0.5,"fiber_100g":9.3,"salt_100g":0.01,"ingredients_text":"Ground sesame seeds."},
        {"category":"Oils & Condiments","display_name":"Strawberry Jam","energy_100g":257,"proteins_100g":0.4,"fat_100g":0.1,"carbohydrates_100g":66.0,"sugars_100g":63.0,"fiber_100g":0.9,"salt_100g":0.03,"ingredients_text":"Strawberries, sugar, lemon juice, pectin."},
        {"category":"Oils & Condiments","display_name":"Pure Honey","energy_100g":304,"proteins_100g":0.3,"fat_100g":0.0,"carbohydrates_100g":82.4,"sugars_100g":82.1,"fiber_100g":0.2,"salt_100g":0.00,"ingredients_text":"Pure honey."},
        {"category":"Oils & Condiments","display_name":"Basil Pesto","energy_100g":399,"proteins_100g":5.3,"fat_100g":40.0,"carbohydrates_100g":4.8,"sugars_100g":1.9,"fiber_100g":1.4,"salt_100g":1.50,"ingredients_text":"Basil, sunflower oil, pine nuts, parmesan, garlic, salt."},
        {"category":"Oils & Condiments","display_name":"Rapeseed Oil","energy_100g":899,"proteins_100g":0.0,"fat_100g":99.9,"carbohydrates_100g":0.0,"sugars_100g":0.0,"fiber_100g":0.0,"salt_100g":0.00,"ingredients_text":"Cold-pressed rapeseed oil."},
        # Beverages
        {"category":"Beverages","display_name":"Fresh Orange Juice","energy_100g":45,"proteins_100g":0.7,"fat_100g":0.2,"carbohydrates_100g":10.4,"sugars_100g":8.4,"fiber_100g":0.2,"salt_100g":0.00,"ingredients_text":"Freshly squeezed orange juice."},
        {"category":"Beverages","display_name":"Unsweetened Oat Milk","energy_100g":40,"proteins_100g":1.0,"fat_100g":1.5,"carbohydrates_100g":6.5,"sugars_100g":4.0,"fiber_100g":0.8,"salt_100g":0.10,"ingredients_text":"Water, oats, salt, vitamins."},
        {"category":"Beverages","display_name":"Unsweetened Almond Milk","energy_100g":17,"proteins_100g":0.6,"fat_100g":1.1,"carbohydrates_100g":1.2,"sugars_100g":0.0,"fiber_100g":0.4,"salt_100g":0.08,"ingredients_text":"Water, almonds, salt."},
        {"category":"Beverages","display_name":"Unsweetened Soy Milk","energy_100g":33,"proteins_100g":3.3,"fat_100g":1.8,"carbohydrates_100g":0.5,"sugars_100g":0.0,"fiber_100g":0.5,"salt_100g":0.13,"ingredients_text":"Water, soybeans, sea salt, vitamins."},
        {"category":"Beverages","display_name":"Brewed Green Tea","energy_100g":1,"proteins_100g":0.0,"fat_100g":0.0,"carbohydrates_100g":0.2,"sugars_100g":0.0,"fiber_100g":0.0,"salt_100g":0.00,"ingredients_text":"Green tea, water."},
        {"category":"Beverages","display_name":"Brewed Black Coffee","energy_100g":2,"proteins_100g":0.3,"fat_100g":0.0,"carbohydrates_100g":0.0,"sugars_100g":0.0,"fiber_100g":0.0,"salt_100g":0.00,"ingredients_text":"Ground coffee, water."},
        {"category":"Beverages","display_name":"Coconut Water","energy_100g":19,"proteins_100g":0.7,"fat_100g":0.2,"carbohydrates_100g":3.7,"sugars_100g":2.6,"fiber_100g":1.1,"salt_100g":0.05,"ingredients_text":"Coconut water."},
        {"category":"Beverages","display_name":"Chocolate Protein Shake","energy_100g":63,"proteins_100g":7.5,"fat_100g":1.0,"carbohydrates_100g":6.5,"sugars_100g":3.5,"fiber_100g":1.5,"salt_100g":0.20,"ingredients_text":"Water, whey protein, cocoa powder, sweetener."},
        # Prepared & Ready
        {"category":"Prepared & Ready","display_name":"Canned Tomato Soup","energy_100g":46,"proteins_100g":1.2,"fat_100g":1.4,"carbohydrates_100g":7.2,"sugars_100g":3.9,"fiber_100g":0.8,"salt_100g":0.65,"ingredients_text":"Tomatoes, water, tomato paste, sugar, modified starch, salt."},
        {"category":"Prepared & Ready","display_name":"Baked Beans In Tomato Sauce","energy_100g":81,"proteins_100g":4.7,"fat_100g":0.2,"carbohydrates_100g":15.3,"sugars_100g":4.2,"fiber_100g":3.7,"salt_100g":0.59,"ingredients_text":"Haricot beans, tomatoes, water, sugar, salt, modified cornflour."},
        {"category":"Prepared & Ready","display_name":"Chicken Tikka Masala","energy_100g":103,"proteins_100g":8.1,"fat_100g":4.2,"carbohydrates_100g":8.7,"sugars_100g":4.1,"fiber_100g":1.1,"salt_100g":0.68,"ingredients_text":"Chicken breast, tomatoes, cream, onion, spices, oil, garlic, ginger."},
        {"category":"Prepared & Ready","display_name":"Frozen Fish Fingers","energy_100g":230,"proteins_100g":14.0,"fat_100g":9.8,"carbohydrates_100g":22.6,"sugars_100g":1.0,"fiber_100g":0.9,"salt_100g":0.82,"ingredients_text":"Fish (58%), breadcrumbs, flour, salt, oil."},
        {"category":"Prepared & Ready","display_name":"Red Lentil Dhal","energy_100g":89,"proteins_100g":5.5,"fat_100g":2.8,"carbohydrates_100g":11.3,"sugars_100g":1.9,"fiber_100g":3.5,"salt_100g":0.54,"ingredients_text":"Red lentils, tomatoes, onion, coconut oil, garlic, ginger, spices."},
        {"category":"Prepared & Ready","display_name":"Greek Salad With Feta","energy_100g":144,"proteins_100g":5.2,"fat_100g":11.7,"carbohydrates_100g":5.0,"sugars_100g":4.1,"fiber_100g":1.5,"salt_100g":1.12,"ingredients_text":"Cucumber, tomatoes, feta cheese, olives, onion, olive oil, oregano."},
        {"category":"Prepared & Ready","display_name":"Minestrone Soup","energy_100g":52,"proteins_100g":2.3,"fat_100g":1.5,"carbohydrates_100g":7.9,"sugars_100g":2.8,"fiber_100g":1.9,"salt_100g":0.55,"ingredients_text":"Vegetables, pasta, tomatoes, broth, olive oil, herbs."},
    ]
    return pd.DataFrame(records), False


# ── Load & index ─────────────────────────────────────────────────────────────
df, _csv_loaded = load_data()
CATEGORIES = ["All"] + sorted(df["category"].unique().tolist())


# ============================================================================
# HEADER
# ============================================================================
_hl, _hr = st.columns([4, 1])
with _hl:
    st.markdown('<span class="pl-eyebrow">Nutrition Intelligence Platform</span>', unsafe_allow_html=True)
    st.markdown('<div class="pl-wordmark">Pure<em>Label</em></div>', unsafe_allow_html=True)
with _hr:
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("☀ Light" if dark else "◑ Dark", key="theme_toggle"):
        st.session_state.dark_mode = not dark
        st.rerun()

st.markdown('<hr class="pl-divider">', unsafe_allow_html=True)

# Database banner
if _csv_loaded:
    st.markdown(f"""
    <div style="background:{T['green_pale']};border:1px solid {T['green']}44;border-radius:12px;
         padding:0.6rem 1.2rem;margin-bottom:0.75rem;">
        <span style="color:{T['green']};">✓</span>
        <span style="color:{T['text_secondary']};font-size:0.82rem;margin-left:0.5rem;">
            Loaded <b style="color:{T['text_primary']};">{len(df):,}</b> English-language products
            from Open Food Facts · non-English names auto-translated to English
        </span>
    </div>""", unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div style="background:{T['yellow_pale']};border:1px solid {T['yellow']}44;border-radius:12px;
         padding:0.6rem 1.2rem;margin-bottom:0.75rem;">
        <span style="color:{T['yellow']};">ℹ</span>
        <span style="color:{T['text_secondary']};font-size:0.82rem;margin-left:0.5rem;">
            Running with built-in database ({len(df)} products). To load all
            <b style="color:{T['text_primary']};">~300k Open Food Facts products</b>, place
            <code>en.openfoodfacts.org.products.csv</code> in the same folder as app.py
            (download free from <b>kaggle.com/datasets/openfoodfacts/world-food-facts</b>).
        </span>
    </div>""", unsafe_allow_html=True)

# NAV
_nc = st.columns([1,1,1,1,1,3])
for _col, _lbl, _vw in zip(_nc, ["Dashboard","Search","Compare","Manual","About"],
                            ["home","search","compare","manual","about"]):
    with _col:
        if st.button(_lbl, use_container_width=True):
            st.session_state.view = _vw
            st.rerun()

st.markdown("<br>", unsafe_allow_html=True)


# ============================================================================
# VIEW: DASHBOARD
# ============================================================================
if st.session_state.view == 'home':
    st.markdown('<div class="pl-section-title">Dashboard</div>', unsafe_allow_html=True)

    c1,c2,c3,c4 = st.columns(4)
    for col,(lbl,val,sub) in zip([c1,c2,c3,c4],[
        ("Products",  f"{len(df):,}", "In database"),
        ("Categories",str(len(df['category'].unique())), "Food groups"),
        ("Method",    "4·4·9", "Atwater system"),
        ("Standard",  "WHO / FSA", "Regulatory basis"),
    ]):
        with col:
            st.markdown(f"""
            <div class="stat-tile">
                <div class="pl-label">{lbl}</div>
                <div class="st-number">{val}</div>
                <div class="st-label">{sub}</div>
            </div>""", unsafe_allow_html=True)

    # Smart Filters
    st.markdown('<div class="pl-section-title">Smart Filters</div>', unsafe_allow_html=True)
    sf_labels = list(SMART_FILTERS.keys())
    sf_cols   = st.columns(len(sf_labels))
    for i, lbl in enumerate(sf_labels):
        with sf_cols[i]:
            if st.button(lbl, key=f"sf_{i}", use_container_width=True):
                st.session_state.smart_filter = lbl
                st.rerun()

    current_sf = st.session_state.get('smart_filter', 'All')
    sf_fn      = SMART_FILTERS.get(current_sf, lambda r: True)

    selected_cat = st.selectbox("Filter by Category", CATEGORIES)
    base = df if selected_cat == "All" else df[df['category'] == selected_cat]
    filtered = base[base.apply(sf_fn, axis=1)].head(200)

    badge = f" · {current_sf}" if current_sf != "All" else ""
    st.markdown(f"<small style='color:{T['accent']};'>Showing {len(filtered)} product(s){badge}</small>",
                unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    if filtered.empty:
        st.markdown(f"""<div class="pl-card" style="text-align:center;padding:3rem;">
            <div style="font-size:2.5rem;margin-bottom:0.5rem;">⊘</div>
            <div style="color:{T['text_secondary']};">No products match this combination.</div>
        </div>""", unsafe_allow_html=True)

    col_a, col_b = st.columns(2, gap="medium")
    for i,(_, row) in enumerate(filtered.iterrows()):
        col  = col_a if i%2==0 else col_b
        kcal = calc_energy(row)
        sc, sl, sc_col = nutrition_score(row)
        fav_icon = "★" if row['display_name'] in st.session_state.favourites else "☆"
        in_cmp   = row['display_name'] in st.session_state.compare_list
        with col:
            st.markdown(f"""
            <div class="pl-card">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                <div>
                  <span class="pl-label">{row['category']}</span>
                  <div style="font-family:'DM Serif Display',serif;font-size:1.15rem;
                       color:{T['text_primary']};margin:0.2rem 0 0.5rem;">{row['display_name']}</div>
                </div>
                <div style="text-align:right;">
                  <div style="font-family:'DM Mono',monospace;font-size:1.1rem;color:{T['accent']};font-weight:500;">
                    {kcal:.0f}<small style="font-size:0.6rem;color:{T['text_muted']}"> kcal</small></div>
                  <small style="color:{T['text_muted']};">per 100g</small>
                  <div style="margin-top:0.3rem;">
                    <span style="background:{sc_col}22;color:{sc_col};border:1px solid {sc_col}44;
                      border-radius:100px;padding:0.1rem 0.55rem;font-size:0.63rem;
                      font-family:'DM Mono',monospace;letter-spacing:0.1em;">{sl}</span>
                  </div>
                </div>
              </div>
              <div style="display:flex;gap:1.2rem;font-family:'DM Mono',monospace;font-size:0.72rem;">
                <span style="color:{T['green']};">P {float(row['proteins_100g']):.1f}g</span>
                <span style="color:{T['accent']};">F {float(row['fat_100g']):.1f}g</span>
                <span style="color:{T['blue']};">C {float(row['carbohydrates_100g']):.1f}g</span>
                <span style="color:{T['text_muted']};">Fibre {float(row['fiber_100g']):.1f}g</span>
              </div>
            </div>""", unsafe_allow_html=True)
            b1,b2,b3 = st.columns([2,1,1])
            with b1:
                if st.button("Analyse →", key=f"h_an_{i}"):
                    st.session_state.product = row
                    st.session_state.view = 'analysis'
                    st.rerun()
            with b2:
                if st.button(fav_icon, key=f"h_fv_{i}"):
                    name = row['display_name']
                    if name in st.session_state.favourites:
                        st.session_state.favourites.remove(name)
                    else:
                        st.session_state.favourites.append(name)
                    st.rerun()
            with b3:
                if st.button("✓" if in_cmp else "+Cmp", key=f"h_cm_{i}"):
                    name = row['display_name']
                    if in_cmp:
                        st.session_state.compare_list.remove(name)
                    elif len(st.session_state.compare_list) < 4:
                        st.session_state.compare_list.append(name)
                    st.rerun()

    if st.session_state.favourites:
        st.markdown('<div class="pl-section-title">★ Favourites</div>', unsafe_allow_html=True)
        fav_df = df[df['display_name'].isin(st.session_state.favourites)]
        for _, row in fav_df.iterrows():
            kcal = calc_energy(row)
            fa,fb = st.columns([4,1])
            with fa:
                st.markdown(f"""
                <div class="pl-card pl-card-gold">
                  <span style="font-family:'DM Serif Display',serif;font-size:1.1rem;
                        color:{T['text_primary']};">{row['display_name']}</span>
                  <span style="font-family:'DM Mono',monospace;font-size:0.8rem;
                        color:{T['accent']};margin-left:0.75rem;">{kcal:.0f} kcal</span>
                </div>""", unsafe_allow_html=True)
            with fb:
                if st.button("Analyse", key=f"fv_an_{row['display_name']}"):
                    st.session_state.product = row
                    st.session_state.view = 'analysis'
                    st.rerun()


# ============================================================================
# VIEW: SEARCH
# ============================================================================
elif st.session_state.view == 'search':
    st.markdown('<div class="pl-section-title">Search Database</div>', unsafe_allow_html=True)

    sq, sc2 = st.columns([3,1])
    with sq:
        query = st.text_input("", placeholder="Search products or ingredients…")
    with sc2:
        cat_filter = st.selectbox("Category", CATEGORIES)

    filtered = df.copy()
    if cat_filter != "All":
        filtered = filtered[filtered['category'] == cat_filter]
    if query.strip():
        q = query.strip().lower()
        mask = (
            filtered['display_name'].str.lower().str.contains(q, na=False) |
            filtered['ingredients_text'].str.lower().str.contains(q, na=False)
        )
        filtered = filtered[mask]

    total     = len(filtered)
    PAGE_SIZE = 50
    page      = st.session_state.get('search_page', 0)
    max_page  = max(0, (total-1)//PAGE_SIZE)
    page      = min(page, max_page)

    st.markdown(
        f"<small style='color:{T['text_muted']};'>{total:,} result(s)"
        + (f" · page {page+1}/{max_page+1}" if total > PAGE_SIZE else "")
        + "</small>",
        unsafe_allow_html=True
    )

    if total > PAGE_SIZE:
        pga, pgb = st.columns([1,1])
        with pga:
            if st.button("◀ Prev", disabled=(page==0)):
                st.session_state.search_page = page-1; st.rerun()
        with pgb:
            if st.button("Next ▶", disabled=(page>=max_page)):
                st.session_state.search_page = page+1; st.rerun()

    page_df = filtered.iloc[page*PAGE_SIZE:(page+1)*PAGE_SIZE]

    if page_df.empty:
        st.markdown(f"""<div class="pl-card" style="text-align:center;padding:3rem;">
            <div style="font-size:2.5rem;margin-bottom:0.5rem;">⊘</div>
            <div style="color:{T['text_secondary']};">No products found.</div>
        </div>""", unsafe_allow_html=True)

    for i,(_, row) in enumerate(page_df.iterrows()):
        kcal   = calc_energy(row)
        sc, sl, sc_col = nutrition_score(row)
        in_cmp = row['display_name'] in st.session_state.compare_list
        st.markdown(f"""
        <div class="pl-card">
          <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.5rem;">
            <div>
              <span class="chip">{row['category']}</span>
              <span style="background:{sc_col}22;color:{sc_col};border:1px solid {sc_col}44;
                border-radius:100px;padding:0.1rem 0.55rem;font-size:0.63rem;
                font-family:'DM Mono',monospace;letter-spacing:0.1em;margin-left:0.3rem;">{sl}</span>
              <div style="font-family:'DM Serif Display',serif;font-size:1.2rem;
                   color:{T['text_primary']};margin:0.4rem 0 0.3rem;">{row['display_name']}</div>
              <div style="font-size:0.78rem;color:{T['text_muted']};font-family:'DM Mono',monospace;">
                P {float(row['proteins_100g']):.1f}g &nbsp;·&nbsp;
                F {float(row['fat_100g']):.1f}g &nbsp;·&nbsp;
                C {float(row['carbohydrates_100g']):.1f}g &nbsp;·&nbsp;
                Fibre {float(row['fiber_100g']):.1f}g
              </div>
            </div>
            <div style="text-align:right;">
              <div style="font-family:'DM Mono',monospace;font-size:1.5rem;color:{T['accent']};">{kcal:.0f}</div>
              <div style="font-size:0.68rem;color:{T['text_muted']};letter-spacing:0.1em;">KCAL / 100G</div>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)
        ba,bb,_ = st.columns([1.2,1.5,5])
        with ba:
            if st.button("Analyse →", key=f"s_an_{i}_{page}"):
                st.session_state.product = row
                st.session_state.view = 'analysis'
                st.rerun()
        with bb:
            lbl = "✓ In Compare" if in_cmp else "+ Compare"
            if st.button(lbl, key=f"s_cm_{i}_{page}"):
                name = row['display_name']
                if in_cmp:
                    st.session_state.compare_list.remove(name)
                elif len(st.session_state.compare_list) < 4:
                    st.session_state.compare_list.append(name)
                st.rerun()


# ============================================================================
# VIEW: COMPARE
# ============================================================================
elif st.session_state.view == 'compare':
    st.markdown('<div class="pl-section-title">Product Comparison</div>', unsafe_allow_html=True)

    if st.session_state.compare_list:
        chips = "".join([f'<span class="chip">{n}</span>' for n in st.session_state.compare_list])
        st.markdown(f"""
        <div class="pl-card pl-card-gold" style="margin-bottom:1rem;">
          <div class="pl-label">Compare List ({len(st.session_state.compare_list)}/4)</div>
          <div style="margin-top:0.5rem;display:flex;flex-wrap:wrap;gap:0.4rem;">{chips}</div>
        </div>""", unsafe_allow_html=True)
        if st.button("Clear All", key="cmp_clear"):
            st.session_state.compare_list = []
            st.rerun()

    all_names = df['display_name'].tolist()
    valid_default = [n for n in st.session_state.compare_list if n in all_names][:4]
    selected = st.multiselect("Select up to 4 products", all_names, default=valid_default, max_selections=4)
    st.session_state.compare_list = selected

    if len(selected) < 2:
        st.markdown(f"""
        <div class="pl-card" style="text-align:center;padding:2.5rem;border-style:dashed;">
          <div style="font-family:'DM Serif Display',serif;font-size:1.3rem;color:{T['text_muted']};">
            Select at least 2 products to compare</div>
          <p style="margin-top:0.5rem;">Use "+ Compare" buttons on Dashboard or Search.</p>
        </div>""", unsafe_allow_html=True)
    else:
        cmp_df = df[df['display_name'].isin(selected)].copy()
        order  = {n:i for i,n in enumerate(selected)}
        cmp_df = cmp_df.sort_values('display_name', key=lambda s: s.map(order)).reset_index(drop=True)
        cmp_df['energy_calc'] = cmp_df.apply(calc_energy, axis=1)

        # Header cards
        cols = st.columns(len(selected))
        for col,(_, row) in zip(cols, cmp_df.iterrows()):
            with col:
                sc,sl,sc_col = nutrition_score(row)
                st.markdown(f"""
                <div class="pl-card pl-card-gold" style="text-align:center;">
                  <span class="pl-label">{row['category']}</span>
                  <div style="font-family:'DM Serif Display',serif;font-size:0.95rem;
                       color:{T['text_primary']};margin:0.3rem 0;">{row['display_name']}</div>
                  <div style="font-family:'DM Mono',monospace;font-size:1.5rem;
                       color:{T['accent']};">{row['energy_calc']:.0f}</div>
                  <div style="font-size:0.68rem;color:{T['text_muted']};letter-spacing:0.1em;
                       margin-bottom:0.5rem;">KCAL / 100G</div>
                  <span style="background:{sc_col}22;color:{sc_col};border:1px solid {sc_col}44;
                    border-radius:100px;padding:0.15rem 0.7rem;font-size:0.63rem;
                    font-family:'DM Mono',monospace;letter-spacing:0.1em;">{sl}</span>
                </div>""", unsafe_allow_html=True)
                if st.button("Analyse →", key=f"cmp_an_{row['display_name']}"):
                    st.session_state.product = row
                    st.session_state.view = 'analysis'
                    st.rerun()

        # Radar chart
        metrics = ['proteins_100g','fat_100g','carbohydrates_100g','fiber_100g','sugars_100g']
        mlabels = ['Protein','Fat','Carbs','Fibre','Sugar']
        colors  = [T['accent'], T['green'], T['blue'], T['red']]
        fig = go.Figure()
        for (_,row),color in zip(cmp_df.iterrows(), colors):
            maxes = [float(cmp_df[m].max()) or 1 for m in metrics]
            vals  = [float(row[m])/mx*100 for m,mx in zip(metrics,maxes)]
            fig.add_trace(go.Scatterpolar(
                r=vals+[vals[0]], theta=mlabels+[mlabels[0]],
                fill='toself', name=row['display_name'],
                line=dict(color=color, width=2),
                fillcolor=hex_to_rgba(color, 0.12),
                opacity=0.85
            ))
        fig.update_layout(
            polar=dict(
                bgcolor='rgba(0,0,0,0)',
                radialaxis=dict(visible=True, showticklabels=False,
                                gridcolor=T['chart_grid'], linecolor=T['chart_grid']),
                angularaxis=dict(gridcolor=T['chart_grid'], linecolor=T['chart_grid'],
                                 tickfont=dict(color=T['text_secondary'],family="DM Sans",size=11))
            ),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(font=dict(color=T['text_secondary'],family="DM Sans",size=11),bgcolor='rgba(0,0,0,0)'),
            margin=dict(t=30,b=30,l=30,r=30), height=360
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar':False})

        # Table
        st.markdown('<div class="pl-section-title">Nutritional Breakdown</div>', unsafe_allow_html=True)
        nutrients = [
            ('Energy (calc)',  'energy_calc',        'kcal', False),
            ('Protein',        'proteins_100g',      'g',    True),
            ('Fat',            'fat_100g',           'g',    False),
            ('Carbohydrates',  'carbohydrates_100g', 'g',    False),
            ('of which Sugars','sugars_100g',        'g',    False),
            ('Fibre',          'fiber_100g',         'g',    True),
            ('Salt',           'salt_100g',          'g',    False),
        ]
        header  = "| Nutrient |" + "".join([f" {r['display_name']} |" for _,r in cmp_df.iterrows()])
        sep     = "|---|" + "---|"*len(cmp_df)
        rows_md = ""
        for lbl,col_name,unit,hib in nutrients:
            vals     = [float(r[col_name]) for _,r in cmp_df.iterrows()]
            best_idx = vals.index(max(vals)) if hib else vals.index(min(vals))
            row_str  = f"| **{lbl}** |"
            for j,v in enumerate(vals):
                row_str += f" {v:.1f}{unit}{'🏆' if j==best_idx else ''} |"
            rows_md += row_str + "\n"
        st.markdown(header+"\n"+sep+"\n"+rows_md)

        # Bar chart
        fig2 = go.Figure()
        for metric,lbl,bcolor in [
            ('proteins_100g','Protein (g)',T['green']),
            ('fat_100g','Fat (g)',T['accent']),
            ('carbohydrates_100g','Carbs (g)',T['blue']),
            ('fiber_100g','Fibre (g)',T['yellow'])
        ]:
            fig2.add_trace(go.Bar(
                name=lbl, x=cmp_df['display_name'].tolist(),
                y=[float(v) for v in cmp_df[metric].tolist()],
                marker_color=bcolor, opacity=0.85
            ))
        fig2.update_layout(
            barmode='group', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color=T['text_secondary'],family="DM Sans"),
            xaxis=dict(gridcolor=T['chart_grid'],tickfont=dict(color=T['text_secondary'])),
            yaxis=dict(gridcolor=T['chart_grid'],tickfont=dict(color=T['text_secondary']),title='g per 100g'),
            legend=dict(bgcolor='rgba(0,0,0,0)',font=dict(color=T['text_secondary'])),
            margin=dict(t=20,b=20,l=20,r=20), height=320
        )
        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar':False})


# ============================================================================
# VIEW: MANUAL ENTRY
# ============================================================================
elif st.session_state.view == 'manual':
    st.markdown('<div class="pl-section-title">Manual Entry</div>', unsafe_allow_html=True)
    st.markdown('<p>Enter values per 100g from any product label. Energy is computed via Atwater 4·4·9.</p>', unsafe_allow_html=True)

    with st.form("manual_form"):
        name = st.text_input("Product Name", placeholder="e.g. Homemade Protein Bar")
        cat  = st.selectbox("Category", [c for c in CATEGORIES if c != "All"])
        ingr = st.text_area("Ingredients (optional)", placeholder="e.g. oats, peanut butter, honey")
        st.markdown("<br>", unsafe_allow_html=True)
        mc1,mc2,mc3 = st.columns(3)
        with mc1:
            protein = st.number_input("Protein (g)",       0.0,100.0,10.0,0.1)
            fat     = st.number_input("Fat (g)",           0.0,100.0, 8.0,0.1)
        with mc2:
            carbs  = st.number_input("Carbohydrates (g)",  0.0,100.0,30.0,0.1)
            sugars = st.number_input("of which Sugars (g)",0.0,100.0, 8.0,0.1)
        with mc3:
            fiber = st.number_input("Fibre (g)",   0.0,50.0,3.0,0.1)
            salt  = st.number_input("Salt (g)",    0.0,10.0,0.3,0.01)
        submitted = st.form_submit_button("Generate Analysis →")

    if submitted and name:
        manual_row = pd.Series({
            'display_name':       name,
            'category':           cat,
            'energy_100g':        protein*4 + carbs*4 + fat*9,
            'proteins_100g':      protein,
            'fat_100g':           fat,
            'carbohydrates_100g': carbs,
            'sugars_100g':        sugars,
            'fiber_100g':         fiber,
            'salt_100g':          salt,
            'ingredients_text':   ingr or 'User-entered data — ingredients not specified.',
        })
        st.session_state.product = manual_row
        st.session_state.view    = 'analysis'
        st.rerun()


# ============================================================================
# VIEW: ANALYSIS
# ============================================================================
elif st.session_state.view == 'analysis':
    p = st.session_state.product
    if p is None:
        st.warning("No product selected.")
        st.stop()

    bk,_ = st.columns([1,5])
    with bk:
        if st.button("← Back"):
            st.session_state.view = 'home'; st.rerun()

    kcal        = calc_energy(p)
    label_kcal  = float(p.get('energy_100g', 0) or 0)
    delta       = abs(kcal-label_kcal)/label_kcal*100 if label_kcal else 0
    total_macro = float(p['proteins_100g'] or 0)+float(p['fat_100g'] or 0)+float(p['carbohydrates_100g'] or 0)
    sc,sl,sc_col = nutrition_score(p)

    st.markdown(f"""
    <div style="margin-bottom:0.5rem;">
      <span class="chip">{p.get('category','')}</span>
      <span style="background:{sc_col}22;color:{sc_col};border:1px solid {sc_col}44;
        border-radius:100px;padding:0.15rem 0.7rem;font-size:0.65rem;
        font-family:'DM Mono',monospace;letter-spacing:0.1em;margin-left:0.5rem;">{sl}</span>
    </div>
    <div class="pl-wordmark" style="font-size:2.2rem;margin-bottom:1.5rem;">{p['display_name']}</div>
    """, unsafe_allow_html=True)

    qs = st.columns(5)
    for col,(lbl,val,unit) in zip(qs,[
        ("Energy",  f"{kcal:.0f}",                              "kcal / 100g"),
        ("Protein", f"{float(p['proteins_100g']):.1f}",         "g / 100g"),
        ("Fat",     f"{float(p['fat_100g']):.1f}",              "g / 100g"),
        ("Carbs",   f"{float(p['carbohydrates_100g']):.1f}",    "g / 100g"),
        ("Fibre",   f"{float(p['fiber_100g']):.1f}",            "g / 100g"),
    ]):
        with col:
            st.markdown(f"""
            <div class="stat-tile">
              <div class="pl-label">{lbl}</div>
              <div class="st-number">{val}</div>
              <div class="st-unit">{unit}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    ac1,ac2 = st.columns([1,1], gap="large")

    with ac1:
        st.markdown(f"""
        <div class="pl-card">
          <div class="pl-label">Macro Distribution</div>
          <div style="margin-top:1rem;">
            {macro_bar_html("Protein",       float(p['proteins_100g']),      total_macro or 1, T['green'])}
            {macro_bar_html("Fat",           float(p['fat_100g']),           total_macro or 1, T['accent'])}
            {macro_bar_html("Carbohydrates", float(p['carbohydrates_100g']), total_macro or 1, T['blue'])}
            {macro_bar_html("Sugars (of Carbs)", float(p['sugars_100g']),   float(p['carbohydrates_100g']) or 1, T['red'])}
            {macro_bar_html("Fibre",         float(p['fiber_100g']),         total_macro or 1, T['yellow'])}
          </div>
        </div>""", unsafe_allow_html=True)

        if total_macro > 0:
            fig_d = go.Figure(go.Pie(
                labels=['Protein','Fat','Carbohydrates'],
                values=[float(p['proteins_100g']),float(p['fat_100g']),float(p['carbohydrates_100g'])],
                hole=0.68,
                marker=dict(colors=[T['green'],T['accent'],T['blue']],
                            line=dict(color=T['bg_primary'],width=3)),
                textinfo='none',
                hovertemplate='%{label}: %{value}g (%{percent})<extra></extra>'
            ))
            fig_d.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(t=0,b=0,l=0,r=0), height=220, showlegend=True,
                legend=dict(orientation="h",x=0.5,xanchor="center",y=-0.05,
                            font=dict(family="DM Sans",size=11,color=T['text_secondary'])),
                annotations=[dict(text=f"<b>{kcal:.0f}</b><br><span style='font-size:9px;'>kcal</span>",
                                  x=0.5,y=0.5,
                                  font=dict(family="DM Serif Display",size=18,color=T['text_primary']),
                                  showarrow=False)]
            )
            st.plotly_chart(fig_d, use_container_width=True, config={'displayModeBar':False})

        st.markdown(f"""
        <div class="pl-card">
          <div class="pl-label">% of WHO Daily Reference (2000 kcal adult)</div>
          <div style="margin-top:1rem;">
            {macro_bar_html("Calories",          kcal,                              2000, fsa_color('fat',0))}
            {macro_bar_html("Protein (50g ref)", float(p['proteins_100g']),         50,   T['green'])}
            {macro_bar_html("Fat (70g ref)",     float(p['fat_100g']),              70,   T['accent'])}
            {macro_bar_html("Sugar (90g ref)",   float(p['sugars_100g']),           90,   fsa_color('sugar',float(p['sugars_100g'])))}
            {macro_bar_html("Salt (5g WHO max)", float(p['salt_100g']),             5,    fsa_color('salt', float(p['salt_100g'])))}
          </div>
        </div>""", unsafe_allow_html=True)

    with ac2:
        st.markdown(f"""
        <div class="pl-card">
          <div class="pl-label">Nutrition Facts · per 100g</div>
          <table class="nt" style="margin-top:1rem;">
            <tr><td>Energy (Label)</td><td class="nt-val">{label_kcal:.0f} kcal</td></tr>
            <tr><td>Energy (Atwater calc.)</td><td class="nt-accent">{kcal:.0f} kcal</td></tr>
            <tr><td>Label Variance</td><td class="nt-val">{delta:.1f}%</td></tr>
            <tr><td class="nt-head">Protein</td><td class="nt-val" style="padding-top:1rem;">{float(p['proteins_100g']):.1f}g</td></tr>
            <tr><td class="nt-head">Fat</td><td class="nt-val">{float(p['fat_100g']):.1f}g</td></tr>
            <tr><td class="nt-head">Carbohydrates</td><td class="nt-val">{float(p['carbohydrates_100g']):.1f}g</td></tr>
            <tr><td class="nt-indent">&nbsp;of which Sugars</td><td class="nt-val">{float(p['sugars_100g']):.1f}g</td></tr>
            <tr><td class="nt-head">Fibre</td><td class="nt-val">{float(p['fiber_100g']):.1f}g</td></tr>
            <tr><td class="nt-head">Salt</td><td class="nt-val">{float(p['salt_100g']):.2f}g</td></tr>
          </table>
        </div>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="pl-card">
          <div class="pl-label">Ingredients</div>
          <p style="margin-top:0.5rem;font-size:0.84rem;font-style:italic;">{p['ingredients_text']}</p>
        </div>""", unsafe_allow_html=True)

        st.markdown(f'<div class="pl-label" style="margin-top:1rem;">Portion Calculator</div>', unsafe_allow_html=True)
        portion_g = st.slider("Portion size (g)", 10, 500, 100, 5)
        r = portion_g / 100
        st.markdown(f"""
        <div class="pl-card pl-card-gold">
          <div class="pl-label">For {portion_g}g serving</div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.5rem;margin-top:0.75rem;">
            <div><div style="font-family:'DM Mono',monospace;font-size:1.1rem;color:{T['accent']};">{kcal*r:.0f} kcal</div><div style="font-size:0.72rem;color:{T['text_muted']};">Energy</div></div>
            <div><div style="font-family:'DM Mono',monospace;font-size:1.1rem;color:{T['green']};">{float(p['proteins_100g'])*r:.1f}g</div><div style="font-size:0.72rem;color:{T['text_muted']};">Protein</div></div>
            <div><div style="font-family:'DM Mono',monospace;font-size:1.1rem;color:{T['accent']};">{float(p['fat_100g'])*r:.1f}g</div><div style="font-size:0.72rem;color:{T['text_muted']};">Fat</div></div>
            <div><div style="font-family:'DM Mono',monospace;font-size:1.1rem;color:{T['blue']};">{float(p['carbohydrates_100g'])*r:.1f}g</div><div style="font-size:0.72rem;color:{T['text_muted']};">Carbs</div></div>
          </div>
        </div>""", unsafe_allow_html=True)

        in_cmp = p.get('display_name') in st.session_state.compare_list
        if st.button("✓ In Compare List" if in_cmp else "+ Add to Compare", key="an_cmp"):
            nm = p.get('display_name','')
            if nm and not in_cmp and len(st.session_state.compare_list) < 4:
                st.session_state.compare_list.append(nm)
                st.success("Added to compare list.")
            elif in_cmp:
                st.session_state.compare_list.remove(nm)
                st.rerun()

    st.markdown('<div class="pl-section-title">Regulatory Context</div>', unsafe_allow_html=True)
    notes = nutrient_notes(p)
    nc1,nc2 = st.columns(2)
    for i,(title,body,cls) in enumerate(notes):
        with (nc1 if i%2==0 else nc2):
            st.markdown(f"""
            <div class="pl-card {cls}">
              <div style="font-weight:600;color:{T['text_primary']};margin-bottom:0.3rem;font-size:0.9rem;">{title}</div>
              <p style="margin:0;font-size:0.83rem;">{body}</p>
            </div>""", unsafe_allow_html=True)

    st.markdown(f'<div class="pl-disclaimer">Contextual notes reference UK FSA nutrient profiling criteria, WHO daily intake recommendations, and EU Regulation 1924/2006. PureLabel is an educational tool only and does not constitute medical or dietary advice.</div>', unsafe_allow_html=True)


# ============================================================================
# VIEW: ABOUT
# ============================================================================
elif st.session_state.view == 'about':
    st.markdown('<div class="pl-section-title">About PureLabel</div>', unsafe_allow_html=True)
    ab1,ab2 = st.columns(2, gap="large")
    with ab1:
        st.markdown(f"""
        <div class="pl-card pl-card-gold">
          <span class="pl-label">Philosophy</span>
          <div style="font-family:'DM Serif Display',serif;font-size:1.4rem;color:{T['text_primary']};margin:0.5rem 0 0.75rem;font-style:italic;">Context, not judgment.</div>
          <p>PureLabel translates nutrition labels into clear, evidence-based context.  No food is labelled "good" or "bad."  We surface what regulatory science says — nothing more.</p>
        </div>
        <div class="pl-card">
          <span class="pl-label">Calorie Method</span>
          <div style="font-family:'DM Serif Display',serif;font-size:1.1rem;color:{T['text_primary']};margin:0.5rem 0;">Atwater General Factors</div>
          <p>Energy is computed as <b>Protein × 4 + Carbohydrate × 4 + Fat × 9</b> (kcal/g), cross-referenced against label values to flag variances &gt;10%.</p>
        </div>
        <div class="pl-card">
          <span class="pl-label">Database</span>
          <p style="margin-top:0.5rem;">Currently loaded: <b>{len(df):,} products</b>
          {'from Open Food Facts CSV.' if _csv_loaded else '(built-in curated set).'}<br><br>
          To load the full dataset (~300 k English products), download
          <b>en.openfoodfacts.org.products.csv</b> from
          <a href="https://www.kaggle.com/datasets/openfoodfacts/world-food-facts"
             style="color:{T['accent']};">kaggle.com/datasets/openfoodfacts/world-food-facts</a>
          and place it in the same folder as app.py.  Non-English names are
          automatically translated to English.</p>
        </div>
        """, unsafe_allow_html=True)
    with ab2:
        st.markdown(f"""
        <div class="pl-card">
          <span class="pl-label">Standards Referenced</span>
          <div style="margin-top:0.75rem;">
            <span class="chip">UK FSA</span><span class="chip">WHO</span>
            <span class="chip">EU Reg. 1924/2006</span><span class="chip">Atwater System</span><span class="chip">EFSA</span>
          </div>
          <p style="margin-top:1rem;">All thresholds come from published, fixed regulatory standards — never proprietary or speculative scores.</p>
        </div>
        <div class="pl-card">
          <span class="pl-label">Features</span>
          <p style="margin-top:0.5rem;">
            <b>Smart Filters</b> — One-click: High Protein, Low Sugar, High Fibre, Low Calorie, Low Salt, and more.<br>
            <b>Nutrition Score</b> — FSA/WHO badge: Excellent / Good / Moderate / Caution on every card.<br>
            <b>Search</b> — Full-text search across {len(df):,} products with pagination.<br>
            <b>Analysis</b> — Macro chart, donut, WHO reference bars, portion calculator, regulatory notes.<br>
            <b>Compare</b> — Radar + bar chart for up to 4 products, with per-nutrient 🏆 winner.<br>
            <b>Manual Entry</b> — Analyse any label by typing values directly.<br>
            <b>Favourites</b> — Star any product for fast recall.
          </p>
        </div>
        <div class="pl-card">
          <span class="pl-label">Disclaimer</span>
          <p style="margin-top:0.5rem;">For <b>educational purposes only</b>.  Does not account for individual health conditions, preparation methods, or bioavailability.  Always consult a registered dietitian.</p>
        </div>
        """, unsafe_allow_html=True)


# ============================================================================
# FOOTER
# ============================================================================
st.markdown(f"""
<div class="pl-footer">
  PureLabel &copy; 2026 &nbsp;·&nbsp; Data-Driven Nutrition &nbsp;·&nbsp;
  No Pseudoscience &nbsp;·&nbsp; WHO · UK FSA · EU 1924/2006
</div>
""", unsafe_allow_html=True)    
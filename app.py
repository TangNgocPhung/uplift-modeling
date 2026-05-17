"""
UpliftIQ — Editorial Design v4
Fix: gộp toàn bộ body vào 1 st.markdown() để padding apply đúng
Tăng padding 56px → 80px cho rộng rãi hơn
"""
import streamlit as st
import pandas as pd
import os
from datetime import date

st.set_page_config(
    page_title='UpliftIQ — Phân Tích Chiến Dịch Email',
    page_icon='▲',
    layout='wide',
    initial_sidebar_state='expanded',
)

MODELS_DIR = os.path.join(os.path.dirname(__file__), 'models')


# ── FONT ──
st.markdown(
    '<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,700&family=IBM+Plex+Mono:wght@300;400;500&family=IBM+Plex+Sans+Condensed:wght@300;400;600;700&display=swap" rel="stylesheet">',
    unsafe_allow_html=True
)


# ── CSS ──
st.markdown("""
<style>
.stApp { background: #F4EFE6; color: #1A2A47; font-family: 'IBM Plex Sans Condensed', sans-serif; }

[data-testid="stSidebar"] { background: #1A2A47 !important; border-right: 4px solid #B22234 !important; }
[data-testid="stSidebar"] * { color: #F4EFE6 !important; }

/* Ẩn Streamlit auto page navigation — CHỈ target container của auto nav, KHÔNG đụng tới custom nav user content */
[data-testid="stSidebarNav"], [data-testid="stSidebarNavItems"], [data-testid="stSidebarNavSeparator"], [data-testid="stSidebarNavLinkContainer"] { display: none !important; }
[data-testid="stSidebarNav"] ul, [data-testid="stSidebarNav"] hr { display: none !important; }

/* Đảm bảo nút toggle sidebar (mở/đóng) luôn click được, không bị masthead che */
[data-testid="stSidebarCollapsedControl"],
[data-testid="stSidebarCollapseButton"],
button[kind="header"] {
  z-index: 999999 !important;
  pointer-events: auto !important;
}
[data-testid="stSidebarCollapsedControl"] svg,
[data-testid="stSidebarCollapseButton"] svg { color: #1A2A47 !important; fill: #1A2A47 !important; }
[data-testid="stHeader"] { background: transparent !important; z-index: 999998 !important; }

/* ═══ Sidebar nav: compress khoảng cách + active state editorial ═══ */
[data-testid="stSidebar"] [data-testid="stElementContainer"]:has([data-testid="stPageLink"]) {
    margin: 0 !important; padding: 0 !important; min-height: 0 !important;
}
[data-testid="stSidebar"] [data-testid="stVerticalBlock"]:has([data-testid="stPageLink"]) {
    gap: 0 !important;
}
[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"],
[data-testid="stSidebar"] [data-testid="stPageLink"] a {
    background: transparent !important;
    border: none !important;
    border-left: 2px solid transparent !important;
    border-radius: 0 !important;
    padding: 5px 0 5px 12px !important;
    margin: 0 !important;
    min-height: 0 !important;
    line-height: 1.3 !important;
    font-family: 'IBM Plex Sans Condensed', sans-serif !important;
    font-size: 11px !important;
    color: #C7A270 !important;
    text-transform: uppercase;
    letter-spacing: .05em;
    transition: all .15s ease;
    display: flex !important;
    align-items: center !important;
}
[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"] *,
[data-testid="stSidebar"] [data-testid="stPageLink"] a * {
    color: inherit !important;
    font-family: 'IBM Plex Sans Condensed', sans-serif !important;
    font-size: 11px !important;
    line-height: 1.3 !important;
    margin: 0 !important; padding: 0 !important;
    background: transparent !important;
}
[data-testid="stSidebar"] a[aria-current="page"],
[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"] {
    border-left-color: #B22234 !important;
    color: #F4EFE6 !important;
    font-weight: 700 !important;
    background: rgba(178,34,52,0.05) !important;
}
[data-testid="stSidebar"] a[aria-current="page"] *,
[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"] * {
    color: #F4EFE6 !important; font-weight: 700 !important;
}
[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"]:hover,
[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {
    border-left-color: #B22234 !important;
    background: rgba(178,34,52,0.08) !important;
    color: #F4EFE6 !important;
}
[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"]:hover *,
[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover * {
    color: #F4EFE6 !important;
}
[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"] [data-testid="stIconMaterial"],
[data-testid="stSidebar"] [data-testid="stPageLink"] svg,
[data-testid="stSidebar"] [data-testid="stPageLink"] [data-testid*="Icon"] {
    display: none !important;
}

.block-container { padding: 0 !important; max-width: 100% !important; }

/* ═══ MASTHEAD ═══ */
.iq-mast { background: #1A2A47; color: #F4EFE6; }
.iq-mt { display: flex; justify-content: space-between; align-items: center; padding: 10px 80px; border-bottom: 1px solid #2C3E5C; font-family: 'IBM Plex Mono', monospace; font-size: 10px; color: #8C7B6B; letter-spacing: .12em; text-transform: uppercase; flex-wrap: wrap; gap: 8px; }
.iq-mc { text-align: center; padding: 24px 80px 0; }
.iq-mn { font-family: 'Playfair Display', serif; font-size: 72px; font-weight: 900; color: #F4EFE6; letter-spacing: -2px; line-height: 1; }
.iq-mn em { color: #B22234; font-style: normal; }
.iq-mtag { font-family: 'IBM Plex Sans Condensed', sans-serif; font-size: 13px; color: #C7A270; letter-spacing: .22em; text-transform: uppercase; margin-top: 6px; }
.iq-rule { height: 4px; margin: 16px 80px 0; background: #B22234; position: relative; }
.iq-rule::after { content: ''; position: absolute; left: 30%; top: 0; right: 0; bottom: 0; background: #C7A270; }
.iq-mk { display: flex; justify-content: space-between; padding: 10px 80px 16px; margin-top: 14px; border-top: 1px solid #2C3E5C; font-family: 'IBM Plex Mono', monospace; font-size: 10px; color: #C7A270; flex-wrap: wrap; gap: 8px; }

/* ═══ BODY ═══ padding 80px sẽ apply đúng vì tất cả trong 1 markdown call */
.iq-body { padding: 36px 80px; background: #F4EFE6; }

.iq-rub { font-family: 'IBM Plex Mono', monospace; font-size: 9px; font-weight: 500; letter-spacing: .25em; text-transform: uppercase; color: #B22234; margin-bottom: 6px; }

.iq-lead { display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: 0; border-top: 3px solid #1A2A47; border-bottom: 1px solid #C7A270; margin-bottom: 28px; }
.iq-ls { padding: 18px 22px 18px 0; border-right: 1px solid #C7A270; }
.iq-ls:last-child { border-right: none; padding-right: 0; }
.iq-ls:first-child { padding-left: 0; }
.iq-ls .v { font-family: 'Playfair Display', serif; font-size: 48px; font-weight: 900; line-height: 1; color: #1A2A47; }
.iq-ls .v.red { color: #B22234; }
.iq-ls .v.sage { color: #6B8068; }
.iq-ls .v.sm { font-size: 32px; }
.iq-ls .l { font-family: 'IBM Plex Sans Condensed', sans-serif; font-size: 11px; color: #4A6378; margin-top: 4px; text-transform: uppercase; letter-spacing: .1em; line-height: 1.4; font-weight: 600; }
.iq-ls .s { font-family: 'IBM Plex Mono', monospace; font-size: 9px; color: #8C7B6B; margin-top: 3px; }

.iq-pages { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0; border-top: 3px solid #1A2A47; border-bottom: 3px solid #1A2A47; margin-bottom: 28px; }
.iq-pi { display: block; padding: 16px 0; border-right: 1px solid #C7A270; text-align: center; text-decoration: none !important; color: inherit; cursor: pointer; transition: background .15s ease; position: relative; }
.iq-pi:last-child { border-right: none; }
.iq-pi:hover { background: #ECE5D7; }
.iq-pi:hover .n { color: #1A2A47; }
.iq-pi:hover::after { content: '→'; position: absolute; top: 12px; right: 14px; color: #B22234; font-family: 'IBM Plex Mono', monospace; font-size: 14px; }
.iq-pi .n { font-family: 'Playfair Display', serif; font-size: 32px; font-weight: 900; color: #B22234; line-height: 1; transition: color .15s ease; }
.iq-pi .t { font-family: 'IBM Plex Sans Condensed', sans-serif; font-size: 12px; font-weight: 700; color: #1A2A47; margin-top: 4px; text-transform: uppercase; letter-spacing: .06em; }
.iq-pi .d { font-family: 'IBM Plex Sans Condensed', sans-serif; font-size: 10px; color: #4A6378; margin-top: 3px; line-height: 1.4; padding: 0 10px; }
.iq-pi .f { font-family: 'IBM Plex Mono', monospace; font-size: 8px; color: #C7A270; margin-top: 6px; letter-spacing: .08em; }

.iq-nav-link { display: block; text-decoration: none !important; border-left: 2px solid transparent; padding: 4px 0 4px 10px; margin-bottom: 4px; color: #C7A270 !important; font-family: 'IBM Plex Sans Condensed', sans-serif; font-size: 11px; transition: all .15s ease; }
.iq-nav-link:hover { border-left-color: #B22234; color: #F4EFE6 !important; background: rgba(178,34,52,0.08); }

.iq-g3 { display: grid; grid-template-columns: 3fr 1px 2fr 1px 2fr; gap: 0; }
.iq-dv { background: #C7A270; }
.iq-col { padding: 0 22px; min-width: 0; }
.iq-col:first-child { padding-left: 0; }
.iq-col:last-child { padding-right: 0; }

.iq-qt { width: 100%; border-collapse: collapse; margin-top: 8px; }
.iq-qt th { font-family: 'IBM Plex Mono', monospace; font-size: 8px; font-weight: 500; color: #4A6378; text-transform: uppercase; letter-spacing: .12em; padding: 5px 0; border-bottom: 2px solid #1A2A47; text-align: left; }
.iq-qt td { padding: 9px 0; border-bottom: 1px solid #C7A270; vertical-align: top; }
.iq-qt tr:last-child td { border-bottom: none; }
.iq-ql { font-family: 'IBM Plex Sans Condensed', sans-serif; font-size: 13px; font-weight: 700; color: #1A2A47; }
.iq-qn { font-family: 'IBM Plex Mono', monospace; font-size: 8px; color: #6B4E5C; margin-top: 2px; }
.iq-qp { font-family: 'IBM Plex Mono', monospace; font-size: 17px; font-weight: 500; text-align: right; }
.iq-qa { font-family: 'IBM Plex Mono', monospace; font-size: 8px; letter-spacing: .06em; text-align: right; padding-top: 2px; }

.c-red { color: #B22234; }
.c-olive { color: #7B8B3C; }
.c-plum { color: #6B4E5C; }
.c-slate { color: #4A6378; }
.c-sage { color: #6B8068; }
.c-tan { color: #C7A270; }

.iq-context { font-family: 'IBM Plex Sans Condensed', sans-serif; font-size: 13px; line-height: 1.8; color: #2C3E5C; border-top: 2px solid #1A2A47; padding-top: 12px; margin-top: 22px; }
.iq-formula { background: #1A2A47; color: #F4EFE6; padding: 2px 8px; font-size: 11px; font-family: 'IBM Plex Mono', monospace; }

.iq-mb { margin-top: 8px; }
.iq-mr { display: flex; align-items: center; gap: 6px; padding: 8px 0; border-bottom: 1px solid #C7A270; }
.iq-mr:first-child { border-top: 2px solid #1A2A47; }
.iq-mrk { font-family: 'IBM Plex Mono', monospace; font-size: 10px; color: #C7A270; min-width: 14px; font-weight: 500; }
.iq-mnm { font-family: 'IBM Plex Sans Condensed', sans-serif; font-size: 12px; font-weight: 600; flex: 1; color: #1A2A47; min-width: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.iq-mbg { width: 40px; position: relative; height: 10px; flex-shrink: 0; }
.iq-mbg2 { height: 2px; background: #ECE5D7; margin-top: 4px; }
.iq-mbb { height: 2px; background: #B22234; position: absolute; top: 4px; left: 0; }
.iq-mv { font-family: 'IBM Plex Mono', monospace; font-size: 11px; font-weight: 600; min-width: 38px; text-align: right; color: #1A2A47; }
.iq-ms { font-family: 'IBM Plex Mono', monospace; font-size: 9px; color: #6B4E5C; min-width: 44px; text-align: right; }
.iq-mc2 { font-family: 'IBM Plex Mono', monospace; font-size: 8px; background: #B22234; color: #F4EFE6; padding: 1px 5px; letter-spacing: .04em; }

.iq-ag { display: grid; grid-template-columns: 1fr 1fr; gap: 0; border-top: 2px solid #1A2A47; margin-top: 8px; }
.iq-ai { display: flex; justify-content: space-between; align-items: center; padding: 7px 0; border-bottom: 1px solid #C7A270; font-family: 'IBM Plex Mono', monospace; font-size: 9px; }
.iq-ai:nth-child(odd) { padding-right: 12px; }
.iq-ai:nth-child(even) { padding-left: 12px; border-left: 1px solid #C7A270; }
.iq-ao { color: #6B8068; font-weight: 500; }
.iq-am { color: #B22234; font-weight: 500; }

.iq-fn { padding: 13px 0; border-bottom: 1px solid #C7A270; }
.iq-fn:first-child { border-top: 2px solid #1A2A47; }
.iq-fb { font-family: 'Playfair Display', serif; font-size: 34px; font-weight: 900; line-height: 1; color: #1A2A47; }
.iq-fb.red { color: #B22234; }
.iq-fb.olive { color: #7B8B3C; }
.iq-fb.sage { color: #6B8068; }
.iq-fh { font-family: 'IBM Plex Sans Condensed', sans-serif; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: .1em; color: #4A6378; margin-top: 2px; }
.iq-fd { font-family: 'IBM Plex Sans Condensed', sans-serif; font-size: 11px; color: #2C3E5C; margin-top: 5px; line-height: 1.6; border-left: 2px solid #C7A270; padding-left: 10px; }

.iq-cf { border-top: 1px solid #C7A270; padding: 12px 0 0; display: flex; justify-content: space-between; font-family: 'IBM Plex Mono', monospace; font-size: 9px; color: #6B4E5C; letter-spacing: .07em; margin-top: 28px; flex-wrap: wrap; gap: 8px; }

@media (max-width: 1300px) {
.iq-mn { font-size: 56px; }
.iq-mt, .iq-mc, .iq-mk { padding-left: 40px; padding-right: 40px; }
.iq-rule { margin-left: 40px; margin-right: 40px; }
.iq-body { padding: 28px 40px; }
.iq-lead { grid-template-columns: 1fr 1fr; }
.iq-ls { border-bottom: 1px solid #C7A270; }
.iq-ls:nth-child(2) { border-right: none; }
.iq-ls:nth-child(3), .iq-ls:nth-child(4) { padding-top: 18px; border-bottom: none; }
.iq-g3 { grid-template-columns: 1fr; }
.iq-dv { height: 1px; margin: 24px 0; }
.iq-col { padding: 0; }
.iq-pages { grid-template-columns: repeat(2, 1fr); }
.iq-pi:nth-child(1), .iq-pi:nth-child(2) { border-bottom: 1px solid #C7A270; }
.iq-pi:nth-child(2) { border-right: none; }
}
@media (max-width: 700px) {
.iq-mn { font-size: 42px; }
.iq-mtag { font-size: 11px; letter-spacing: .15em; }
.iq-mt, .iq-mc, .iq-mk { padding-left: 22px; padding-right: 22px; }
.iq-rule { margin-left: 22px; margin-right: 22px; }
.iq-body { padding: 22px 22px; }
.iq-lead { grid-template-columns: 1fr; }
.iq-ls { border-right: none; border-bottom: 1px solid #C7A270; padding: 14px 0; }
.iq-ls:last-child { border-bottom: none; }
.iq-pages { grid-template-columns: 1fr; }
.iq-pi { border-right: none; border-bottom: 1px solid #C7A270; }
.iq-pi:last-child { border-bottom: none; }
.iq-cf { flex-direction: column; align-items: flex-start; }
}
</style>
""", unsafe_allow_html=True)


# ── HELPERS ──
def load_qini():
    fp = os.path.join(MODELS_DIR, 'final_qini_pool_cv.csv')
    if os.path.exists(fp):
        df = pd.read_csv(fp).sort_values('Qini_mean', ascending=False)
        return [(r['Model'], r['Qini_mean'], r['Qini_std']) for _, r in df.iterrows()]
    return [('CausalForest', 0.1502, 0.0993), ('S-Learner', 0.1237, 0.0754),
            ('T-Learner', 0.0949, 0.0323), ('UpliftRF', 0.0709, 0.0742),
            ('X-Learner', 0.0594, 0.0590), ('DR-Learner', 0.0499, 0.0893)]

ARTS = {'CausalForest model': 'cf_final.pkl', 'X-Learner backup': 'xlearner_final.pkl',
        'Response model': 'response_model.pkl', 'Test + quadrant': 'test_quadrant_FINAL.parquet',
        'Qini results': 'final_qini_pool_cv.csv', 'Policy comparison': 'policy_comparison_FINAL.csv',
        'Thresholds': 'classify_thresholds.csv', 'Persona profile': 'persona_detailed.csv'}

def build_art_html():
    out = ''
    for lbl, fn in ARTS.items():
        fp = os.path.join(MODELS_DIR, fn)
        ok = os.path.exists(fp)
        cls = 'iq-ao' if ok else 'iq-am'
        mk = '✓' if ok else '✗'
        if ok:
            b = os.path.getsize(fp)
            sz = f'{b/1024:.0f}K' if b < 1e6 else f'{b/1e6:.1f}M'
        else:
            sz = 'thiếu'
        out += f'<div class="iq-ai"><span class="{cls}">{mk} {lbl}</span><span class="{cls}">{sz}</span></div>'
    return out

def build_model_html():
    models = load_qini()
    max_q = max(m[1] for m in models)
    out = ''
    for i, (name, mean, std) in enumerate(models):
        champ = ' <span class="iq-mc2">CHAMP</span>' if i == 0 else ''
        pct = mean / max_q * 100
        out += f'<div class="iq-mr"><div class="iq-mrk">{i+1}</div><div class="iq-mnm">{name}{champ}</div><div class="iq-mbg"><div class="iq-mbg2"></div><div class="iq-mbb" style="width:{pct:.0f}%"></div></div><div class="iq-mv">{mean:.4f}</div><div class="iq-ms">±{std:.4f}</div></div>'
    return out


# ── MASTHEAD ──
today = date.today().strftime('%d.%m.%Y')

st.markdown(f"""
<div class="iq-mast">
<div class="iq-mt">
<span>KhAI THÁC DỮ LIỆU VÀ ỨNG DỤNG · ĐHSP TP.HCM · 2026</span>
<span>CAUSAL INFERENCE &amp; UPLIFT MODELING</span>
</div>
<div class="iq-mc">
<div class="iq-mn">Uplift<em>IQ</em></div>
<div class="iq-mtag">Hệ thống phân tích chiến dịch email · Email Campaign Intelligence</div>
</div>
<div class="iq-rule"></div>
<div class="iq-mk">
<span>GV HƯỚNG DẪN: TS. Huỳnh Lê Tấn Tài</span>
<span>▲ 6 MÔ HÌNH · HILLSTROM · 57,557 KHÁCH HÀNG</span>
<span>CHAMPION: CAUSALFOREST DML (ECONML)</span>
</div>
</div>
""", unsafe_allow_html=True)


# ── BODY — GỘP TẤT CẢ VÀO 1 ST.MARKDOWN ──
art_html = build_art_html()
model_html = build_model_html()

body_html = f"""
<div class="iq-body">

<div class="iq-rub">Kết quả nghiên cứu</div>
<div class="iq-lead">
<div class="iq-ls">
<div class="v red">0.150</div>
<div class="l">Qini Score Champion · CausalForest DML</div>
<div class="s">Pool 5-fold CV · 57,557 mẫu · 627 events</div>
</div>
<div class="iq-ls" style="padding-left:20px">
<div class="v sm sage">+1.98×</div>
<div class="l">Lift top 10% Mens Email</div>
<div class="s">Conv 3.40% vs avg 1.52%</div>
</div>
<div class="iq-ls" style="padding-left:20px">
<div class="v sm sage">+30.2%</div>
<div class="l">Profit vs No-treatment</div>
<div class="s">IPS estimator · test set</div>
</div>
<div class="iq-ls" style="padding-left:20px">
<div class="v sm">1,859</div>
<div class="l">VND/user · Uplift Policy v2</div>
<div class="s">vs 1,320 không gửi ai</div>
</div>
</div>

<div class="iq-pages">
<a class="iq-pi" href="/Single_Predict" target="_self">
<div class="n">01</div>
<div class="t">Single Predict</div>
<div class="d">Nhập 1 khách, nhận CATE + recommendation</div>
<div class="f">1_SINGLE_PREDICT.PY</div>
</a>
<a class="iq-pi" href="/Batch_Upload" target="_self">
<div class="n">02</div>
<div class="t">Batch Upload</div>
<div class="d">Upload CSV, batch scoring, download</div>
<div class="f">2_BATCH_UPLOAD.PY</div>
</a>
<a class="iq-pi" href="/Economic_Simulator" target="_self">
<div class="n">03</div>
<div class="t">Economic Sim</div>
<div class="d">Điều chỉnh cost/profit, profit curve</div>
<div class="f">3_ECONOMIC_SIM.PY</div>
</a>
<a class="iq-pi" href="/Persona_Explorer" target="_self">
<div class="n">04</div>
<div class="t">Persona</div>
<div class="d">Khám phá 4 nhóm, SHAP, filter</div>
<div class="f">4_PERSONA.PY</div>
</a>
</div>

<div class="iq-g3">
<div class="iq-col">
<div class="iq-rub">Phân loại khách hàng</div>
<table class="iq-qt">
<tr><th>Nhóm</th><th style="text-align:right">Tỷ lệ</th><th style="text-align:right">Hành động</th></tr>
<tr><td><div class="iq-ql">Persuadable</div><div class="iq-qn">2,063 · Uplift cao + Response thấp</div></td><td><div class="iq-qp c-red">23.9%</div></td><td><div class="iq-qa c-red">GỬI EMAIL</div></td></tr>
<tr><td><div class="iq-ql">Sure Thing</div><div class="iq-qn">2,474 · Tự mua không cần email</div></td><td><div class="iq-qp c-tan">28.7%</div></td><td><div class="iq-qa c-tan">KHÔNG GỬI</div></td></tr>
<tr><td><div class="iq-ql">Sleeping Dog</div><div class="iq-qn">2,268 · Email phản tác dụng</div></td><td><div class="iq-qp c-red">26.3%</div></td><td><div class="iq-qa c-red">TUYỆT ĐỐI KHÔNG</div></td></tr>
<tr><td><div class="iq-ql">Lost Cause</div><div class="iq-qn">1,829 · Không phản hồi</div></td><td><div class="iq-qp c-slate">21.2%</div></td><td><div class="iq-qa c-slate">BỎ QUA</div></td></tr>
</table>
<div class="iq-rub" style="margin-top:22px">Bài toán</div>
<p class="iq-context"><strong>Response model thông thường</strong> dự đoán ai sẽ mua nhưng không phân biệt được liệu email có <em>gây ra</em> việc mua hay không.<br><br>Uplift Modeling ước lượng <span class="iq-formula">CATE = E[Y(1)−Y(0)|X]</span> — phần gia tăng conversion rate khi gửi email cho từng cá nhân.</p>
</div>
<div class="iq-dv"></div>
<div class="iq-col">
<div class="iq-rub">Bảng xếp hạng mô hình · Pool-CV</div>
<div class="iq-mb">{model_html}</div>
<p style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:#6B4E5C;margin-top:6px;text-align:right">5-fold · 57,557 mẫu · 627 events</p>
<div class="iq-rub" style="margin-top:22px">Artifact files · ./models/</div>
<div class="iq-ag">{art_html}</div>
<p style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:#6B4E5C;margin-top:5px">Copy từ MyDrive/uplift/artifacts/</p>
</div>
<div class="iq-dv"></div>
<div class="iq-col">
<div class="iq-rub">Phát hiện chính</div>
<div class="iq-fn">
<div class="iq-fb sage">+1.98×</div>
<div class="iq-fh">Lift top 10% Mens Email</div>
<div class="iq-fd">CausalForest xếp đúng top 10% có conv rate 3.40% — gấp 2.23× ATE tổng thể +0.86%.</div>
</div>
<div class="iq-fn">
<div class="iq-fb red">−0.44%</div>
<div class="iq-fh">Womens Top 10% — Uplift Âm</div>
<div class="iq-fd">Tất cả 6 models thất bại xếp hạng Womens email ở top 10%. ATE Womens (+0.38%) quá thấp.</div>
</div>
<div class="iq-fn">
<div class="iq-fb olive">+80.5%</div>
<div class="iq-fh">Multichannel → Persuadable</div>
<div class="iq-fd">Khách đa kênh nhiều hơn 80.5% trong nhóm Persuadable — feature nhận diện quan trọng nhất.</div>
</div>
<div class="iq-fn">
<div class="iq-fb">1,659</div>
<div class="iq-fh">Người CATE Âm — T-Learner</div>
<div class="iq-fd">T-Learner xác nhận 1,659 khách min uplift &lt; 0 — căn cứ phân loại Sleeping Dog.</div>
</div>
</div>
</div>

<div class="iq-cf">
<span>©2026 UPLIFTIQ - Khai thác dữ liệu và ứng dụng </span>
<span>KÜNZEL 2019 · ATHEY &amp; WAGER 2019 · HILLSTROM 2008</span>
<span>STREAMLIT · CAUSALML · ECONML · LIGHTGBM</span>
</div>

</div>
"""
st.markdown(body_html, unsafe_allow_html=True)


# ── SIDEBAR ──
with st.sidebar:
    # Logo + Navigation label
    st.markdown("""
<div style="font-family:'Playfair Display',serif;font-size:24px;font-weight:900;color:#F4EFE6;letter-spacing:-0.5px;padding:8px 0 2px">Uplift<span style="color:#B22234">IQ</span></div>
<div style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:#C7A270;text-transform:uppercase;letter-spacing:.2em;margin-bottom:14px;border-bottom:1px solid #2C3E5C;padding-bottom:10px">Navigation</div>
""", unsafe_allow_html=True)

    # Navigation links — Streamlit tự thêm aria-current="page" cho trang hiện tại
    nav_pages = [
        ('app.py', '00 · TRANG CHỦ'),
        ('pages/1_🎯_Single_Predict.py', '01 · SINGLE PREDICT'),
        ('pages/2_📊_Batch_Upload.py', '02 · BATCH UPLOAD'),
        ('pages/3_💰_Economic_Simulator.py', '03 · ECONOMIC SIM'),
        ('pages/4_👥_Persona_Explorer.py', '04 · PERSONA EXPLORER'),
        ('pages/5_📖_Gioi_Thieu_Do_An.py', '05 · GIỚI THIỆU ĐỒ ÁN'),
    ]
    for page_path, label in nav_pages:
        st.page_link(page_path, label=label)

    # Champion + meta info
    st.markdown("""
<div style="border-top:1px solid #2C3E5C;margin-top:18px;padding-top:14px;font-family:'IBM Plex Mono',monospace;font-size:9px;color:#C7A270;line-height:2">
<div style="color:#B22234;font-weight:600">▲ CHAMPION MODEL</div>
<div style="color:#F4EFE6">CausalForest DML</div>
<div>Qini 0.150 ± 0.099</div>
<div>Pool-CV 5-fold</div>
</div>
<div style="border-top:1px solid #2C3E5C;margin-top:18px;padding-top:14px;font-family:'IBM Plex Mono',monospace;font-size:9px;color:#C7A270;line-height:2">
<div>GVHD: TS. Huỳnh Lê Tấn Tài</div>
<div>ĐHSP TP.HCM · 2026</div>
</div>
<div style="border-top:1px solid #2C3E5C;margin-top:18px;padding-top:14px;font-family:'IBM Plex Mono',monospace;font-size:9px;color:#C7A270;line-height:2">
<div>Thành viên thực hiện</div>
<div>Tăng Ngọc Phụng - KHMT836027</div>
<div>Hoàng Châu Ngọc Phương - KHMT836028</div>
<div>Lê Thị Mai Len - KHMT836015</div>
</div>
""", unsafe_allow_html=True)
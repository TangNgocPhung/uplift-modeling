"""
Editorial design system v4 — shared CSS + components cho các trang phụ.

Sử dụng:
    from utils.editorial import inject_css, render_masthead, render_sidebar_header

    inject_css()                      # gọi 1 lần đầu page
    render_masthead(2, 'Batch Upload', 'Batch scoring', 'danh sách khách hàng',
                    'Upload CSV → score → download')
    with st.sidebar:
        render_sidebar_header(active_idx=2)
        ... custom widgets ...
"""
import streamlit as st


FONT_LINK = (
    '<link href="https://fonts.googleapis.com/css2?'
    'family=Playfair+Display:ital,wght@0,700;0,900;1,700&'
    'family=IBM+Plex+Mono:wght@300;400;500&'
    'family=IBM+Plex+Sans+Condensed:wght@300;400;600;700'
    '&display=swap" rel="stylesheet">'
)


CSS_BASE = """
<style>
/* ── Palette ── */
.stApp { background: #F4EFE6; color: #1A2A47; font-family: 'IBM Plex Sans Condensed', sans-serif; }

/* Ẩn các UI Streamlit không cần — KHÔNG ẩn <header> vì chứa nút toggle sidebar */
#MainMenu, footer, [data-testid="stToolbar"], .stDeployButton { display: none !important; }
[data-testid="stHeader"] { background: transparent !important; z-index: 999998 !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] { background: #1A2A47 !important; border-right: 4px solid #B22234 !important; }
[data-testid="stSidebar"] * { color: #F4EFE6 !important; }
[data-testid="stSidebarNav"], [data-testid="stSidebarNavItems"], [data-testid="stSidebarNavSeparator"], [data-testid="stSidebarNavLinkContainer"] { display: none !important; }
[data-testid="stSidebarNav"] ul, [data-testid="stSidebarNav"] hr { display: none !important; }

/* Đảm bảo nút toggle sidebar luôn click được */
[data-testid="stSidebarCollapsedControl"],
[data-testid="stSidebarCollapseButton"],
button[kind="header"] { z-index: 999999 !important; pointer-events: auto !important; }
[data-testid="stSidebarCollapsedControl"] svg { color: #1A2A47 !important; fill: #1A2A47 !important; }

/* ── Nav links: st.page_link styled editorial ── */
.iq-nav-link { display:block; text-decoration:none !important; border-left:2px solid transparent;
    padding:4px 0 4px 10px; margin-bottom:4px;
    color:#C7A270 !important; font-family:'IBM Plex Sans Condensed',sans-serif;
    font-size:11px; transition: all .15s ease; }
.iq-nav-link:hover { border-left-color:#B22234; color:#F4EFE6 !important; background:rgba(178,34,52,0.08); }
.iq-nav-link.active { border-left-color:#B22234; color:#F4EFE6 !important; font-weight:700; }

/* ═══════════════════════════════════════════════════════════════
   Sidebar nav: compress khoảng cách st.page_link
   ═══════════════════════════════════════════════════════════════ */

/* (1) Triệt tiêu margin-bottom + gap của container Streamlit chứa stPageLink */
[data-testid="stSidebar"] [data-testid="stElementContainer"]:has([data-testid="stPageLink"]) {
    margin: 0 !important;
    padding: 0 !important;
    min-height: 0 !important;
}

/* (2) Triệt tiêu gap giữa các stElementContainer chứa nav (target FlexContainer) */
[data-testid="stSidebar"] [data-testid="stVerticalBlock"]:has([data-testid="stPageLink"]) {
    gap: 0 !important;
}

/* (3) st.page_link bản thân — nén padding, font editorial */
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

/* (4) Override các span/p/div con bên trong page_link */
[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"] *,
[data-testid="stSidebar"] [data-testid="stPageLink"] a * {
    color: inherit !important;
    font-family: 'IBM Plex Sans Condensed', sans-serif !important;
    font-size: 11px !important;
    line-height: 1.3 !important;
    margin: 0 !important;
    padding: 0 !important;
    background: transparent !important;
}

/* (5) ACTIVE state — Streamlit tự thêm aria-current="page" cho trang hiện tại */
[data-testid="stSidebar"] a[aria-current="page"],
[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"] {
    border-left-color: #B22234 !important;
    color: #F4EFE6 !important;
    font-weight: 700 !important;
    background: rgba(178,34,52,0.05) !important;
}
[data-testid="stSidebar"] a[aria-current="page"] *,
[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"] * {
    color: #F4EFE6 !important;
    font-weight: 700 !important;
}

/* (6) HOVER state */
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

/* (7) Ẩn icon mặc định của st.page_link (chỉ giữ text label) */
[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"] [data-testid="stIconMaterial"],
[data-testid="stSidebar"] [data-testid="stPageLink"] svg,
[data-testid="stSidebar"] [data-testid="stPageLink"] [data-testid*="Icon"] {
    display: none !important;
}

/* ── Block container ── */
.block-container { padding: 0 80px !important; max-width: 100% !important; }

/* ── Mini-masthead (page header) ── */
.iq-ph { background: #1A2A47; color: #F4EFE6; padding: 22px 80px 22px;
    border-bottom: 4px solid #B22234; margin: 0 -80px 0 -80px; }
.iq-ph-top { display: flex; justify-content: space-between; font-family: 'IBM Plex Mono', monospace;
    font-size: 10px; color: #C7A270; letter-spacing: .15em; text-transform: uppercase;
    margin-bottom: 10px; flex-wrap: wrap; gap: 6px; }
.iq-ph-back { color: #C7A270 !important; text-decoration: none !important; }
.iq-ph-back:hover { color: #F4EFE6 !important; }
.iq-ph-title { font-family: 'Playfair Display', serif; font-size: 44px; font-weight: 900;
    line-height: 1.05; letter-spacing: -1px; }
.iq-ph-title em { color: #B22234; font-style: normal; }
.iq-ph-sub { font-family: 'IBM Plex Sans Condensed', sans-serif; font-size: 13px; color: #C7A270;
    margin-top: 6px; letter-spacing: .15em; text-transform: uppercase; }

/* ── Body ── */
.iq-body { padding: 36px 0 24px 0; background: #F4EFE6; }

.iq-rub { font-family: 'IBM Plex Mono', monospace; font-size: 9px; font-weight: 500;
    letter-spacing: .25em; text-transform: uppercase; color: #B22234;
    margin-bottom: 8px; padding-top: 8px; border-top: 2px solid #1A2A47; }
.iq-section-hd { font-family: 'Playfair Display', serif; font-size: 24px; font-weight: 700;
    color: #1A2A47; margin-bottom: 4px; }
.iq-section-desc { font-family: 'IBM Plex Sans Condensed', sans-serif; font-size: 12px;
    color: #4A6378; margin-bottom: 14px; line-height: 1.6; }
.iq-col-title { font-family: 'IBM Plex Sans Condensed', sans-serif; font-size: 11px;
    font-weight: 700; text-transform: uppercase; color: #B22234; letter-spacing: .12em;
    margin-bottom: 8px; border-bottom: 1px solid #C7A270; padding-bottom: 4px; }

/* ── Widget restyle (slider / number_input / radio / select / multiselect) ── */
.stSlider label, .stNumberInput label, .stRadio label, .stSelectbox label,
.stMultiSelect label, .stTextInput label, .stFileUploader label, .stCheckbox label {
    color: #1A2A47 !important; font-family: 'IBM Plex Sans Condensed', sans-serif !important;
    font-size: 12px !important; font-weight: 600 !important; }
.stSlider [data-baseweb="slider"] > div > div { background: #C7A270 !important; }
.stSlider [data-baseweb="slider"] [role="slider"] { background: #B22234 !important; border-color: #B22234 !important; }
.stRadio label[data-baseweb="radio"] { color: #1A2A47 !important; }
.stSelectbox div[data-baseweb="select"],
.stMultiSelect div[data-baseweb="select"] { border-color: #C7A270 !important; background: #FBF8F2 !important; }
.stNumberInput input, .stTextInput input { background: #FBF8F2 !important; border-color: #C7A270 !important;
    color: #1A2A47 !important; font-family: 'IBM Plex Mono', monospace !important; }

/* Sidebar widgets — invert label color cho hợp nền tối */
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] .stNumberInput label,
[data-testid="stSidebar"] .stRadio label,
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label,
[data-testid="stSidebar"] .stTextInput label,
[data-testid="stSidebar"] .stCheckbox label,
[data-testid="stSidebar"] .stCheckbox label p { color: #C7A270 !important; }
[data-testid="stSidebar"] .stNumberInput input,
[data-testid="stSidebar"] .stTextInput input { background: #2C3E5C !important; border-color: #4A6378 !important;
    color: #F4EFE6 !important; }

/* ── Buttons ── */
div.stButton > button, div.stDownloadButton > button {
    background: #1A2A47 !important; color: #F4EFE6 !important;
    border: none !important; border-radius: 0 !important;
    padding: 12px 24px !important;
    font-family: 'IBM Plex Sans Condensed', sans-serif !important;
    font-size: 14px !important; font-weight: 700 !important;
    text-transform: uppercase !important; letter-spacing: .12em !important;
    box-shadow: 4px 4px 0 #B22234 !important;
    transition: all .15s ease !important;
}
div.stButton > button:hover, div.stDownloadButton > button:hover {
    background: #B22234 !important; color: #F4EFE6 !important;
    transform: translate(2px, 2px) !important;
    box-shadow: 2px 2px 0 #1A2A47 !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] { border-bottom: 3px solid #1A2A47; gap: 2px; background: transparent; }
.stTabs [data-baseweb="tab"] { background: transparent !important; border: none !important;
    border-radius: 0 !important; padding: 12px 20px !important;
    font-family: 'IBM Plex Sans Condensed', sans-serif !important;
    font-size: 12px !important; font-weight: 700 !important;
    text-transform: uppercase !important; letter-spacing: .12em !important;
    color: #4A6378 !important; }
.stTabs [data-baseweb="tab"][aria-selected="true"] { color: #B22234 !important;
    background: #FBF8F2 !important; border-bottom: 3px solid #B22234 !important; margin-bottom: -3px; }
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }
.stTabs [data-baseweb="tab-panel"] { padding-top: 24px; }

/* ── Expander ── */
.streamlit-expanderHeader, [data-testid="stExpander"] summary {
    background: #FBF8F2 !important; border: 1px solid #C7A270 !important; border-radius: 0 !important;
    font-family: 'IBM Plex Sans Condensed', sans-serif !important; font-weight: 600 !important;
    color: #1A2A47 !important; font-size: 12px !important; text-transform: uppercase;
    letter-spacing: .08em; }
[data-testid="stExpander"] { border: none !important; }

/* ── Detail table ── */
.iq-dt { width: 100%; border-collapse: collapse; margin-top: 12px; }
.iq-dt th { font-family: 'IBM Plex Mono', monospace; font-size: 9px; font-weight: 500;
    color: #4A6378; text-transform: uppercase; letter-spacing: .12em; padding: 8px 12px;
    border-bottom: 2px solid #1A2A47; text-align: left; background: #ECE5D7; }
.iq-dt td { padding: 10px 12px; border-bottom: 1px solid #C7A270;
    font-family: 'IBM Plex Sans Condensed', sans-serif; font-size: 12px; color: #1A2A47; }
.iq-dt td.num { font-family: 'IBM Plex Mono', monospace; text-align: right; }
.iq-dt tr.highlight { background: #FBF8F2; }
.iq-dt tr.highlight td { font-weight: 700; }

/* ── Streamlit dataframe restyle ── */
[data-testid="stDataFrame"] { border: 1px solid #C7A270; }

/* ── Status banners (success/info/warning/error) ── */
.iq-banner { padding: 14px 22px; margin: 12px 0; border-left: 4px solid #1A2A47;
    background: #FBF8F2; font-family: 'IBM Plex Sans Condensed', sans-serif;
    font-size: 13px; color: #1A2A47; line-height: 1.6; }
.iq-banner.success { border-left-color: #6B8068; }
.iq-banner.info { border-left-color: #4A6378; }
.iq-banner.warning { border-left-color: #C7A270; }
.iq-banner.error { border-left-color: #B22234; }
.iq-banner b, .iq-banner strong { color: #1A2A47; font-weight: 700; }
.iq-banner code { background: #1A2A47; color: #F4EFE6; padding: 1px 6px;
    font-family: 'IBM Plex Mono', monospace; font-size: 11px; }

/* ── Lead metrics (replacement cho st.metric) ── */
.iq-lead { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0;
    border-top: 3px solid #1A2A47; border-bottom: 1px solid #C7A270; margin: 12px 0 24px; }
.iq-lead.cols3 { grid-template-columns: repeat(3, 1fr); }
.iq-lead.cols2 { grid-template-columns: repeat(2, 1fr); }
.iq-ls { padding: 16px 22px 16px 0; border-right: 1px solid #C7A270; }
.iq-ls:last-child { border-right: none; padding-right: 0; }
.iq-ls:not(:first-child) { padding-left: 22px; }
.iq-ls .v { font-family: 'Playfair Display', serif; font-size: 36px; font-weight: 900;
    line-height: 1; color: #1A2A47; }
.iq-ls .v.red { color: #B22234; } .iq-ls .v.sage { color: #6B8068; } .iq-ls .v.tan { color: #C7A270; }
.iq-ls .v.sm { font-size: 26px; }
.iq-ls .l { font-family: 'IBM Plex Sans Condensed', sans-serif; font-size: 11px;
    color: #4A6378; margin-top: 4px; text-transform: uppercase; letter-spacing: .1em;
    line-height: 1.4; font-weight: 600; }
.iq-ls .s { font-family: 'IBM Plex Mono', monospace; font-size: 9px; color: #8C7B6B; margin-top: 3px; }

/* ── Empty state ── */
.iq-empty { background: #FBF8F2; border: 2px dashed #C7A270; padding: 40px; text-align: center; }
.iq-empty .icon { font-family: 'Playfair Display', serif; font-size: 64px; color: #C7A270; line-height: 1; }
.iq-empty .text { font-family: 'IBM Plex Sans Condensed', sans-serif; font-size: 14px;
    color: #4A6378; margin-top: 12px; }

/* ── Quadrant card (dùng ở Persona) ── */
.iq-quadrant-card { background: #FBF8F2; border-left: 6px solid #B22234; padding: 22px 28px;
    margin: 8px 0; }
.iq-q-name { font-family: 'Playfair Display', serif; font-size: 28px; font-weight: 900;
    line-height: 1; color: #1A2A47; }
.iq-q-rec { font-family: 'IBM Plex Sans Condensed', sans-serif; font-size: 12px;
    color: #4A6378; margin-top: 6px; line-height: 1.6; }
.iq-q-meta { font-family: 'IBM Plex Mono', monospace; font-size: 10px; color: #8C7B6B;
    margin-top: 10px; padding-top: 8px; border-top: 1px solid #C7A270; letter-spacing: .05em; }

/* ── Insight card (dùng ở Economic) ── */
.iq-insight { background: #1A2A47; color: #F4EFE6; padding: 18px 24px; margin: 14px 0;
    border-left: 4px solid #C7A270; font-family: 'IBM Plex Sans Condensed', sans-serif;
    font-size: 13px; line-height: 1.7; }
.iq-insight b, .iq-insight strong { color: #C7A270; }

/* ── Sidebar break-even pill ── */
.iq-be-pill { margin-top: 10px; padding: 10px 14px; background: #2C3E5C; border-left: 3px solid #B22234; }
.iq-be-pill .lbl { font-family: 'IBM Plex Mono', monospace; font-size: 9px; color: #C7A270;
    letter-spacing: .15em; text-transform: uppercase; }
.iq-be-pill .val { font-family: 'IBM Plex Mono', monospace; font-size: 18px; color: #F4EFE6; margin-top: 2px; }
.iq-be-pill .note { font-family: 'IBM Plex Sans Condensed', sans-serif; font-size: 10px;
    color: #C7A270; margin-top: 4px; line-height: 1.4; }

.iq-sb-section { border-top: 1px solid #2C3E5C; margin-top: 18px; padding-top: 14px;
    font-family: 'IBM Plex Mono', monospace; font-size: 9px; color: #C7A270;
    letter-spacing: .15em; text-transform: uppercase; margin-bottom: 8px; }
</style>
"""


# Năm trang phụ. Index 0 = trang chủ.
# Dùng đường dẫn file thực (st.page_link API) thay vì URL slug để Streamlit
# tự handle URL routing — emoji + dấu gạch dưới trong filename không bị lỗi.
NAV_ITEMS = [
    ('app.py', '00 · TRANG CHỦ'),
    ('pages/1_🎯_Single_Predict.py', '01 · SINGLE PREDICT'),
    ('pages/2_📊_Batch_Upload.py', '02 · BATCH UPLOAD'),
    ('pages/3_💰_Economic_Simulator.py', '03 · ECONOMIC SIM'),
    ('pages/4_👥_Persona_Explorer.py', '04 · PERSONA EXPLORER'),
    ('pages/5_📖_Gioi_Thieu_Do_An.py', '05 · GIỚI THIỆU ĐỒ ÁN'),
]

NAV_TOTAL = 5  # tổng số trang phụ (không tính trang chủ)


def inject_css(extra: str = '') -> None:
    """Gọi 1 lần đầu mỗi page để chèn font + base CSS. `extra` là CSS riêng cho trang."""
    st.markdown(FONT_LINK, unsafe_allow_html=True)
    st.markdown(CSS_BASE, unsafe_allow_html=True)
    if extra:
        st.markdown(f'<style>{extra}</style>', unsafe_allow_html=True)


def render_masthead(page_num: int, page_label: str,
                    title_main: str, title_em: str,
                    subtitle: str) -> None:
    """Mini-masthead navy ở đầu trang phụ."""
    st.markdown(f"""
<div class="iq-ph">
<div class="iq-ph-top">
<a class="iq-ph-back" href="/" target="_self">← UpliftIQ Home</a>
<span>TRANG {page_num:02d} / {NAV_TOTAL:02d}</span>
<span>{page_label}</span>
</div>
<div class="iq-ph-title">{title_main} <em>{title_em}</em></div>
<div class="iq-ph-sub">{subtitle}</div>
</div>
""", unsafe_allow_html=True)


def render_sidebar_header(active_idx: int = 0) -> None:
    """Logo + navigation cho sidebar.

    Dùng st.page_link() — Streamlit tự thêm aria-current="page" cho trang hiện tại,
    CSS tự detect active state mà không cần wrapper class.
    Tham số `active_idx` giữ lại cho backward compat nhưng không dùng nữa.
    """
    # Logo + Navigation label
    st.markdown("""
<div style="font-family:'Playfair Display',serif;font-size:22px;font-weight:900;color:#F4EFE6;letter-spacing:-0.5px;padding:8px 0 2px">Uplift<span style="color:#B22234">IQ</span></div>
<div style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:#C7A270;text-transform:uppercase;letter-spacing:.2em;margin-bottom:8px;border-bottom:1px solid #2C3E5C;padding-bottom:8px">Navigation</div>
""", unsafe_allow_html=True)

    # Render page links — Streamlit tự xử lý active state
    for page_path, label in NAV_ITEMS:
        st.page_link(page_path, label=label)

    # Divider dưới nav
    st.markdown('<div style="border-bottom:1px solid #2C3E5C;margin:10px 0 12px"></div>',
                unsafe_allow_html=True)


def render_break_even(threshold: float, note: str = 'Chỉ gửi email nếu uplift dự đoán > ngưỡng này') -> None:
    """Pill hiển thị break-even threshold trong sidebar."""
    st.markdown(f"""
<div class="iq-be-pill">
<div class="lbl">Break-even τ</div>
<div class="val">{threshold:.4f}</div>
<div class="note">{note}</div>
</div>
""", unsafe_allow_html=True)


def sidebar_section_title(title: str) -> None:
    """Sub-heading mono trong sidebar."""
    st.markdown(f'<div class="iq-sb-section">{title}</div>', unsafe_allow_html=True)


def banner(kind: str, body_html: str) -> None:
    """Render banner editorial. kind ∈ {success, info, warning, error}."""
    st.markdown(f'<div class="iq-banner {kind}">{body_html}</div>', unsafe_allow_html=True)


def section(rub: str, headline: str, desc: str = '') -> None:
    """Render rub + headline + (optional) description."""
    desc_html = f'<div class="iq-section-desc">{desc}</div>' if desc else ''
    st.markdown(f"""
<div class="iq-rub">// {rub}</div>
<div class="iq-section-hd">{headline}</div>
{desc_html}
""", unsafe_allow_html=True)


def empty_state(text_html: str, icon: str = '▲') -> None:
    st.markdown(f"""
<div class="iq-empty">
<div class="icon">{icon}</div>
<div class="text">{text_html}</div>
</div>
""", unsafe_allow_html=True)


def error_card(title: str, body_html: str) -> None:
    """Editorial error block — thay cho st.error khi cần style."""
    st.markdown(f"""
<div style="padding:32px 40px;background:#FBF8F2;border:2px solid #B22234;margin:32px 0;font-family:'IBM Plex Sans Condensed',sans-serif">
<div style="font-family:'IBM Plex Mono',monospace;font-size:10px;color:#B22234;letter-spacing:.2em;text-transform:uppercase;margin-bottom:8px">⚠ Error</div>
<div style="font-family:'Playfair Display',serif;font-size:24px;font-weight:700;color:#1A2A47;margin-bottom:10px">{title}</div>
<div style="font-size:13px;color:#4A6378;line-height:1.7">{body_html}</div>
</div>
""", unsafe_allow_html=True)

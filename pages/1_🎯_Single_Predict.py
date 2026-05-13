"""
Trang 1 — Single Predict (Editorial design v4)
Phong cách: Vietnamese Editorial / Tạp Chí Data (đồng bộ homepage)
"""
import streamlit as st
import numpy as np
import pandas as pd
from utils.load_models import (load_causal_forest, load_response_model,
                                load_classify_thresholds,
                                predict_cate, predict_response,
                                FEAT)
from utils.policy import (optimal_action, expected_profit_per_user,
                           DEFAULT_PROFIT, DEFAULT_COST,
                           QUADRANT_COLORS, QUADRANT_RECOMMENDATION,
                           quadrant_label)
from utils.plots import gauge_uplift

st.set_page_config(
    page_title='Single Predict — UpliftIQ',
    page_icon='▲',
    layout='wide',
    initial_sidebar_state='expanded',
)


# ═════════════════════════════════════════════════════════════
# FONT + CSS — đồng bộ với homepage
# ═════════════════════════════════════════════════════════════
st.markdown(
    '<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,700&family=IBM+Plex+Mono:wght@300;400;500&family=IBM+Plex+Sans+Condensed:wght@300;400;600;700&display=swap" rel="stylesheet">',
    unsafe_allow_html=True
)

st.markdown("""
<style>
.stApp { background: #F4EFE6; color: #1A2A47; font-family: 'IBM Plex Sans Condensed', sans-serif; }
#MainMenu, footer, header, [data-testid="stToolbar"], .stDeployButton { display: none !important; }

[data-testid="stSidebar"] { background: #1A2A47 !important; border-right: 4px solid #B22234 !important; }
[data-testid="stSidebar"] * { color: #F4EFE6 !important; }
[data-testid="stSidebarNav"], [data-testid="stSidebarNavItems"], [data-testid="stSidebarNavSeparator"], [data-testid="stSidebarNavLinkContainer"] { display: none !important; }
section[data-testid="stSidebar"] ul { display: none !important; }
section[data-testid="stSidebar"] [role="navigation"] { display: none !important; }
section[data-testid="stSidebar"] hr { display: none !important; }

.block-container { padding: 0 80px !important; max-width: 100% !important; }

/* Page header (mini-masthead) — dùng margin âm để breakout full width */
.iq-ph { background: #1A2A47; color: #F4EFE6; padding: 22px 80px 22px; border-bottom: 4px solid #B22234; margin: 0 -80px 0 -80px; }
.iq-ph-top { display: flex; justify-content: space-between; font-family: 'IBM Plex Mono', monospace; font-size: 10px; color: #C7A270; letter-spacing: .15em; text-transform: uppercase; margin-bottom: 10px; }
.iq-ph-back { color: #C7A270 !important; text-decoration: none !important; }
.iq-ph-back:hover { color: #F4EFE6 !important; }
.iq-ph-title { font-family: 'Playfair Display', serif; font-size: 44px; font-weight: 900; line-height: 1.05; letter-spacing: -1px; }
.iq-ph-title em { color: #B22234; font-style: normal; }
.iq-ph-sub { font-family: 'IBM Plex Sans Condensed', sans-serif; font-size: 13px; color: #C7A270; margin-top: 6px; letter-spacing: .15em; text-transform: uppercase; }

.iq-body { padding: 36px 0 24px 0; background: #F4EFE6; }

.iq-rub { font-family: 'IBM Plex Mono', monospace; font-size: 9px; font-weight: 500; letter-spacing: .25em; text-transform: uppercase; color: #B22234; margin-bottom: 8px; padding-top: 8px; border-top: 2px solid #1A2A47; }

.iq-section-hd { font-family: 'Playfair Display', serif; font-size: 24px; font-weight: 700; color: #1A2A47; margin-bottom: 4px; }
.iq-section-desc { font-family: 'IBM Plex Sans Condensed', sans-serif; font-size: 12px; color: #4A6378; margin-bottom: 14px; line-height: 1.6; }

.iq-col-title { font-family: 'IBM Plex Sans Condensed', sans-serif; font-size: 11px; font-weight: 700; text-transform: uppercase; color: #B22234; letter-spacing: .12em; margin-bottom: 8px; border-bottom: 1px solid #C7A270; padding-bottom: 4px; }

/* Streamlit widgets — restyle theo palette */
.stSlider label, .stNumberInput label, .stRadio label, .stSelectbox label, .stTextInput label { color: #1A2A47 !important; font-family: 'IBM Plex Sans Condensed', sans-serif !important; font-size: 12px !important; font-weight: 600 !important; }
.stSlider [data-baseweb="slider"] > div > div { background: #C7A270 !important; }
.stSlider [data-baseweb="slider"] [role="slider"] { background: #B22234 !important; border-color: #B22234 !important; }
.stRadio label[data-baseweb="radio"] { color: #1A2A47 !important; }
.stSelectbox div[data-baseweb="select"] { border-color: #C7A270 !important; background: #FBF8F2 !important; }
.stNumberInput input { background: #FBF8F2 !important; border-color: #C7A270 !important; color: #1A2A47 !important; font-family: 'IBM Plex Mono', monospace !important; }

/* Predict button — bold editorial */
div.stButton > button {
    background: #1A2A47 !important; color: #F4EFE6 !important;
    border: none !important; border-radius: 0 !important;
    padding: 14px 28px !important;
    font-family: 'IBM Plex Sans Condensed', sans-serif !important;
    font-size: 16px !important; font-weight: 700 !important;
    text-transform: uppercase !important; letter-spacing: .15em !important;
    box-shadow: 4px 4px 0 #B22234 !important;
    transition: all .15s ease !important;
}
div.stButton > button:hover {
    background: #B22234 !important; color: #F4EFE6 !important;
    transform: translate(2px, 2px) !important;
    box-shadow: 2px 2px 0 #1A2A47 !important;
}

/* Result cards — editorial */
.iq-result-headline { font-family: 'Playfair Display', serif; font-size: 96px; font-weight: 900; line-height: 0.95; color: #1A2A47; letter-spacing: -3px; }
.iq-result-headline.red { color: #B22234; }
.iq-result-headline.sage { color: #6B8068; }
.iq-result-headline.rust { color: #92400E; }
.iq-result-kicker { font-family: 'IBM Plex Mono', monospace; font-size: 11px; color: #B22234; letter-spacing: .25em; text-transform: uppercase; margin-bottom: 8px; }
.iq-result-sub { font-family: 'IBM Plex Sans Condensed', sans-serif; font-size: 13px; color: #4A6378; line-height: 1.6; margin-top: 8px; padding-top: 12px; border-top: 1px solid #C7A270; }

.iq-action-card { background: #FBF8F2; border: 2px solid #1A2A47; padding: 24px 28px; }
.iq-action-card.success { border-color: #6B8068; }
.iq-action-card.danger { border-color: #B22234; }
.iq-action-card.warning { border-color: #92400E; }
.iq-action-title { font-family: 'Playfair Display', serif; font-size: 28px; font-weight: 700; line-height: 1.2; margin-bottom: 12px; color: #1A2A47; }
.iq-action-title.success { color: #6B8068; }
.iq-action-title.danger { color: #B22234; }
.iq-action-body { font-family: 'IBM Plex Sans Condensed', sans-serif; font-size: 13px; line-height: 1.7; color: #2C3E5C; }
.iq-action-body strong { color: #1A2A47; }
.iq-mono { font-family: 'IBM Plex Mono', monospace; background: #1A2A47; color: #F4EFE6; padding: 2px 7px; font-size: 12px; }

.iq-quadrant-card { background: #FBF8F2; border-left: 6px solid #B22234; padding: 22px 28px; }
.iq-q-name { font-family: 'Playfair Display', serif; font-size: 36px; font-weight: 900; line-height: 1; color: #1A2A47; }
.iq-q-rec { font-family: 'IBM Plex Sans Condensed', sans-serif; font-size: 13px; color: #4A6378; margin-top: 8px; line-height: 1.6; }
.iq-q-meta { font-family: 'IBM Plex Mono', monospace; font-size: 11px; color: #8C7B6B; margin-top: 12px; padding-top: 10px; border-top: 1px solid #C7A270; letter-spacing: .05em; }

/* Detail table */
.iq-dt { width: 100%; border-collapse: collapse; margin-top: 12px; }
.iq-dt th { font-family: 'IBM Plex Mono', monospace; font-size: 9px; font-weight: 500; color: #4A6378; text-transform: uppercase; letter-spacing: .12em; padding: 8px 12px; border-bottom: 2px solid #1A2A47; text-align: left; background: #ECE5D7; }
.iq-dt td { padding: 10px 12px; border-bottom: 1px solid #C7A270; font-family: 'IBM Plex Sans Condensed', sans-serif; font-size: 12px; color: #1A2A47; }
.iq-dt td.num { font-family: 'IBM Plex Mono', monospace; text-align: right; }
.iq-dt tr.highlight { background: #FBF8F2; }
.iq-dt tr.highlight td { font-weight: 700; }

.iq-empty { background: #FBF8F2; border: 2px dashed #C7A270; padding: 40px; text-align: center; }
.iq-empty .icon { font-family: 'Playfair Display', serif; font-size: 64px; color: #C7A270; line-height: 1; }
.iq-empty .text { font-family: 'IBM Plex Sans Condensed', sans-serif; font-size: 14px; color: #4A6378; margin-top: 12px; }
</style>
""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════
# LOAD MODELS
# ═════════════════════════════════════════════════════════════
cf_model = load_causal_forest()
response_model = load_response_model()
thresholds = load_classify_thresholds()

if cf_model is None:
    st.markdown("""
<div style="padding:32px 40px;background:#FBF8F2;border:2px solid #B22234;margin:32px 0;font-family:'IBM Plex Sans Condensed',sans-serif">
<div style="font-family:'IBM Plex Mono',monospace;font-size:10px;color:#B22234;letter-spacing:.2em;text-transform:uppercase;margin-bottom:8px">⚠ Error</div>
<div style="font-family:'Playfair Display',serif;font-size:24px;font-weight:700;color:#1A2A47;margin-bottom:10px">Chưa có file mô hình</div>
<div style="font-size:13px;color:#4A6378;line-height:1.7">Vui lòng copy file <code style="background:#1A2A47;color:#F4EFE6;padding:2px 6px;font-family:'IBM Plex Mono',monospace">cf_final.pkl</code> vào thư mục <code style="background:#1A2A47;color:#F4EFE6;padding:2px 6px;font-family:'IBM Plex Mono',monospace">./models/</code> rồi reload.</div>
</div>
""", unsafe_allow_html=True)
    st.stop()


# ═════════════════════════════════════════════════════════════
# PAGE HEADER
# ═════════════════════════════════════════════════════════════
st.markdown("""
<div class="iq-ph">
<div class="iq-ph-top">
<a class="iq-ph-back" href="/" target="_self">← UpliftIQ Home</a>
<span>TRANG 01 / 04</span>
<span>SINGLE PREDICT</span>
</div>
<div class="iq-ph-title">Dự đoán cho <em>một khách hàng</em></div>
<div class="iq-ph-sub">Nhập thông tin → CausalForest dự đoán CATE → Khuyến nghị tối ưu</div>
</div>
""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════
# SIDEBAR
# ═════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
<div style="font-family:'Playfair Display',serif;font-size:22px;font-weight:900;color:#F4EFE6;letter-spacing:-0.5px;padding:8px 0 2px">Uplift<span style="color:#B22234">IQ</span></div>
<div style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:#C7A270;text-transform:uppercase;letter-spacing:.2em;margin-bottom:14px;border-bottom:1px solid #2C3E5C;padding-bottom:10px">Navigation</div>
<div style="line-height:1.4;margin-bottom:18px">
<a class="iq-nav-link" href="/" target="_self" style="display:block;text-decoration:none;border-left:2px solid transparent;padding:4px 0 4px 10px;margin-bottom:4px;color:#C7A270;font-family:'IBM Plex Sans Condensed',sans-serif;font-size:11px">00 · TRANG CHỦ</a>
<a class="iq-nav-link" href="/Single_Predict" target="_self" style="display:block;text-decoration:none;border-left:2px solid #B22234;padding:4px 0 4px 10px;margin-bottom:4px;color:#F4EFE6;font-family:'IBM Plex Sans Condensed',sans-serif;font-size:11px;font-weight:700">01 · SINGLE PREDICT</a>
<a class="iq-nav-link" href="/Batch_Upload" target="_self" style="display:block;text-decoration:none;border-left:2px solid transparent;padding:4px 0 4px 10px;margin-bottom:4px;color:#C7A270;font-family:'IBM Plex Sans Condensed',sans-serif;font-size:11px">02 · BATCH UPLOAD</a>
<a class="iq-nav-link" href="/Economic_Simulator" target="_self" style="display:block;text-decoration:none;border-left:2px solid transparent;padding:4px 0 4px 10px;margin-bottom:4px;color:#C7A270;font-family:'IBM Plex Sans Condensed',sans-serif;font-size:11px">03 · ECONOMIC SIM</a>
<a class="iq-nav-link" href="/Persona_Explorer" target="_self" style="display:block;text-decoration:none;border-left:2px solid transparent;padding:4px 0 4px 10px;color:#C7A270;font-family:'IBM Plex Sans Condensed',sans-serif;font-size:11px">04 · PERSONA EXPLORER</a>
</div>
<div style="border-top:1px solid #2C3E5C;padding-top:14px;font-family:'IBM Plex Mono',monospace;font-size:9px;color:#C7A270;letter-spacing:.1em;text-transform:uppercase;margin-bottom:10px">⚙ Tham số kinh tế</div>
""", unsafe_allow_html=True)

    profit_per_conv = st.number_input(
        'Lợi nhuận / conversion (VND)', value=DEFAULT_PROFIT,
        min_value=10_000, max_value=1_000_000, step=10_000)
    cost_per_email = st.number_input(
        'Chi phí / email (VND)', value=DEFAULT_COST,
        min_value=500, max_value=50_000, step=500)

    threshold = cost_per_email / profit_per_conv

    st.markdown(f"""
<div style="margin-top:10px;padding:10px 14px;background:#2C3E5C;border-left:3px solid #B22234">
<div style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:#C7A270;letter-spacing:.15em;text-transform:uppercase">Break-even τ</div>
<div style="font-family:'IBM Plex Mono',monospace;font-size:18px;color:#F4EFE6;margin-top:2px">{threshold:.4f}</div>
<div style="font-family:'IBM Plex Sans Condensed',sans-serif;font-size:10px;color:#C7A270;margin-top:4px;line-height:1.4">Chỉ gửi email nếu uplift dự đoán {'>'} ngưỡng này</div>
</div>
""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════
# BODY — INPUT FORM
# ═════════════════════════════════════════════════════════════
st.markdown('<div class="iq-body">', unsafe_allow_html=True)

st.markdown("""
<div class="iq-rub">// thông tin khách hàng</div>
<div class="iq-section-hd">Nhập đặc điểm khách hàng cần dự đoán</div>
<div class="iq-section-desc">Mô hình sẽ ước lượng uplift cho 2 loại email (Mens, Womens) và đề xuất hành động tối ưu dựa trên break-even threshold cấu hình ở sidebar.</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3, gap='large')

with col1:
    st.markdown('<div class="iq-col-title">Hành vi mua hàng</div>', unsafe_allow_html=True)
    recency = st.slider('Recency (tháng kể từ lần mua cuối)', 1, 12, 5,
                         help='Khoảng thời gian từ lần mua cuối cùng')
    history_log = st.number_input('History — log(tổng chi tiêu)',
                                    0.0, 10.0, 5.0, step=0.5,
                                    help='Log của tổng chi tiêu trước đó (VND)')

with col2:
    st.markdown('<div class="iq-col-title">Đặc điểm khách hàng</div>', unsafe_allow_html=True)
    womens = st.radio('Đã từng mua sản phẩm nữ?',
                       ['Không', 'Có'], horizontal=True)
    newbie = st.radio('Khách hàng mới (newbie)?',
                       ['Không', 'Có'], horizontal=True,
                       help='Khách đăng ký trong 12 tháng gần đây')

with col3:
    st.markdown('<div class="iq-col-title">Khu vực & Kênh mua</div>', unsafe_allow_html=True)
    zip_code = st.selectbox('Khu vực',
                              ['Urban (thành thị)', 'Suburban (ngoại ô)', 'Rural (nông thôn)'])
    channel = st.selectbox('Kênh mua chính',
                            ['Multichannel (đa kênh)', 'Web', 'Phone'])

st.markdown('<div style="height:18px"></div>', unsafe_allow_html=True)

predict_btn = st.button('▲  Dự đoán  ▲', type='primary', use_container_width=True)


# ═════════════════════════════════════════════════════════════
# RESULTS
# ═════════════════════════════════════════════════════════════
if predict_btn:
    X = np.array([[
        recency,
        1 if womens == 'Có' else 0,
        1 if newbie == 'Có' else 0,
        history_log,
        1 if zip_code.startswith('Rural') else 0,
        1 if zip_code.startswith('Suburban') else 0,
        1 if zip_code.startswith('Urban') else 0,
        1 if channel.startswith('Multichannel') else 0,
        1 if channel.startswith('Phone') else 0,
        1 if channel.startswith('Web') else 0,
    ]], dtype=np.float32)

    cate = predict_cate(cf_model, X)[0]
    tau_men, tau_women = float(cate[0]), float(cate[1])
    action = optimal_action(cate.reshape(1, -1),
                              profit=profit_per_conv, cost=cost_per_email)[0]
    resp = float(predict_response(response_model, X)[0]) if response_model is not None else None

    # ── KẾT QUẢ DỰ ĐOÁN ──
    st.markdown('<div style="height:24px"></div>', unsafe_allow_html=True)
    st.markdown('<div class="iq-rub">// kết quả dự đoán cate</div>', unsafe_allow_html=True)
    st.markdown('<div class="iq-section-hd">Conditional Average Treatment Effect</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(gauge_uplift(tau_men, threshold=threshold,
                                       label='τ_men · Mens E-Mail'),
                          use_container_width=True)
    with c2:
        st.plotly_chart(gauge_uplift(tau_women, threshold=threshold,
                                       label='τ_women · Womens E-Mail'),
                          use_container_width=True)

    # ── KHUYẾN NGHỊ ──
    st.markdown('<div style="height:24px"></div>', unsafe_allow_html=True)
    st.markdown('<div class="iq-rub">// khuyến nghị hành động</div>', unsafe_allow_html=True)

    if action == 0:
        loss_estimate = abs(profit_per_conv * cate.max() - cost_per_email)
        st.markdown(f"""
<div class="iq-action-card danger">
<div class="iq-action-title danger">✕ Không gửi email</div>
<div class="iq-action-body">
Cả hai loại email đều có uplift dự đoán <strong>dưới ngưỡng break-even</strong>
<span class="iq-mono">τ = {threshold:.4f}</span>.<br><br>
• <strong>τ_men</strong>: <span class="iq-mono">{tau_men:+.4f}</span> &nbsp; {('✕ dưới ngưỡng' if tau_men < threshold else '✓ trên ngưỡng')}<br>
• <strong>τ_women</strong>: <span class="iq-mono">{tau_women:+.4f}</span> &nbsp; {('✕ dưới ngưỡng' if tau_women < threshold else '✓ trên ngưỡng')}<br><br>
<strong>Lý do</strong>: Gửi email cho khách này dự kiến <strong>lỗ {loss_estimate:,.0f} VND/user</strong> — không hiệu quả về chi phí.
</div>
</div>
""", unsafe_allow_html=True)

    else:
        treat_name = 'Mens E-Mail' if action == 1 else 'Womens E-Mail'
        chosen_tau = tau_men if action == 1 else tau_women
        expected_profit = profit_per_conv * chosen_tau - cost_per_email

        st.markdown(f"""
<div class="iq-action-card success">
<div class="iq-action-title success">✓ Gửi {treat_name}</div>
<div class="iq-action-body">
Mô hình đề xuất gửi <strong>{treat_name}</strong> — đây là treatment có lợi nhuận kỳ vọng cao nhất.<br><br>
• <strong>Uplift dự đoán</strong>: <span class="iq-mono">{chosen_tau:+.4f}</span> (= +{chosen_tau*100:.2f}% điểm conversion)<br>
• <strong>Doanh thu kỳ vọng</strong>: <span class="iq-mono">{profit_per_conv * chosen_tau:,.0f} VND/user</span><br>
• <strong>Chi phí</strong>: <span class="iq-mono">{cost_per_email:,.0f} VND/user</span><br><br>
<strong style="font-size:15px">→ Lợi nhuận kỳ vọng: <span style="color:#6B8068;font-size:18px">{expected_profit:,.0f} VND/user</span></strong>
</div>
</div>
""", unsafe_allow_html=True)

    # ── PHÂN LOẠI QUADRANT ──
    if resp is not None:
        st.markdown('<div style="height:24px"></div>', unsafe_allow_html=True)
        st.markdown('<div class="iq-rub">// phân loại khách hàng</div>', unsafe_allow_html=True)

        max_uplift = float(cate.max())
        quadrant = quadrant_label(max_uplift, resp,
                                    thresholds['u_p10'],
                                    thresholds['u_med'],
                                    thresholds['r_med'])
        color = QUADRANT_COLORS.get(quadrant, '#6B7280')
        recommendation = QUADRANT_RECOMMENDATION.get(quadrant, '')

        st.markdown(f"""
<div class="iq-quadrant-card" style="border-left-color:{color}">
<div style="display:flex;justify-content:space-between;align-items:baseline;gap:20px">
<div style="flex:1">
<div style="font-family:'IBM Plex Mono',monospace;font-size:10px;letter-spacing:.2em;text-transform:uppercase;color:{color};font-weight:600">Nhóm khách hàng</div>
<div class="iq-q-name" style="color:{color};margin-top:4px">{quadrant}</div>
<div class="iq-q-rec">{recommendation}</div>
</div>
<div style="text-align:right;font-family:'IBM Plex Mono',monospace;font-size:11px;color:#4A6378">
<div>uplift_max</div>
<div style="font-size:16px;color:#1A2A47;font-weight:500;margin-top:2px">{max_uplift:+.4f}</div>
<div style="margin-top:8px">response</div>
<div style="font-size:16px;color:#1A2A47;font-weight:500;margin-top:2px">{resp:.4f}</div>
</div>
</div>
<div class="iq-q-meta">
Ngưỡng phân loại: u_p10={thresholds['u_p10']:.4f} · u_med={thresholds['u_med']:.4f} · r_med={thresholds['r_med']:.4f}
</div>
</div>
""", unsafe_allow_html=True)

    # ── BẢNG CHI TIẾT ──
    st.markdown('<div style="height:24px"></div>', unsafe_allow_html=True)
    st.markdown('<div class="iq-rub">// bảng chi tiết</div>', unsafe_allow_html=True)
    st.markdown('<div class="iq-section-hd">So sánh 3 lựa chọn</div>', unsafe_allow_html=True)

    rows = [
        ('Mens E-Mail',   tau_men,    profit_per_conv * tau_men,    cost_per_email, profit_per_conv * tau_men - cost_per_email,    action == 1),
        ('Womens E-Mail', tau_women,  profit_per_conv * tau_women,  cost_per_email, profit_per_conv * tau_women - cost_per_email,  action == 2),
        ('Không gửi',     0.0,        0.0,                            0,             0.0,                                              action == 0),
    ]
    table_html = '<table class="iq-dt">'
    table_html += '<tr><th>Loại Email</th><th style="text-align:right">Uplift</th><th style="text-align:right">Doanh thu</th><th style="text-align:right">Chi phí</th><th style="text-align:right">Lợi nhuận ròng</th></tr>'
    for name, tau, rev, cost, profit_v, is_best in rows:
        cls = 'highlight' if is_best else ''
        prefix = '★ ' if is_best else ''
        table_html += f'<tr class="{cls}"><td>{prefix}{name}</td><td class="num">{tau:+.4f}</td><td class="num">{rev:,.0f}</td><td class="num">{cost:,.0f}</td><td class="num">{profit_v:,.0f}</td></tr>'
    table_html += '</table>'
    st.markdown(table_html, unsafe_allow_html=True)

else:
    # ── EMPTY STATE ──
    st.markdown("""
<div class="iq-empty">
<div class="icon">▲</div>
<div class="text">Nhập thông tin khách hàng ở phía trên rồi bấm <strong>DỰ ĐOÁN</strong> để xem kết quả.</div>
</div>
""", unsafe_allow_html=True)

    st.markdown('<div style="height:24px"></div>', unsafe_allow_html=True)
    st.markdown('<div class="iq-rub">// 3 personas tham khảo</div>', unsafe_allow_html=True)
    st.markdown('<div class="iq-section-hd">Mẫu khách hàng điển hình</div>', unsafe_allow_html=True)

    st.markdown("""
<table class="iq-dt">
<tr><th>Persona</th><th>Recency</th><th>Womens</th><th>Newbie</th><th>History</th><th>Channel</th><th>Khu vực</th><th>Kỳ vọng</th></tr>
<tr><td><strong style="color:#B22234">▲ Persuadable mạnh</strong></td><td>1-2</td><td>1</td><td>1</td><td>7-9</td><td>Multichannel</td><td>Urban</td><td>Uplift cao → gửi Mens</td></tr>
<tr><td><strong style="color:#4A6378">◆ Sure Thing</strong></td><td>3-5</td><td>1</td><td>0</td><td>8+</td><td>Phone</td><td>Suburban</td><td>Tự mua, không cần gửi</td></tr>
<tr><td><strong style="color:#8C7B6B">◯ Lost Cause</strong></td><td>9-12</td><td>0</td><td>0</td><td>3-4</td><td>Web</td><td>Rural</td><td>Không phản hồi</td></tr>
</table>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
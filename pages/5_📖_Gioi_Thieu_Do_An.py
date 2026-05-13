"""
Trang 5 — Giới thiệu đồ án (Editorial design v4)
Cover tiểu luận: đề tài, GVHD, nhóm thực hiện, tóm tắt, mục tiêu, phương pháp.
"""
import streamlit as st
from utils.editorial import (inject_css, render_masthead, render_sidebar_header,
                              sidebar_section_title, section)

st.set_page_config(
    page_title='Giới thiệu đồ án — UpliftIQ',
    page_icon='▲',
    layout='wide',
    initial_sidebar_state='expanded',
)


# ═════════════════════════════════════════════════════════════
# CSS riêng cho trang Giới thiệu (cover hero, team cards, refs)
# ═════════════════════════════════════════════════════════════
EXTRA_CSS = """
/* ── Cover hero ── */
.iq-cover { background: #1A2A47; color: #F4EFE6;
    margin: 24px -80px 32px; padding: 56px 80px 48px;
    border-top: 4px solid #C7A270; border-bottom: 4px solid #B22234;
    position: relative; }
.iq-cover::before { content: ''; position: absolute; top: 0; left: 0; right: 0;
    height: 6px; background: linear-gradient(90deg, #B22234 0%, #B22234 30%, #C7A270 30%, #C7A270 100%); }
.iq-cover-kicker { font-family: 'IBM Plex Mono', monospace; font-size: 11px;
    color: #C7A270; letter-spacing: .28em; text-transform: uppercase;
    margin-bottom: 22px; padding-bottom: 14px; border-bottom: 1px solid #2C3E5C; }
.iq-cover-kicker span { color: #B22234; }
.iq-cover-title { font-family: 'Playfair Display', serif;
    font-size: 56px; font-weight: 900; line-height: 1.05; letter-spacing: -1.5px;
    color: #F4EFE6; }
.iq-cover-title em { color: #B22234; font-style: normal; }
.iq-cover-title .accent { color: #C7A270; font-style: italic; font-weight: 700; }
.iq-cover-rule { height: 3px; background: #B22234; margin: 22px 0; width: 80px; }
.iq-cover-sub { font-family: 'Playfair Display', serif; font-style: italic;
    font-size: 22px; line-height: 1.4; color: #F4EFE6; font-weight: 400;
    max-width: 880px; }
.iq-cover-meta { display: flex; justify-content: space-between; flex-wrap: wrap; gap: 14px;
    margin-top: 36px; padding-top: 18px; border-top: 1px solid #2C3E5C;
    font-family: 'IBM Plex Mono', monospace; font-size: 10px;
    color: #8C7B6B; letter-spacing: .15em; text-transform: uppercase; }
.iq-cover-meta b { color: #C7A270; font-weight: 500; }

/* ── Team / Advisor cards ── */
.iq-people { display: grid; grid-template-columns: 1fr 2fr; gap: 0;
    border-top: 3px solid #1A2A47; border-bottom: 1px solid #C7A270;
    margin: 8px 0 28px; }
.iq-people-col { padding: 22px 28px 22px 0; }
.iq-people-col:first-child { border-right: 1px solid #C7A270; padding-right: 28px; }
.iq-people-col:last-child { padding-left: 28px; padding-right: 0; }
.iq-people-label { font-family: 'IBM Plex Mono', monospace; font-size: 9px;
    color: #B22234; letter-spacing: .25em; text-transform: uppercase;
    margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #C7A270; }

.iq-advisor-name { font-family: 'Playfair Display', serif; font-size: 32px;
    font-weight: 900; line-height: 1.1; color: #1A2A47; letter-spacing: -.5px; }
.iq-advisor-role { font-family: 'IBM Plex Sans Condensed', sans-serif;
    font-size: 11px; color: #4A6378; text-transform: uppercase;
    letter-spacing: .15em; margin-top: 6px; font-weight: 600; }
.iq-advisor-org { font-family: 'IBM Plex Sans Condensed', sans-serif;
    font-size: 12px; color: #6B4E5C; margin-top: 12px; padding-top: 10px;
    border-top: 1px solid #C7A270; font-style: italic; }

.iq-student { padding: 10px 0; border-bottom: 1px solid #C7A270;
    display: flex; justify-content: space-between; align-items: baseline;
    gap: 14px; flex-wrap: wrap; }
.iq-student:last-child { border-bottom: none; }
.iq-student-name { font-family: 'Playfair Display', serif; font-size: 19px;
    font-weight: 700; color: #1A2A47; flex: 1; min-width: 200px; }
.iq-student-mssv { font-family: 'IBM Plex Mono', monospace; font-size: 12px;
    color: #B22234; letter-spacing: .08em; background: #FBF8F2;
    padding: 4px 10px; border-left: 2px solid #B22234; }

/* ── Pull-quote / Abstract ── */
.iq-abstract { background: #FBF8F2; padding: 28px 36px; margin: 14px 0;
    border-left: 6px solid #C7A270; border-right: 1px solid #C7A270;
    font-family: 'Playfair Display', serif; font-size: 17px; line-height: 1.7;
    color: #1A2A47; }
.iq-abstract::first-letter { font-family: 'Playfair Display', serif;
    font-size: 64px; font-weight: 900; color: #B22234; float: left;
    line-height: 0.85; padding-right: 10px; padding-top: 4px; }
.iq-abstract b, .iq-abstract strong { color: #B22234; font-weight: 700; }

/* ── Numbered list editorial ── */
.iq-nums { display: grid; grid-template-columns: repeat(2, 1fr); gap: 0;
    border-top: 3px solid #1A2A47; margin: 8px 0; }
.iq-num { display: flex; gap: 18px; padding: 18px 22px 18px 0;
    border-bottom: 1px solid #C7A270; align-items: flex-start; }
.iq-num:nth-child(odd) { padding-right: 22px; border-right: 1px solid #C7A270; }
.iq-num:nth-child(even) { padding-left: 22px; }
.iq-num-n { font-family: 'Playfair Display', serif; font-size: 42px;
    font-weight: 900; color: #B22234; line-height: 0.9; min-width: 50px; }
.iq-num-body .h { font-family: 'IBM Plex Sans Condensed', sans-serif;
    font-size: 14px; font-weight: 700; color: #1A2A47; margin-bottom: 4px;
    text-transform: uppercase; letter-spacing: .06em; }
.iq-num-body .d { font-family: 'IBM Plex Sans Condensed', sans-serif;
    font-size: 13px; color: #4A6378; line-height: 1.6; }

/* ── Pipeline / phương pháp ── */
.iq-pipe { display: grid; grid-template-columns: repeat(5, 1fr); gap: 0;
    border-top: 3px solid #1A2A47; border-bottom: 3px solid #1A2A47;
    margin: 8px 0 20px; }
.iq-pipe-step { padding: 16px 14px; border-right: 1px solid #C7A270;
    text-align: center; position: relative; }
.iq-pipe-step:last-child { border-right: none; }
.iq-pipe-step::after { content: '→'; position: absolute; right: -10px; top: 26px;
    color: #B22234; font-family: 'IBM Plex Mono', monospace; font-size: 18px;
    background: #F4EFE6; padding: 0 4px; z-index: 2; }
.iq-pipe-step:last-child::after { display: none; }
.iq-pipe-num { font-family: 'IBM Plex Mono', monospace; font-size: 10px;
    color: #B22234; letter-spacing: .2em; margin-bottom: 4px; }
.iq-pipe-name { font-family: 'Playfair Display', serif; font-size: 18px;
    font-weight: 700; color: #1A2A47; line-height: 1.15; }
.iq-pipe-desc { font-family: 'IBM Plex Sans Condensed', sans-serif;
    font-size: 10px; color: #6B4E5C; margin-top: 6px; line-height: 1.4; }

/* ── Model list ── */
.iq-models { border-top: 3px solid #1A2A47; margin-top: 8px; }
.iq-model { display: grid; grid-template-columns: 28px 1fr 100px 80px;
    align-items: center; gap: 14px; padding: 12px 0; border-bottom: 1px solid #C7A270; }
.iq-model:last-child { border-bottom: 2px solid #1A2A47; }
.iq-model .rk { font-family: 'IBM Plex Mono', monospace; font-size: 10px;
    color: #C7A270; }
.iq-model .nm { font-family: 'Playfair Display', serif; font-size: 18px;
    font-weight: 700; color: #1A2A47; }
.iq-model .nm em { color: #B22234; font-style: normal; font-weight: 900;
    margin-left: 8px; font-family: 'IBM Plex Mono', monospace; font-size: 10px;
    background: #B22234; color: #F4EFE6; padding: 2px 6px; letter-spacing: .08em; }
.iq-model .ds { font-family: 'IBM Plex Sans Condensed', sans-serif;
    font-size: 11px; color: #4A6378; }
.iq-model .qn { font-family: 'IBM Plex Mono', monospace; font-size: 13px;
    color: #1A2A47; font-weight: 600; text-align: right; }
.iq-model .lb { font-family: 'IBM Plex Mono', monospace; font-size: 9px;
    color: #C7A270; text-align: right; letter-spacing: .1em; }

/* ── Tool cards (links sang 4 trang công cụ) ── */
.iq-tools { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0;
    border-top: 3px solid #1A2A47; border-bottom: 3px solid #1A2A47;
    margin: 8px 0; }
.iq-tool { display: block; padding: 18px 14px; border-right: 1px solid #C7A270;
    text-align: center; text-decoration: none !important; color: inherit;
    transition: background .15s ease; }
.iq-tool:last-child { border-right: none; }
.iq-tool:hover { background: #ECE5D7; }
.iq-tool .n { font-family: 'Playfair Display', serif; font-size: 30px;
    font-weight: 900; color: #B22234; line-height: 1; }
.iq-tool .t { font-family: 'IBM Plex Sans Condensed', sans-serif; font-size: 12px;
    font-weight: 700; color: #1A2A47; margin-top: 4px; text-transform: uppercase;
    letter-spacing: .06em; }
.iq-tool .d { font-family: 'IBM Plex Sans Condensed', sans-serif; font-size: 10px;
    color: #4A6378; margin-top: 4px; line-height: 1.4; padding: 0 6px; }

/* ── References ── */
.iq-ref { padding: 12px 0; border-bottom: 1px solid #C7A270;
    display: grid; grid-template-columns: 32px 1fr; gap: 12px; }
.iq-ref:first-child { border-top: 2px solid #1A2A47; }
.iq-ref-n { font-family: 'IBM Plex Mono', monospace; font-size: 11px;
    color: #B22234; font-weight: 600; }
.iq-ref-txt { font-family: 'IBM Plex Sans Condensed', sans-serif; font-size: 12px;
    color: #1A2A47; line-height: 1.6; }
.iq-ref-txt em { color: #4A6378; font-style: italic; }

/* ── Responsive ── */
@media (max-width: 1100px) {
.iq-cover-title { font-size: 40px; }
.iq-cover-sub { font-size: 18px; }
.iq-people { grid-template-columns: 1fr; }
.iq-people-col:first-child { border-right: none; border-bottom: 1px solid #C7A270;
    padding-bottom: 22px; padding-right: 0; }
.iq-people-col:last-child { padding-left: 0; padding-top: 22px; }
.iq-pipe { grid-template-columns: repeat(2, 1fr); }
.iq-pipe-step::after { display: none; }
.iq-tools { grid-template-columns: repeat(2, 1fr); }
.iq-nums { grid-template-columns: 1fr; }
.iq-num:nth-child(odd) { border-right: none; padding-right: 0; }
.iq-num:nth-child(even) { padding-left: 0; }
}
@media (max-width: 600px) {
.iq-cover { margin: 16px -22px 24px; padding: 36px 22px 28px; }
.iq-cover-title { font-size: 30px; letter-spacing: -.8px; }
.iq-pipe, .iq-tools { grid-template-columns: 1fr; }
.iq-model { grid-template-columns: 24px 1fr; }
.iq-model .qn, .iq-model .lb { display: none; }
}
"""

inject_css(EXTRA_CSS)


# ═════════════════════════════════════════════════════════════
# PAGE HEADER
# ═════════════════════════════════════════════════════════════
render_masthead(5, 'GIỚI THIỆU ĐỒ ÁN',
                'Tiểu luận', 'kết thúc môn',
                'Học phần Khai thác dữ liệu · ĐHSP TP.HCM · 2026')


# ═════════════════════════════════════════════════════════════
# SIDEBAR
# ═════════════════════════════════════════════════════════════
with st.sidebar:
    render_sidebar_header(active_idx=5)

    sidebar_section_title('▲ Đề tài')
    st.markdown("""
<div style="font-family:'IBM Plex Sans Condensed',sans-serif;font-size:11px;color:#F4EFE6;line-height:1.6;padding:8px 0">
Uplift Modeling cho chiến dịch tặng điểm &amp; khuyến mãi — Causal ML để nhận diện
nhóm <b style="color:#B22234">Persuadable</b>.
</div>
""", unsafe_allow_html=True)

    sidebar_section_title('▲ GVHD')
    st.markdown("""
<div style="font-family:'IBM Plex Sans Condensed',sans-serif;font-size:11px;color:#F4EFE6;line-height:1.7;padding:4px 0">
<b style="color:#C7A270">TS. Huỳnh Lê Tấn Tài</b><br>
<span style="color:#C7A270">ĐHSP TP.HCM</span>
</div>
""", unsafe_allow_html=True)

    sidebar_section_title('▲ Nhóm thực hiện')
    st.markdown("""
<div style="font-family:'IBM Plex Mono',monospace;font-size:10px;color:#C7A270;line-height:1.9;padding:4px 0">
<div style="color:#F4EFE6">Tăng Ngọc Phụng</div>
<div>KHMT836027</div>
<div style="height:6px"></div>
<div style="color:#F4EFE6">Hoàng Châu Ngọc Phương</div>
<div>KHMT836028</div>
<div style="height:6px"></div>
<div style="color:#F4EFE6">Lê Thị Mai Len</div>
<div>KHMT836015</div>
</div>
""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════
# COVER HERO
# ═════════════════════════════════════════════════════════════
st.markdown('<div class="iq-body" style="padding-top:8px">', unsafe_allow_html=True)

st.markdown("""
<div class="iq-cover">
<div class="iq-cover-kicker">
ĐỒ ÁN TIỂU LUẬN KẾT THÚC MÔN · HỌC PHẦN <span>KHAI THÁC DỮ LIỆU</span> · 2026
</div>

<div class="iq-cover-title">
Ứng dụng <em>Uplift Modeling</em><br>
trong tối ưu hóa chiến dịch<br>
<span class="accent">tặng điểm &amp; khuyến mãi</span>
</div>

<div class="iq-cover-rule"></div>

<div class="iq-cover-sub">
Tiếp cận <b>Causal Machine Learning</b> để nhận diện
nhóm khách hàng <em style="color:#B22234;font-style:normal;font-weight:700">Persuadable</em>
— những người chỉ mua hàng nếu được kích hoạt bằng email/khuyến mãi.
</div>

<div class="iq-cover-meta">
<span><b>GVHD</b> · TS. Huỳnh Lê Tấn Tài</span>
<span><b>NHÓM</b> · 3 học viên</span>
<span><b>MÔ HÌNH</b> · 6 uplift estimators</span>
<span><b>DỮ LIỆU</b> · Hillstrom 57,557 khách hàng</span>
<span><b>NĂM</b> · 2026</span>
</div>
</div>
""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════
# GVHD + NHÓM THỰC HIỆN
# ═════════════════════════════════════════════════════════════
section('giảng viên hướng dẫn & nhóm thực hiện',
        'Người đồng hành cùng đề tài')

st.markdown("""
<div class="iq-people">
<div class="iq-people-col">
<div class="iq-people-label">Giảng viên hướng dẫn</div>
<div class="iq-advisor-name">TS. Huỳnh Lê Tấn Tài</div>
<div class="iq-advisor-role">Giảng viên · Khoa Công nghệ Thông tin</div>
<div class="iq-advisor-org">Trường Đại học Sư phạm Thành phố Hồ Chí Minh — Học phần Khai thác dữ liệu</div>
</div>
<div class="iq-people-col">
<div class="iq-people-label">Nhóm thực hiện · 3 học viên</div>
<div class="iq-student">
<div class="iq-student-name">Tăng Ngọc Phụng</div>
<div class="iq-student-mssv">KHMT836027</div>
</div>
<div class="iq-student">
<div class="iq-student-name">Hoàng Châu Ngọc Phương</div>
<div class="iq-student-mssv">KHMT836028</div>
</div>
<div class="iq-student">
<div class="iq-student-name">Lê Thị Mai Len</div>
<div class="iq-student-mssv">KHMT836015</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════
# TÓM TẮT
# ═════════════════════════════════════════════════════════════
section('tóm tắt', 'Vấn đề & cách tiếp cận')

st.markdown("""
<div class="iq-abstract">
<b>Response model</b> truyền thống chỉ dự đoán "ai sẽ mua" mà không phân biệt
được liệu khách hàng có mua <em>nhờ</em> email khuyến mãi hay tự mua không cần email.
Hệ quả là doanh nghiệp gửi đại trà — vừa lãng phí ngân sách cho nhóm tự mua
(<b>Sure Thing</b>), vừa gây tác dụng ngược ở nhóm khó chịu khi nhận quảng cáo
(<b>Sleeping Dog</b>). Đề tài này áp dụng <b>Uplift Modeling</b> — ước lượng
hiệu ứng nhân quả cá nhân <em>τ(x) = E[Y(1) − Y(0) | X = x]</em> bằng sáu
thuật toán Causal ML (S/T/X/DR-Learner, Uplift Random Forest, Causal Forest DML)
trên bộ dữ liệu Hillstrom (57,557 khách hàng) — để phân loại bốn nhóm
Persuadable / Sure Thing / Lost Cause / Sleeping Dog và đề xuất chính sách
phân bổ tối ưu, kiểm chứng qua IPS evaluation và Qini curve.
</div>
""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════
# MỤC TIÊU NGHIÊN CỨU
# ═════════════════════════════════════════════════════════════
section('mục tiêu nghiên cứu', 'Bốn câu hỏi cần trả lời')

st.markdown("""
<div class="iq-nums">
<div class="iq-num">
<div class="iq-num-n">01</div>
<div class="iq-num-body">
<div class="h">Ước lượng CATE cá nhân hóa</div>
<div class="d">Xây dựng mô hình ước lượng <code>τ(x) = E[Y(1)−Y(0)|X=x]</code> —
phần gia tăng xác suất mua hàng khi khách hàng nhận email khuyến mãi,
cho từng cá nhân dựa trên 10 đặc trưng.</div>
</div>
</div>
<div class="iq-num">
<div class="iq-num-n">02</div>
<div class="iq-num-body">
<div class="h">So sánh sáu thuật toán uplift</div>
<div class="d">Đánh giá S-Learner, T-Learner, X-Learner, DR-Learner,
Uplift Random Forest và Causal Forest DML qua <b>Qini score</b> pool 5-fold CV
để chọn champion model.</div>
</div>
</div>
<div class="iq-num">
<div class="iq-num-n">03</div>
<div class="iq-num-body">
<div class="h">Phân loại 4 nhóm hành vi</div>
<div class="d">Dùng uplift kết hợp response model để gắn nhãn
Persuadable / Sure Thing / Lost Cause / Sleeping Dog,
phục vụ chiến lược marketing differentiated.</div>
</div>
</div>
<div class="iq-num">
<div class="iq-num-n">04</div>
<div class="iq-num-body">
<div class="h">Tối ưu chính sách phân bổ</div>
<div class="d">Đề xuất uplift-threshold policy <code>τ(x) &gt; cost/profit</code>
và kiểm chứng bằng <b>IPS estimator</b> trên test set —
so sánh với baseline không gửi / gửi đại trà / random.</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════
# PHƯƠNG PHÁP
# ═════════════════════════════════════════════════════════════
section('phương pháp', 'Pipeline 5 bước · từ raw data đến policy')

st.markdown("""
<div class="iq-pipe">
<div class="iq-pipe-step">
<div class="iq-pipe-num">01</div>
<div class="iq-pipe-name">EDA & Preprocess</div>
<div class="iq-pipe-desc">Hillstrom 57,557 dòng · log-transform history · one-hot encode</div>
</div>
<div class="iq-pipe-step">
<div class="iq-pipe-num">02</div>
<div class="iq-pipe-name">Train 6 models</div>
<div class="iq-pipe-desc">CausalML + EconML · 5-fold CV · GridSearch hyperparams</div>
</div>
<div class="iq-pipe-step">
<div class="iq-pipe-num">03</div>
<div class="iq-pipe-name">Đánh giá Qini</div>
<div class="iq-pipe-desc">Pool predictions · Qini score · chọn champion</div>
</div>
<div class="iq-pipe-step">
<div class="iq-pipe-num">04</div>
<div class="iq-pipe-name">Phân loại quadrant</div>
<div class="iq-pipe-desc">u_p10 / u_med / r_med thresholds · 4 nhóm hành vi</div>
</div>
<div class="iq-pipe-step">
<div class="iq-pipe-num">05</div>
<div class="iq-pipe-name">IPS Policy Eval</div>
<div class="iq-pipe-desc">Inverse-Propensity Score · profit/user · sensitivity</div>
</div>
</div>
""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════
# 6 MÔ HÌNH
# ═════════════════════════════════════════════════════════════
section('sáu thuật toán uplift', 'Xếp hạng theo Qini Pool-CV',
        'Causal Forest DML (EconML) đạt Qini cao nhất 0.150 ± 0.099, được chọn làm champion.')

models_data = [
    (1, 'Causal Forest DML', 'EconML · Athey &amp; Wager 2019', '0.1502', '± 0.0993', True),
    (2, 'S-Learner', 'CausalML · single-model meta', '0.1237', '± 0.0754', False),
    (3, 'T-Learner', 'CausalML · two-model meta', '0.0949', '± 0.0323', False),
    (4, 'Uplift Random Forest', 'CausalML · tree-based', '0.0709', '± 0.0742', False),
    (5, 'X-Learner', 'CausalML · Künzel 2019', '0.0594', '± 0.0590', False),
    (6, 'DR-Learner', 'CausalML · Doubly Robust', '0.0499', '± 0.0893', False),
]
rows_html = ''
for rk, name, desc, qini, std, is_champ in models_data:
    champ_badge = '<em>CHAMP</em>' if is_champ else ''
    rows_html += f"""
<div class="iq-model">
<div class="rk">{rk:02d}</div>
<div>
<div class="nm">{name}{champ_badge}</div>
<div class="ds">{desc}</div>
</div>
<div class="qn">{qini}</div>
<div class="lb">{std}</div>
</div>
"""
st.markdown(f'<div class="iq-models">{rows_html}</div>', unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════
# ĐÓNG GÓP CHÍNH
# ═════════════════════════════════════════════════════════════
section('đóng góp chính', 'Bốn phát hiện then chốt')

st.markdown("""
<div class="iq-nums">
<div class="iq-num">
<div class="iq-num-n">▲</div>
<div class="iq-num-body">
<div class="h">Lift +1.98× cho Mens E-Mail top 10%</div>
<div class="d">Causal Forest xếp đúng top 10% khách hàng có conversion rate 3.40%
— gấp 2.23× ATE tổng thể (+0.86%), chứng minh khả năng targeting hiệu quả.</div>
</div>
</div>
<div class="iq-num">
<div class="iq-num-n">▲</div>
<div class="iq-num-body">
<div class="h">+30.2% lợi nhuận vs không gửi</div>
<div class="d">Uplift Policy v2 (threshold-based) đạt 1,859 VND/user so với
1,320 VND/user của policy không gửi — kiểm chứng bằng IPS estimator trên test set.</div>
</div>
</div>
<div class="iq-num">
<div class="iq-num-n">▲</div>
<div class="iq-num-body">
<div class="h">Phát hiện 1,659 Sleeping Dogs</div>
<div class="d">T-Learner xác nhận 1,659 khách hàng có uplift âm — gửi email cho họ
sẽ gây tác dụng ngược. Khám phá này không thể có được bằng response model thuần.</div>
</div>
</div>
<div class="iq-num">
<div class="iq-num-n">▲</div>
<div class="iq-num-body">
<div class="h">Multichannel = 80.5% Persuadable</div>
<div class="d">Khách hàng đa kênh chiếm 80.5% nhóm Persuadable — đây là feature
nhận diện quan trọng nhất, giúp tinh chỉnh chiến lược thu hút khách hàng tiềm năng.</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════
# CẤU TRÚC ỨNG DỤNG
# ═════════════════════════════════════════════════════════════
section('cấu trúc ứng dụng', 'Bốn công cụ tương tác',
        'Bấm vào từng card để mở công cụ tương ứng.')

st.markdown("""
<div class="iq-tools">
<a class="iq-tool" href="/Single_Predict" target="_self">
<div class="n">01</div>
<div class="t">Single Predict</div>
<div class="d">Nhập 1 khách, nhận CATE + recommendation</div>
</a>
<a class="iq-tool" href="/Batch_Upload" target="_self">
<div class="n">02</div>
<div class="t">Batch Upload</div>
<div class="d">Upload CSV, batch scoring, download kết quả</div>
</a>
<a class="iq-tool" href="/Economic_Simulator" target="_self">
<div class="n">03</div>
<div class="t">Economic Sim</div>
<div class="d">Điều chỉnh cost/profit, xem profit curve</div>
</a>
<a class="iq-tool" href="/Persona_Explorer" target="_self">
<div class="n">04</div>
<div class="t">Persona</div>
<div class="d">Khám phá 4 nhóm, filter, marketing plan</div>
</a>
</div>
""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════
# TÀI LIỆU THAM KHẢO
# ═════════════════════════════════════════════════════════════
section('tài liệu tham khảo', 'Foundational works · Uplift & Causal ML')

refs = [
    ('Athey, S., &amp; Wager, S. (2019).', 'Estimating Treatment Effects with Causal Forests: An Application.', 'Observational Studies, 5(2), 37–51.'),
    ('Künzel, S. R., Sekhon, J. S., Bickel, P. J., &amp; Yu, B. (2019).', 'Metalearners for estimating heterogeneous treatment effects using machine learning.', 'PNAS, 116(10), 4156–4165.'),
    ('Hillstrom, K. (2008).', 'The MineThatData E-Mail Analytics And Data Mining Challenge.', 'MineThatData Blog — public dataset benchmark.'),
    ('Imbens, G. W., &amp; Rubin, D. B. (2015).', 'Causal Inference for Statistics, Social, and Biomedical Sciences.', 'Cambridge University Press.'),
    ('Diemert, E., Betlei, A., Renaudin, C., &amp; Amini, M. R. (2018).', 'A Large Scale Benchmark for Uplift Modeling.', 'KDD AdKDD &amp; TargetAd Workshop.'),
    ('Radcliffe, N. J., &amp; Surry, P. D. (2011).', 'Real-World Uplift Modelling with Significance-Based Uplift Trees.', 'Stochastic Solutions White Paper.'),
    ('Chernozhukov, V., Chetverikov, D., Demirer, M., et al. (2018).', 'Double/Debiased Machine Learning for Treatment and Structural Parameters.', 'The Econometrics Journal, 21(1), C1–C68.'),
    ('Pearl, J. (2009).', 'Causality: Models, Reasoning, and Inference (2nd ed.).', 'Cambridge University Press.'),
]
refs_html = ''
for i, (authors, title, venue) in enumerate(refs, 1):
    refs_html += f"""
<div class="iq-ref">
<div class="iq-ref-n">[{i:02d}]</div>
<div class="iq-ref-txt">{authors} <em>{title}</em> {venue}</div>
</div>
"""
st.markdown(refs_html, unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════
# FOOTER
# ═════════════════════════════════════════════════════════════
st.markdown("""
<div style="margin-top:32px;border-top:3px solid #1A2A47;padding:18px 0;display:flex;justify-content:space-between;flex-wrap:wrap;gap:12px;font-family:'IBM Plex Mono',monospace;font-size:9px;color:#6B4E5C;letter-spacing:.1em">
<span>© 2026 UPLIFTIQ · TIỂU LUẬN KẾT THÚC MÔN</span>
<span>HỌC PHẦN KHAI THÁC DỮ LIỆU · ĐHSP TP.HCM</span>
<span>STREAMLIT · CAUSALML · ECONML · LIGHTGBM</span>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

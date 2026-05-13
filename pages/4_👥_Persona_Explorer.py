"""
Trang 4 — Persona Explorer (Editorial design v4)
Khám phá 4 nhóm Persuadable / Sure Thing / Lost Cause / Sleeping Dog.
"""
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from utils.load_models import load_test_data, load_persona_profile, FEAT
from utils.policy import QUADRANT_COLORS, QUADRANT_RECOMMENDATION
from utils.plots import quadrant_pie, quadrant_scatter
from utils.editorial import (inject_css, render_masthead, render_sidebar_header,
                              sidebar_section_title, banner, section, error_card)

st.set_page_config(
    page_title='Persona Explorer — UpliftIQ',
    page_icon='▲',
    layout='wide',
    initial_sidebar_state='expanded',
)

inject_css()


# ═════════════════════════════════════════════════════════════
# LOAD DATA
# ═════════════════════════════════════════════════════════════
test_df = load_test_data()
persona_df = load_persona_profile()

if test_df is None:
    render_masthead(4, 'PERSONA EXPLORER',
                    'Khám phá', 'persona khách hàng',
                    'Phân tích 4 nhóm · Đặc trưng · Marketing plan')
    error_card('Thiếu file dữ liệu',
               'Cần file <code>test_quadrant_FINAL.parquet</code> trong '
               '<code>./models/</code>. Quay lại trang chủ để xem trạng thái artifacts.')
    st.stop()

if 'quadrant' not in test_df.columns:
    render_masthead(4, 'PERSONA EXPLORER',
                    'Khám phá', 'persona khách hàng',
                    'Phân tích 4 nhóm · Đặc trưng · Marketing plan')
    error_card('Test data thiếu cột <code>quadrant</code>',
               'Chạy lại Bước 9 trong notebook để gắn nhãn quadrant cho test set.')
    st.stop()


# ═════════════════════════════════════════════════════════════
# PAGE HEADER
# ═════════════════════════════════════════════════════════════
render_masthead(4, 'PERSONA EXPLORER',
                'Khám phá', 'persona khách hàng',
                'Bốn nhóm · Đặc trưng · Bản đồ uplift × response · Marketing plan')


# ═════════════════════════════════════════════════════════════
# SIDEBAR — FILTERS
# ═════════════════════════════════════════════════════════════
with st.sidebar:
    render_sidebar_header(active_idx=4)

    sidebar_section_title('▼ Filter')

    available_quadrants = sorted(test_df['quadrant'].unique().tolist())
    selected_q = st.multiselect(
        'Quadrant',
        available_quadrants,
        default=available_quadrants,
    )

    rec_min, rec_max = int(test_df['recency'].min()), int(test_df['recency'].max())
    rec_range = st.slider('Recency (tháng)', rec_min, rec_max, (rec_min, rec_max))

    womens_filter = st.radio('Womens', ['Tất cả', 'Có (=1)', 'Không (=0)'])
    newbie_filter = st.radio('Newbie', ['Tất cả', 'Có (=1)', 'Không (=0)'])

    sidebar_section_title('▼ Channel')
    channels = []
    if st.checkbox('Multichannel', True): channels.append('Multichannel')
    if st.checkbox('Phone', True): channels.append('Phone')
    if st.checkbox('Web', True): channels.append('Web')


# Apply filters
filtered = test_df[test_df['quadrant'].isin(selected_q)].copy()
filtered = filtered[(filtered['recency'] >= rec_range[0]) &
                      (filtered['recency'] <= rec_range[1])]
if womens_filter != 'Tất cả':
    filtered = filtered[filtered['womens'] == (1 if 'Có' in womens_filter else 0)]
if newbie_filter != 'Tất cả':
    filtered = filtered[filtered['newbie'] == (1 if 'Có' in newbie_filter else 0)]

channel_mask = pd.Series(False, index=filtered.index)
if 'Multichannel' in channels: channel_mask |= (filtered['channel_Multichannel'] == 1)
if 'Phone' in channels: channel_mask |= (filtered['channel_Phone'] == 1)
if 'Web' in channels: channel_mask |= (filtered['channel_Web'] == 1)
filtered = filtered[channel_mask]


# ═════════════════════════════════════════════════════════════
# BODY
# ═════════════════════════════════════════════════════════════
st.markdown('<div class="iq-body">', unsafe_allow_html=True)

banner('info',
       f'🔎 Filter còn lại: <b>{len(filtered):,}</b> khách / {len(test_df):,} tổng')

if len(filtered) == 0:
    banner('warning', '⚠ Không có khách hàng nào khớp filter. Hãy nới lỏng điều kiện ở sidebar.')
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()


# Lead metrics
if 'uplift_max' in filtered.columns:
    mean_uplift = filtered['uplift_max'].mean()
    mean_response = filtered['response'].mean() if 'response' in filtered.columns else float('nan')
    mean_recency = filtered['recency'].mean()
    mean_history = filtered['history_log'].mean()
    response_str = f'{mean_response:.4f}' if not np.isnan(mean_response) else '—'

    st.markdown(f"""
<div class="iq-lead">
<div class="iq-ls">
<div class="v sm red">{mean_uplift:+.4f}</div>
<div class="l">Mean uplift_max</div>
<div class="s">CATE bình quân</div>
</div>
<div class="iq-ls">
<div class="v sm">{response_str}</div>
<div class="l">Mean response</div>
<div class="s">P[Y=1|control]</div>
</div>
<div class="iq-ls">
<div class="v sm tan">{mean_recency:.1f}</div>
<div class="l">Mean recency (tháng)</div>
<div class="s">từ lần mua cuối</div>
</div>
<div class="iq-ls">
<div class="v sm sage">{mean_history:.2f}</div>
<div class="l">Mean history (log)</div>
<div class="s">tổng chi tiêu log</div>
</div>
</div>
""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════
# TABS
# ═════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs([
    'Overview', 'Bản đồ persona', 'Profile chi tiết', 'Marketing plan'
])

# ───────────────── TAB 1: OVERVIEW ─────────────────
with tab1:
    section('phân bổ persona', 'Tỷ lệ 4 nhóm trong filter')

    c1, c2 = st.columns([1, 1])
    with c1:
        counts = filtered['quadrant'].value_counts().to_dict()
        st.plotly_chart(quadrant_pie(counts, QUADRANT_COLORS),
                          use_container_width=True)

    with c2:
        st.markdown('<div class="iq-col-title">Thống kê theo nhóm</div>', unsafe_allow_html=True)
        for q in ['Persuadable', 'Sure Thing', 'Lost Cause', 'Sleeping Dog']:
            n_q = int((filtered['quadrant'] == q).sum())
            pct = n_q / len(filtered) * 100 if len(filtered) > 0 else 0
            color = QUADRANT_COLORS.get(q, '#999')
            st.markdown(f"""
<div class="iq-quadrant-card" style="border-left-color:{color};margin-bottom:10px;padding:14px 18px">
<div style="display:flex;justify-content:space-between;align-items:baseline">
<div style="font-family:'Playfair Display',serif;font-size:18px;font-weight:700;color:{color}">{q}</div>
<div style="font-family:'IBM Plex Mono',monospace;font-size:14px;color:#1A2A47;font-weight:600">{n_q:,} · {pct:.1f}%</div>
</div>
<div style="font-family:'IBM Plex Sans Condensed',sans-serif;font-size:11px;color:#4A6378;margin-top:4px;line-height:1.5">
{QUADRANT_RECOMMENDATION.get(q, '')}
</div>
</div>
""", unsafe_allow_html=True)


# ───────────────── TAB 2: PERSONA MAP ─────────────────
with tab2:
    section('bản đồ 2d', 'Uplift × Response',
            'Mỗi điểm = 1 khách hàng. Vị trí trên bản đồ quyết định nhóm.')

    if 'uplift_max' in filtered.columns and 'response' in filtered.columns:
        st.plotly_chart(quadrant_scatter(filtered), use_container_width=True)

        st.markdown("""
<div class="iq-insight">
<b>Cách đọc bản đồ</b>:<br>
• Trục X = <code>response</code> (P[Y=1|control]) — khả năng tự mua nếu không gửi.<br>
• Trục Y = <code>uplift_max</code> (max τ) — phần tăng thêm conversion nhờ email.<br><br>
🟢 <b>Persuadable</b> (góc trên-trái): uplift cao, response thấp → <b>GỬI</b><br>
🔵 <b>Sure Thing</b> (góc dưới-phải): response cao, uplift thấp → tự mua<br>
⚪ <b>Lost Cause</b> (góc dưới-trái): cả 2 thấp → bỏ qua<br>
🔴 <b>Sleeping Dog</b> (vùng uplift âm): email phản tác dụng → <b>KHÔNG GỬI</b>
</div>
""", unsafe_allow_html=True)
    else:
        banner('warning', '⚠ Test data thiếu cột <code>uplift_max</code> hoặc <code>response</code>.')


# ───────────────── TAB 3: PROFILE CHI TIẾT ─────────────────
with tab3:
    section('persona profile', 'So sánh đặc trưng từng nhóm với population')

    profile = filtered.groupby('quadrant')[FEAT].mean().round(3)
    pop_mean = filtered[FEAT].mean()
    diff = ((profile - pop_mean) / pop_mean * 100).round(1)

    selected_q_profile = st.selectbox(
        'Chọn quadrant',
        sorted(filtered['quadrant'].unique()),
    )

    sub = filtered[filtered['quadrant'] == selected_q_profile]
    n_sub = len(sub)
    color = QUADRANT_COLORS.get(selected_q_profile, '#999')

    st.markdown(f"""
<div class="iq-quadrant-card" style="border-left-color:{color}">
<div style="display:flex;justify-content:space-between;align-items:baseline">
<div>
<div style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:{color};letter-spacing:.2em;text-transform:uppercase;font-weight:600">Nhóm khách hàng</div>
<div class="iq-q-name" style="color:{color};margin-top:4px">{selected_q_profile}</div>
<div class="iq-q-rec">{QUADRANT_RECOMMENDATION.get(selected_q_profile, '')}</div>
</div>
<div style="text-align:right;font-family:'IBM Plex Mono',monospace;font-size:11px;color:#4A6378">
<div>N khách</div>
<div style="font-family:'Playfair Display',serif;font-size:32px;color:#1A2A47;font-weight:900">{n_sub:,}</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)

    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
    st.markdown('<div class="iq-col-title">Đặc trưng nổi bật vs population</div>', unsafe_allow_html=True)

    if selected_q_profile in profile.index:
        sub_diff = diff.loc[selected_q_profile].sort_values(ascending=False)
        higher = [(f, d) for f, d in sub_diff.head(5).items() if d > 0]
        lower = [(f, d) for f, d in sub_diff.tail(5).items() if d < 0]

        c1, c2 = st.columns(2)
        with c1:
            rows_high = ''.join(
                f'<tr><td><code>{f}</code></td>'
                f'<td class="num">{profile.loc[selected_q_profile, f]:.3f}</td>'
                f'<td class="num" style="color:#6B8068;font-weight:700">+{d:.0f}%</td></tr>'
                for f, d in higher
            )
            st.markdown(f"""
<div class="iq-col-title" style="color:#6B8068">▲ Cao hơn population</div>
<table class="iq-dt"><tr><th>Feature</th><th style="text-align:right">Mean</th><th style="text-align:right">Δ%</th></tr>{rows_high}</table>
""", unsafe_allow_html=True)

        with c2:
            rows_low = ''.join(
                f'<tr><td><code>{f}</code></td>'
                f'<td class="num">{profile.loc[selected_q_profile, f]:.3f}</td>'
                f'<td class="num" style="color:#B22234;font-weight:700">{d:.0f}%</td></tr>'
                for f, d in lower
            )
            st.markdown(f"""
<div class="iq-col-title" style="color:#B22234">▼ Thấp hơn population</div>
<table class="iq-dt"><tr><th>Feature</th><th style="text-align:right">Mean</th><th style="text-align:right">Δ%</th></tr>{rows_low}</table>
""", unsafe_allow_html=True)

    st.markdown('<div style="height:24px"></div>', unsafe_allow_html=True)
    section('phân phối feature', 'So sánh phân phối giữa các nhóm')

    feature_to_compare = st.selectbox('Chọn feature', FEAT, index=0)

    fig = go.Figure()
    for q in sorted(filtered['quadrant'].unique()):
        sub_q = filtered[filtered['quadrant'] == q]
        fig.add_trace(go.Histogram(
            x=sub_q[feature_to_compare], name=q,
            marker_color=QUADRANT_COLORS.get(q, '#999'),
            opacity=0.6, histnorm='probability',
        ))
    fig.update_layout(
        barmode='overlay',
        title=dict(text=f'Phân phối · {feature_to_compare}',
                     font=dict(family='Playfair Display', size=16, color='#1A2A47')),
        xaxis_title=feature_to_compare, yaxis_title='Probability',
        height=380, plot_bgcolor='#FBF8F2', paper_bgcolor='#F4EFE6',
        font=dict(family='IBM Plex Sans Condensed', color='#1A2A47'),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="iq-col-title">Sample 50 khách · {selected_q_profile}</div>',
                  unsafe_allow_html=True)
    show_cols = FEAT[:6] + ['uplift_max', 'response'] if 'uplift_max' in sub.columns else FEAT[:8]
    show_cols = [c for c in show_cols if c in sub.columns]
    st.dataframe(sub[show_cols].head(50), use_container_width=True, height=300)


# ───────────────── TAB 4: MARKETING PLAN ─────────────────
with tab4:
    section('marketing plan', 'Hành động đề xuất theo từng nhóm',
            'Mỗi quadrant cần chiến lược riêng — không gửi đại trà.')

    plans = {
        'Persuadable': {
            'mark': '✓',
            'action': 'GỬI EMAIL — Mens E-Mail ưu tiên',
            'reason': 'Uplift cao, response baseline thấp → email kích hoạt mua hàng.',
            'channel': 'Email + có thể thêm SMS reminder',
            'frequency': 'Hàng tháng (không spam)',
            'expected_roi': 'Cao — uplift +0.6% đến +1.0% so với không làm gì',
        },
        'Sure Thing': {
            'mark': '⚠',
            'action': 'KHÔNG GỬI promotional email',
            'reason': 'Họ tự mua mà không cần ưu đãi → tiết kiệm chi phí.',
            'channel': 'Chỉ gửi newsletter thông tin sản phẩm mới',
            'frequency': 'Hàng quý',
            'expected_roi': 'Tiết kiệm chi phí — không spam khách trung thành',
        },
        'Lost Cause': {
            'mark': '✕',
            'action': 'KHÔNG GỬI promotional email',
            'reason': 'Uplift thấp + response thấp → email không hiệu quả.',
            'channel': 'Tái kích hoạt qua call center, partnership',
            'frequency': 'Chiến dịch tái kích hoạt năm 1-2 lần',
            'expected_roi': 'Thấp — cần test campaign khác',
        },
        'Sleeping Dog': {
            'mark': '⛔',
            'action': 'TUYỆT ĐỐI KHÔNG GỬI promotional email',
            'reason': 'Email gây phản tác dụng — họ giảm mua hàng nếu nhận email.',
            'channel': 'Tránh tất cả promotional; chỉ transactional',
            'frequency': 'Zero promotional contact',
            'expected_roi': 'Tiết kiệm + tránh churn',
        },
    }

    for q, plan in plans.items():
        n_q = int((filtered['quadrant'] == q).sum())
        if n_q == 0:
            continue
        color = QUADRANT_COLORS[q]
        pct = n_q / len(filtered) * 100

        st.markdown(f"""
<div class="iq-quadrant-card" style="border-left-color:{color}">
<div style="display:flex;justify-content:space-between;align-items:flex-start;gap:24px;flex-wrap:wrap">
<div style="flex:0 0 180px;text-align:center;background:{color};color:#F4EFE6;padding:18px 14px">
<div style="font-family:'Playfair Display',serif;font-size:44px;font-weight:900;line-height:1">{plan['mark']}</div>
<div style="font-family:'Playfair Display',serif;font-size:30px;font-weight:900;margin-top:6px">{n_q:,}</div>
<div style="font-family:'IBM Plex Mono',monospace;font-size:10px;opacity:0.85;margin-top:4px;letter-spacing:.1em">{pct:.1f}% FILTERED</div>
</div>
<div style="flex:1;min-width:260px">
<div style="font-family:'Playfair Display',serif;font-size:24px;font-weight:700;color:{color};margin-bottom:8px">{q}</div>
<div style="font-family:'IBM Plex Sans Condensed',sans-serif;font-size:13px;line-height:1.8;color:#1A2A47">
<b style="color:#B22234;letter-spacing:.08em;text-transform:uppercase;font-size:10px;font-family:'IBM Plex Mono',monospace">▸ Action</b> · {plan['action']}<br>
<b style="color:#B22234;letter-spacing:.08em;text-transform:uppercase;font-size:10px;font-family:'IBM Plex Mono',monospace">▸ Lý do</b> · {plan['reason']}<br>
<b style="color:#B22234;letter-spacing:.08em;text-transform:uppercase;font-size:10px;font-family:'IBM Plex Mono',monospace">▸ Kênh</b> · {plan['channel']}<br>
<b style="color:#B22234;letter-spacing:.08em;text-transform:uppercase;font-size:10px;font-family:'IBM Plex Mono',monospace">▸ Tần suất</b> · {plan['frequency']}<br>
<b style="color:#B22234;letter-spacing:.08em;text-transform:uppercase;font-size:10px;font-family:'IBM Plex Mono',monospace">▸ Expected ROI</b> · {plan['expected_roi']}
</div>
</div>
</div>
</div>
<div style="height:12px"></div>
""", unsafe_allow_html=True)

    plan_export = pd.DataFrame.from_dict(plans, orient='index').reset_index()
    plan_export.columns = ['Quadrant', 'Mark', 'Action', 'Reason', 'Channel', 'Frequency', 'ROI']
    plan_export['N_khach'] = [
        int((filtered['quadrant'] == q).sum()) for q in plans.keys()
    ]
    csv_bytes = plan_export.to_csv(index=False).encode('utf-8')
    st.download_button(
        '▼  Download Marketing Plan (CSV)',
        csv_bytes, 'marketing_action_plan.csv', 'text/csv',
    )

st.markdown('</div>', unsafe_allow_html=True)

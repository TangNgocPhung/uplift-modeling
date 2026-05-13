"""
Trang 4 — Persona Explorer: khám phá 4 nhóm Persuadable / Sure Thing /
Lost Cause / Sleeping Dog với filter và visualization.
"""
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from utils.load_models import load_test_data, load_persona_profile, FEAT
from utils.policy import QUADRANT_COLORS, QUADRANT_RECOMMENDATION
from utils.plots import quadrant_pie, quadrant_scatter

st.set_page_config(page_title='Persona Explorer', page_icon='👥', layout='wide')

st.title('👥 Persona Explorer')
st.caption('Khám phá 4 nhóm khách hàng — đặc trưng, hành vi, khuyến nghị marketing')

# === Load data ===
test_df = load_test_data()
persona_df = load_persona_profile()

if test_df is None:
    st.error('❌ Cần file `test_quadrant_final.parquet`. Quay lại trang chủ.')
    st.stop()

# Verify columns
if 'quadrant' not in test_df.columns:
    st.error('Test data không có cột `quadrant`. Chạy lại Bước 9 trong notebook.')
    st.stop()

# === Sidebar filters ===
with st.sidebar:
    st.subheader('🔍 Filter')

    # Quadrant filter
    available_quadrants = sorted(test_df['quadrant'].unique().tolist())
    selected_q = st.multiselect(
        'Chọn quadrant',
        available_quadrants,
        default=available_quadrants,
    )

    # Recency
    rec_min, rec_max = int(test_df['recency'].min()), int(test_df['recency'].max())
    rec_range = st.slider('Recency (tháng)', rec_min, rec_max, (rec_min, rec_max))

    # Womens / Newbie
    womens_filter = st.radio('Womens', ['Tất cả', 'Có (=1)', 'Không (=0)'])
    newbie_filter = st.radio('Newbie', ['Tất cả', 'Có (=1)', 'Không (=0)'])

    # Channel
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

st.info(f'🔎 Filter còn lại: **{len(filtered):,}** khách / {len(test_df):,} total')

if len(filtered) == 0:
    st.warning('Không có khách hàng nào khớp filter. Hãy nới lỏng điều kiện.')
    st.stop()

# === Tab layout ===
tab1, tab2, tab3, tab4 = st.tabs([
    '📊 Overview', '🗺️ Bản đồ Persona', '📋 Profile chi tiết', '🎯 Marketing Plan'
])

# ===== TAB 1: OVERVIEW =====
with tab1:
    col1, col2 = st.columns([1, 1])

    with col1:
        # Pie chart
        counts = filtered['quadrant'].value_counts().to_dict()
        st.plotly_chart(quadrant_pie(counts, QUADRANT_COLORS),
                          use_container_width=True)

    with col2:
        st.subheader('📊 Thống kê filtered')
        for q in ['Persuadable', 'Sure Thing', 'Lost Cause', 'Sleeping Dog']:
            n_q = (filtered['quadrant'] == q).sum()
            pct = n_q / len(filtered) * 100 if len(filtered) > 0 else 0
            color = QUADRANT_COLORS.get(q, '#999')
            st.markdown(f"""
            <div style='background-color: {color}15; border-left: 4px solid {color};
                        padding: 0.75rem 1rem; margin-bottom: 0.5rem; border-radius: 4px;'>
                <b style='color: {color}'>{q}</b>: {n_q:,} khách ({pct:.1f}%)<br>
                <span style='color: #6B7280; font-size: 0.85rem;'>
                    {QUADRANT_RECOMMENDATION.get(q, '')}
                </span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('---')

    # Metrics row
    if 'uplift_max' in filtered.columns:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric('Mean uplift', f"{filtered['uplift_max'].mean():.4f}")
        if 'response' in filtered.columns:
            col2.metric('Mean response', f"{filtered['response'].mean():.4f}")
        col3.metric('Mean recency', f"{filtered['recency'].mean():.1f}")
        col4.metric('Mean history', f"{filtered['history_log'].mean():.2f}")

# ===== TAB 2: PERSONA MAP =====
with tab2:
    st.subheader('🗺️ Bản đồ 2D — Uplift vs Response')

    if 'uplift_max' in filtered.columns and 'response' in filtered.columns:
        st.plotly_chart(quadrant_scatter(filtered), use_container_width=True)

        st.markdown("""
        **Đọc bản đồ**:
        - Trục X = predicted response (P[Y=1|control]) — "khả năng tự mua nếu không gửi"
        - Trục Y = predicted uplift (max τ) — "phần tăng thêm conversion nhờ email"
        - 🟢 **Persuadable** (góc trên trái): uplift cao, response thấp → **GỬI**
        - 🔵 **Sure Thing** (góc dưới phải): response cao, uplift thấp → tự mua
        - ⚪ **Lost Cause** (góc dưới trái): cả 2 thấp → bỏ qua
        - 🔴 **Sleeping Dog** (vùng đỏ): uplift âm/rất thấp → **KHÔNG GỬI**
        """)
    else:
        st.warning('Test data thiếu cột uplift_max hoặc response.')

# ===== TAB 3: PROFILE CHI TIẾT =====
with tab3:
    st.subheader('📋 Persona Profile theo từng quadrant')

    # Compute mean per quadrant from filtered
    profile = filtered.groupby('quadrant')[FEAT].mean().round(3)
    pop_mean = filtered[FEAT].mean()
    diff = ((profile - pop_mean) / pop_mean * 100).round(1)

    selected_q_profile = st.selectbox(
        'Chọn quadrant để xem chi tiết',
        sorted(filtered['quadrant'].unique()),
    )

    sub = filtered[filtered['quadrant'] == selected_q_profile]
    n_sub = len(sub)
    color = QUADRANT_COLORS.get(selected_q_profile, '#999')

    st.markdown(f"""
    <div style='background-color: {color}20; padding: 1rem; border-radius: 8px;
                border-left: 5px solid {color};'>
        <h3 style='color: {color}; margin: 0;'>{selected_q_profile} — {n_sub:,} khách</h3>
        <p style='margin: 0.5rem 0 0 0;'>{QUADRANT_RECOMMENDATION.get(selected_q_profile, '')}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('### 📊 Đặc trưng (so với population trong filter)')

    if selected_q_profile in profile.index:
        sub_diff = diff.loc[selected_q_profile].sort_values(ascending=False)

        # Top 5 cao hơn
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('**🔼 Cao hơn population**')
            for f, d in sub_diff.head(5).items():
                if d > 0:
                    st.write(f'- `{f}`: {profile.loc[selected_q_profile, f]:.3f} (+{d:.0f}%)')

        with col2:
            st.markdown('**🔽 Thấp hơn population**')
            for f, d in sub_diff.tail(5).items():
                if d < 0:
                    st.write(f'- `{f}`: {profile.loc[selected_q_profile, f]:.3f} ({d:.0f}%)')

    # Feature distribution comparison
    st.markdown('### 📈 Phân phối features (so sánh với các nhóm khác)')

    feature_to_compare = st.selectbox('Chọn feature', FEAT, index=0)

    fig = go.Figure()
    for q in sorted(filtered['quadrant'].unique()):
        sub_q = filtered[filtered['quadrant'] == q]
        fig.add_trace(go.Histogram(
            x=sub_q[feature_to_compare],
            name=q,
            marker_color=QUADRANT_COLORS.get(q, '#999'),
            opacity=0.6,
            histnorm='probability',
        ))
    fig.update_layout(
        barmode='overlay',
        title=f'Phân phối `{feature_to_compare}` theo quadrant',
        xaxis_title=feature_to_compare,
        yaxis_title='Probability',
        height=400,
    )
    st.plotly_chart(fig, use_container_width=True)

    # Sample table
    st.markdown(f'### 👁️ Sample 50 khách trong nhóm {selected_q_profile}')
    show_cols = FEAT[:6] + ['uplift_max', 'response'] if 'uplift_max' in sub.columns else FEAT[:8]
    show_cols = [c for c in show_cols if c in sub.columns]
    st.dataframe(sub[show_cols].head(50), use_container_width=True, height=300)

# ===== TAB 4: MARKETING PLAN =====
with tab4:
    st.subheader('🎯 Marketing Action Plan theo từng quadrant')

    plans = {
        'Persuadable': {
            'icon': '✅',
            'action': 'GỬI EMAIL — Mens E-Mail ưu tiên',
            'reason': 'Uplift cao, response baseline thấp → email kích hoạt mua hàng',
            'channel': 'Email + có thể thêm SMS reminder',
            'frequency': 'Hàng tháng (không spam)',
            'expected_roi': 'Cao — uplift +0.6% đến +1.0% so với không làm gì',
        },
        'Sure Thing': {
            'icon': '⚠️',
            'action': 'KHÔNG GỬI promotional email',
            'reason': 'Họ tự mua mà không cần ưu đãi → tiết kiệm chi phí',
            'channel': 'Chỉ gửi newsletter thông tin sản phẩm mới',
            'frequency': 'Hàng quý',
            'expected_roi': 'Tiết kiệm chi phí — không spam khách trung thành',
        },
        'Lost Cause': {
            'icon': '❌',
            'action': 'KHÔNG GỬI promotional email',
            'reason': 'Uplift thấp + response thấp → email không hiệu quả',
            'channel': 'Tái kích hoạt qua call center, partnership',
            'frequency': 'Chiến dịch tái kích hoạt năm 1-2 lần',
            'expected_roi': 'Thấp — cần test campaign khác',
        },
        'Sleeping Dog': {
            'icon': '🚫',
            'action': 'TUYỆT ĐỐI KHÔNG GỬI promotional email',
            'reason': 'Email gây phản tác dụng — họ giảm mua hàng nếu nhận email',
            'channel': 'Tránh tất cả promotional; chỉ transactional',
            'frequency': 'Zero promotional contact',
            'expected_roi': 'Tiết kiệm + tránh churn',
        },
    }

    for q, plan in plans.items():
        n_q = (filtered['quadrant'] == q).sum()
        if n_q == 0: continue
        color = QUADRANT_COLORS[q]

        with st.expander(f"{plan['icon']} **{q}** — {n_q:,} khách trong filter", expanded=True):
            col1, col2 = st.columns([1, 2])
            with col1:
                st.markdown(f"""
                <div style='background-color: {color}; padding: 1rem; border-radius: 8px;
                            color: white; text-align: center;'>
                    <div style='font-size: 3rem;'>{plan['icon']}</div>
                    <h3 style='margin: 0; color: white;'>{n_q:,}</h3>
                    <p style='margin: 0; opacity: 0.9;'>{n_q/len(filtered)*100:.1f}% filtered</p>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                **🎬 Action**: {plan['action']}

                **💡 Lý do**: {plan['reason']}

                **📡 Kênh**: {plan['channel']}

                **🔄 Tần suất**: {plan['frequency']}

                **📈 Expected ROI**: {plan['expected_roi']}
                """)

    # Download action plan as CSV
    plan_export = pd.DataFrame.from_dict(plans, orient='index').reset_index()
    plan_export.columns = ['Quadrant', 'Icon', 'Action', 'Reason', 'Channel', 'Frequency', 'ROI']
    plan_export['N_khach'] = [
        (filtered['quadrant'] == q).sum() for q in plans.keys()
    ]
    csv_bytes = plan_export.to_csv(index=False).encode('utf-8')
    st.download_button(
        '📥 Download Marketing Plan (CSV)',
        csv_bytes, 'marketing_action_plan.csv', 'text/csv',
    )

"""
Trang 3 — Economic Simulator (Editorial design v4)
Slider tham số kinh tế → real-time profit comparison giữa các chính sách.
"""
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from utils.load_models import load_causal_forest, load_test_data, predict_cate, FEAT
from utils.policy import (optimal_action, ips_policy_value,
                           policy_no_treat, policy_treat_all,
                           policy_random, policy_uplift_top)
from utils.plots import profit_curve_plotly, policy_comparison_bar
from utils.editorial import (inject_css, render_masthead, render_sidebar_header,
                              render_break_even, sidebar_section_title,
                              banner, section, error_card)

st.set_page_config(
    page_title='Economic Simulator — UpliftIQ',
    page_icon='▲',
    layout='wide',
    initial_sidebar_state='expanded',
)

inject_css()


# ═════════════════════════════════════════════════════════════
# LOAD DATA + MODEL
# ═════════════════════════════════════════════════════════════
test_df = load_test_data()
cf_model = load_causal_forest()

if test_df is None or cf_model is None:
    render_masthead(3, 'ECONOMIC SIMULATOR',
                    'Mô phỏng', 'kinh tế',
                    'Slider cost/profit · Real-time profit comparison')
    error_card('Thiếu file dữ liệu hoặc mô hình',
               'Cần cả hai file <code>cf_final.pkl</code> và '
               '<code>test_quadrant_FINAL.parquet</code> trong thư mục <code>./models/</code>. '
               'Quay lại trang chủ để xem trạng thái artifacts.')
    st.stop()


# Lấy CATE đã có sẵn trong test_df, hoặc compute nếu chưa có
if 'cate_men' not in test_df.columns:
    X_test = test_df[FEAT].values.astype(np.float32)
    cate = predict_cate(cf_model, X_test)
    test_df = test_df.copy()
    test_df['cate_men'] = cate[:, 0]
    test_df['cate_women'] = cate[:, 1]
else:
    cate = test_df[['cate_men', 'cate_women']].values

n = len(test_df)
T_actual = test_df['actual_T'].values if 'actual_T' in test_df.columns else None
y_actual = test_df['actual_y'].values if 'actual_y' in test_df.columns else None


# ═════════════════════════════════════════════════════════════
# PAGE HEADER
# ═════════════════════════════════════════════════════════════
render_masthead(3, 'ECONOMIC SIMULATOR',
                'Mô phỏng', 'kinh tế',
                'Slider cost/profit → Real-time profit comparison giữa các policy')


# ═════════════════════════════════════════════════════════════
# SIDEBAR
# ═════════════════════════════════════════════════════════════
with st.sidebar:
    render_sidebar_header(active_idx=3)

    sidebar_section_title('⚙ Tham số kinh tế')
    profit_per_conv = st.slider(
        'Lợi nhuận / conversion (VND)',
        min_value=50_000, max_value=500_000, value=200_000, step=10_000,
    )
    cost_per_email = st.slider(
        'Chi phí / email (VND)',
        min_value=500, max_value=20_000, value=5_000, step=500,
    )

    threshold = cost_per_email / profit_per_conv
    render_break_even(threshold)

    sidebar_section_title('▣ Thông tin data')
    info_rows = [('Test size', f'{n:,} khách')]
    if y_actual is not None:
        info_rows.append(('Tỷ lệ conversion', f'{y_actual.mean():.4f}'))
    info_html = ''.join(
        f'<div style="display:flex;justify-content:space-between;font-family:\'IBM Plex Mono\',monospace;font-size:11px;color:#F4EFE6;padding:4px 0;border-bottom:1px solid #2C3E5C">'
        f'<span style="color:#C7A270">{k}</span><span>{v}</span></div>'
        for k, v in info_rows
    )
    st.markdown(info_html, unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════
# BODY
# ═════════════════════════════════════════════════════════════
st.markdown('<div class="iq-body">', unsafe_allow_html=True)

# Pre-compute tất cả policies
policies_actions = {
    '1. Không gửi ai':        policy_no_treat(n),
    '2. Gửi tất cả Mens':     policy_treat_all(n, 1),
    '3. Gửi tất cả Womens':   policy_treat_all(n, 2),
    '4. Random 30%':          policy_random(n, 0.3),
    '5. Uplift top 30%':      policy_uplift_top(cate, 0.3),
    '★ 6. Uplift threshold':  optimal_action(cate, profit_per_conv, cost_per_email),
}

policy_df = None
if T_actual is not None and y_actual is not None:
    policy_results = []
    for name, a in policies_actions.items():
        pv = ips_policy_value(a, T_actual, y_actual,
                                profit=profit_per_conv, cost=cost_per_email)
        n_treated = int((a != 0).sum())
        policy_results.append({
            'Policy': name,
            'N_treated': n_treated,
            '%_treated': f'{n_treated/n*100:.1f}%',
            'Profit/user (VND)': round(pv),
            'Total profit (VND)': round(pv * n),
        })
    policy_df = pd.DataFrame(policy_results)


# ═════════════════════════════════════════════════════════════
# TABS
# ═════════════════════════════════════════════════════════════
tab1, tab2, tab3 = st.tabs(['So sánh policies', 'Profit-vs-k% curve', 'Sensitivity'])

# ───────────────── TAB 1 ─────────────────
with tab1:
    section('so sánh chính sách', 'Sáu chiến lược phân bổ email',
            'So sánh policy uplift-driven với baseline naive trên test set qua IPS evaluation.')

    if policy_df is None:
        banner('warning',
               '⚠ Test data không có cột <code>actual_T</code> / <code>actual_y</code> — '
               'không thể IPS evaluate. Chạy lại bước 9 trong notebook để có actuals.')
    else:
        # Bảng editorial
        best_idx = int(policy_df['Profit/user (VND)'].idxmax())
        table_html = '<table class="iq-dt">'
        table_html += ('<tr><th>Policy</th><th style="text-align:right">N treated</th>'
                       '<th style="text-align:right">% treated</th>'
                       '<th style="text-align:right">Profit / user</th>'
                       '<th style="text-align:right">Total profit</th></tr>')
        for i, r in policy_df.iterrows():
            cls = 'highlight' if i == best_idx else ''
            table_html += (f'<tr class="{cls}"><td>{r["Policy"]}</td>'
                           f'<td class="num">{r["N_treated"]:,}</td>'
                           f'<td class="num">{r["%_treated"]}</td>'
                           f'<td class="num">{r["Profit/user (VND)"]:,}</td>'
                           f'<td class="num">{r["Total profit (VND)"]:,}</td></tr>')
        table_html += '</table>'
        st.markdown(table_html, unsafe_allow_html=True)

        st.plotly_chart(policy_comparison_bar(policy_df), use_container_width=True)

        # Highlight best
        best = policy_df.iloc[best_idx]
        banner('success',
               f'🏆 <b>Chính sách tốt nhất</b>: {best["Policy"]} — '
               f'profit/user <code>{best["Profit/user (VND)"]:,} VND</code>, '
               f'tổng <code>{best["Total profit (VND)"]:,} VND</code> '
               f'với {best["N_treated"]:,} khách được gửi ({best["%_treated"]}).')

        # Compare uplift vs treat-all
        uplift_pv = policy_df.iloc[5]['Profit/user (VND)']
        treat_all_pv = max(policy_df.iloc[1]['Profit/user (VND)'],
                            policy_df.iloc[2]['Profit/user (VND)'])
        lift_vs_all = uplift_pv - treat_all_pv

        st.markdown(f"""
<div class="iq-lead cols2">
<div class="iq-ls">
<div class="v sm">{uplift_pv:,}</div>
<div class="l">Uplift threshold · profit / user (VND)</div>
<div class="s">{lift_vs_all:+,} VND vs treat-all</div>
</div>
<div class="iq-ls">
<div class="v sm sage">{lift_vs_all * 1_000_000:+,.0f}</div>
<div class="l">Tiết kiệm cho 1M khách (VND)</div>
<div class="s">scale up benefit</div>
</div>
</div>
""", unsafe_allow_html=True)


# ───────────────── TAB 2 ─────────────────
with tab2:
    section('profit-vs-k% curve', 'Tìm k* tối ưu',
            'Lợi nhuận thay đổi thế nào khi chỉ gửi top k% theo uplift score.')

    if T_actual is None:
        banner('warning', '⚠ Cần <code>actual_T</code> + <code>actual_y</code> để vẽ curve.')
    else:
        ks = list(range(0, 101, 5))
        profits_uplift, profits_random = [], []
        for k_pct in ks:
            a_u = policy_uplift_top(cate, k_pct / 100)
            a_r = policy_random(n, k_pct / 100)
            profits_uplift.append(ips_policy_value(
                a_u, T_actual, y_actual,
                profit=profit_per_conv, cost=cost_per_email))
            profits_random.append(ips_policy_value(
                a_r, T_actual, y_actual,
                profit=profit_per_conv, cost=cost_per_email))

        k_opt = ks[int(np.argmax(profits_uplift))]
        max_profit = max(profits_uplift)
        lift_vs_all = max_profit - profits_uplift[-1]

        c1, c2 = st.columns([3, 1])
        with c1:
            st.plotly_chart(profit_curve_plotly(ks, profits_uplift,
                                                  profits_random, k_opt),
                              use_container_width=True)
        with c2:
            st.markdown(f"""
<div style="border-top:3px solid #1A2A47;padding-top:12px">
<div style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:#B22234;letter-spacing:.2em;text-transform:uppercase">k* tối ưu</div>
<div style="font-family:'Playfair Display',serif;font-size:48px;font-weight:900;color:#1A2A47;line-height:1">{k_opt}%</div>
<div style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:#8C7B6B;margin-top:4px">top % theo uplift score</div>

<div style="margin-top:20px;border-top:1px solid #C7A270;padding-top:12px">
<div style="font-family:'IBM Plex Sans Condensed',sans-serif;font-size:11px;color:#4A6378;text-transform:uppercase;letter-spacing:.1em;font-weight:600">Max profit / user</div>
<div style="font-family:'IBM Plex Mono',monospace;font-size:18px;color:#6B8068;font-weight:600">{max_profit:,.0f} VND</div>
</div>

<div style="margin-top:14px;border-top:1px solid #C7A270;padding-top:12px">
<div style="font-family:'IBM Plex Sans Condensed',sans-serif;font-size:11px;color:#4A6378;text-transform:uppercase;letter-spacing:.1em;font-weight:600">Treat-all (k=100%)</div>
<div style="font-family:'IBM Plex Mono',monospace;font-size:16px;color:#1A2A47">{profits_uplift[-1]:,.0f} VND</div>
</div>

<div style="margin-top:14px;border-top:1px solid #C7A270;padding-top:12px">
<div style="font-family:'IBM Plex Sans Condensed',sans-serif;font-size:11px;color:#B22234;text-transform:uppercase;letter-spacing:.1em;font-weight:700">Lift vs treat-all</div>
<div style="font-family:'IBM Plex Mono',monospace;font-size:18px;color:#B22234;font-weight:600">{lift_vs_all:+,.0f} VND</div>
</div>
</div>
""", unsafe_allow_html=True)

        st.markdown(f"""
<div class="iq-insight">
💡 <b>Insight</b>: Chỉ cần gửi email cho <b>top {k_opt}%</b> khách hàng theo uplift score
để đạt lợi nhuận tối đa. Gửi nhiều hơn = tốn cost không tạo thêm conversion (đường cong đi xuống sau k*).
</div>
""", unsafe_allow_html=True)


# ───────────────── TAB 3 ─────────────────
with tab3:
    section('sensitivity analysis', 'Profit theo các kịch bản cost / profit',
            'Lợi nhuận thay đổi thế nào khi tham số kinh tế khác đi?')

    if T_actual is None:
        banner('warning', '⚠ Cần actuals để chạy sensitivity.')
    else:
        with st.spinner('Đang tính sensitivity...'):
            costs = [1_000, 2_000, 5_000, 10_000, 20_000]
            profits_vals = [100_000, 200_000, 300_000]

            sens_data = []
            for prof in profits_vals:
                for c in costs:
                    a = optimal_action(cate, profit=prof, cost=c)
                    pv = ips_policy_value(a, T_actual, y_actual,
                                            profit=prof, cost=c)
                    n_send = int((a != 0).sum())
                    sens_data.append({
                        'Profit/conv (VND)': prof,
                        'Cost/email (VND)': c,
                        '%_treated': round(n_send / n * 100, 1),
                        'Profit/user (VND)': round(pv),
                        'Break-even τ': round(c / prof, 4),
                    })
            sens_df = pd.DataFrame(sens_data)

        pivot = sens_df.pivot(index='Profit/conv (VND)', columns='Cost/email (VND)',
                                values='Profit/user (VND)')

        fig = go.Figure(data=go.Heatmap(
            z=pivot.values, x=pivot.columns, y=pivot.index,
            colorscale=[[0, '#B22234'], [0.5, '#F4EFE6'], [1, '#6B8068']], zmid=0,
            text=pivot.values, texttemplate='%{text:,}',
            textfont={'size': 11, 'family': 'IBM Plex Mono'},
            colorbar=dict(title='Profit/user',
                            tickfont=dict(family='IBM Plex Mono', size=10)),
        ))
        fig.update_layout(
            title=dict(text='Heatmap · Profit / user theo (Cost, Profit)',
                         font=dict(family='Playfair Display', size=18, color='#1A2A47')),
            xaxis_title='Cost / email (VND)',
            yaxis_title='Profit / conversion (VND)',
            height=400, plot_bgcolor='#FBF8F2', paper_bgcolor='#F4EFE6',
            font=dict(family='IBM Plex Sans Condensed', color='#1A2A47'),
        )
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(sens_df, use_container_width=True, hide_index=True)

        st.markdown("""
<div class="iq-insight">
📐 <b>Đọc bảng</b>: <code>% treated</code> giảm khi cost tăng — uplift modeling tự động
chọn lọc khách hàng có uplift đủ cao để bù chi phí. Đây chính là giá trị
cốt lõi của uplift modeling so với gửi đại trà.
</div>
""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════
# FOOTER SUMMARY
# ═════════════════════════════════════════════════════════════
st.markdown('<div style="height:24px"></div>', unsafe_allow_html=True)
st.markdown(f"""
<div style="border-top:2px solid #1A2A47;padding:14px 0;display:flex;justify-content:space-between;flex-wrap:wrap;gap:12px;font-family:'IBM Plex Mono',monospace;font-size:10px;color:#6B4E5C;letter-spacing:.08em">
<span>PROFIT/CONV · {profit_per_conv:,} VND</span>
<span>COST/EMAIL · {cost_per_email:,} VND</span>
<span>BREAK-EVEN τ · {threshold:.4f}</span>
<span>N TEST · {n:,}</span>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

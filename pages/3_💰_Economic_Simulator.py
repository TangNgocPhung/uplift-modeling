"""
Trang 3 — Economic Simulator (Editorial design v4)
Slider tham số kinh tế → real-time profit comparison giữa các chính sách.
"""
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from utils.load_models import (load_causal_forest, load_response_model,
                                load_test_data, predict_cate, predict_response, FEAT)
from utils.policy import (optimal_action, ips_policy_value,
                           policy_no_treat, policy_treat_all,
                           policy_random, policy_uplift_top, policy_response_top)
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

# Response scores — ưu tiên cột pre-computed trong test_df, fallback predict_response
if 'response' in test_df.columns:
    response_scores = test_df['response'].values
else:
    rm = load_response_model()
    if rm is not None:
        X_test_full = test_df[FEAT].values.astype(np.float32)
        response_scores = predict_response(rm, X_test_full)
    else:
        response_scores = None


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

# Pre-compute tất cả policies — bao gồm baseline Response Model để head-to-head
policies_actions = {
    '1. Không gửi ai':        policy_no_treat(n),
    '2. Gửi tất cả Mens':     policy_treat_all(n, 1),
    '3. Gửi tất cả Womens':   policy_treat_all(n, 2),
    '4. Random 30%':          policy_random(n, 0.3),
}
if response_scores is not None:
    policies_actions['5. Response top 30% (predictive)'] = policy_response_top(response_scores, 0.3, treatment=1)
policies_actions['6. Uplift top 30% (causal)'] = policy_uplift_top(cate, 0.3)
policies_actions['★ 7. Uplift threshold (causal)'] = optimal_action(cate, profit_per_conv, cost_per_email)

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
    n_pol = len(policies_actions)
    section('so sánh chính sách', f'{n_pol} chiến lược phân bổ email',
            'So sánh policy uplift-driven (causal) với Response model (predictive) '
            'và các baseline naive — đánh giá bằng IPS estimator trên test set.')

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

        # Lookup theo tên — robust khi số policies đổi
        def _pv(name_contains):
            mask = policy_df['Policy'].str.contains(name_contains, regex=False)
            return int(policy_df.loc[mask, 'Profit/user (VND)'].iloc[0]) if mask.any() else None

        uplift_thresh_pv = _pv('Uplift threshold')
        uplift_top_pv = _pv('Uplift top 30%')
        response_top_pv = _pv('Response top 30%')
        treat_men_pv = _pv('Gửi tất cả Mens')
        treat_women_pv = _pv('Gửi tất cả Womens')
        treat_all_pv = max(treat_men_pv or 0, treat_women_pv or 0)

        lift_vs_all = (uplift_thresh_pv or 0) - treat_all_pv

        # ─── HEADLINE: Uplift vs Response (Causal vs Predictive) ───
        if response_top_pv is not None and uplift_top_pv is not None:
            lift_vs_response = uplift_top_pv - response_top_pv
            lift_pct = (lift_vs_response / abs(response_top_pv) * 100) if response_top_pv else 0
            verdict = ('Causal ML thắng' if lift_vs_response > 0
                       else 'Response model thắng' if lift_vs_response < 0
                       else 'Hoà')
            verdict_color = '#6B8068' if lift_vs_response > 0 else '#B22234' if lift_vs_response < 0 else '#4A6378'

            st.markdown(f"""
<div class="iq-rub" style="margin-top:18px">// head-to-head: causal vs predictive (cùng k=30%)</div>
<div class="iq-lead cols3">
<div class="iq-ls">
<div class="v sm">{response_top_pv:,}</div>
<div class="l">Response top 30% · profit / user</div>
<div class="s">baseline predictive — "ai sẽ mua"</div>
</div>
<div class="iq-ls">
<div class="v sm red">{uplift_top_pv:,}</div>
<div class="l">Uplift top 30% · profit / user</div>
<div class="s">causal — "ai mua NHỜ email"</div>
</div>
<div class="iq-ls">
<div class="v sm" style="color:{verdict_color}">{lift_vs_response:+,}</div>
<div class="l" style="color:{verdict_color}">{verdict} ({lift_pct:+.1f}%)</div>
<div class="s">VND/user · giá trị causal modeling</div>
</div>
</div>
""", unsafe_allow_html=True)

            if lift_vs_response > 0:
                banner('success',
                       f'🎯 <b>Bằng chứng cho thesis</b>: Cùng số lượng email gửi đi (top 30%), '
                       f'uplift modeling tạo thêm <code>{lift_vs_response:+,} VND/user</code> '
                       f'so với response model truyền thống — '
                       f'<b>+{lift_vs_response * 1_000_000:,.0f} VND</b> cho 1 triệu khách.')
            else:
                banner('warning',
                       f'⚠ Trên test set hiện tại, uplift top-30 chưa vượt response top-30. '
                       f'Hai khả năng: (a) propensity ước lượng sai → IPS biased; '
                       f'(b) cost/profit hiện tại làm threshold không tách được. '
                       f'Thử điều chỉnh slider hoặc xem Tab 2 để có bức tranh đầy đủ theo k%.')

        # ─── Uplift vs treat-all (giữ original) ───
        st.markdown(f"""
<div class="iq-rub" style="margin-top:18px">// uplift vs gửi đại trà</div>
<div class="iq-lead cols2">
<div class="iq-ls">
<div class="v sm">{uplift_thresh_pv:,}</div>
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
        profits_uplift, profits_random, profits_response = [], [], []
        for k_pct in ks:
            a_u = policy_uplift_top(cate, k_pct / 100)
            a_r = policy_random(n, k_pct / 100)
            profits_uplift.append(ips_policy_value(
                a_u, T_actual, y_actual,
                profit=profit_per_conv, cost=cost_per_email))
            profits_random.append(ips_policy_value(
                a_r, T_actual, y_actual,
                profit=profit_per_conv, cost=cost_per_email))
            if response_scores is not None:
                a_resp = policy_response_top(response_scores, k_pct / 100, treatment=1)
                profits_response.append(ips_policy_value(
                    a_resp, T_actual, y_actual,
                    profit=profit_per_conv, cost=cost_per_email))

        k_opt = ks[int(np.argmax(profits_uplift))]
        max_profit = max(profits_uplift)
        lift_vs_all = max_profit - profits_uplift[-1]
        # Lift uplift vs response tại k tối ưu
        if response_scores is not None:
            lift_vs_resp_at_kopt = profits_uplift[ks.index(k_opt)] - profits_response[ks.index(k_opt)]
        else:
            lift_vs_resp_at_kopt = None

        c1, c2 = st.columns([3, 1])
        with c1:
            st.plotly_chart(
                profit_curve_plotly(ks, profits_uplift, profits_random, k_opt,
                                      profits_response=profits_response if response_scores is not None else None),
                use_container_width=True)
        with c2:
            lift_resp_block = ''
            if lift_vs_resp_at_kopt is not None:
                lift_color = '#6B8068' if lift_vs_resp_at_kopt > 0 else '#B22234'
                lift_resp_block = f"""
<div style="margin-top:14px;border-top:1px solid #C7A270;padding-top:12px">
<div style="font-family:'IBM Plex Sans Condensed',sans-serif;font-size:11px;color:{lift_color};text-transform:uppercase;letter-spacing:.1em;font-weight:700">Lift vs Response @ k*</div>
<div style="font-family:'IBM Plex Mono',monospace;font-size:18px;color:{lift_color};font-weight:600">{lift_vs_resp_at_kopt:+,.0f} VND</div>
<div style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:#8C7B6B;margin-top:2px">causal vs predictive</div>
</div>
"""
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
{lift_resp_block}
</div>
""", unsafe_allow_html=True)

        insight_extra = ''
        if response_scores is not None:
            response_max = max(profits_response)
            response_kopt = ks[int(np.argmax(profits_response))]
            insight_extra = (
                f'<br><br>📈 <b>So sánh với baseline Response model</b>: '
                f'Response top-k% đạt đỉnh {response_max:,.0f} VND/user tại k={response_kopt}% — '
                f'thấp hơn uplift {max_profit - response_max:+,.0f} VND/user. '
                f'Response model gửi cho khách <em>sẵn sàng mua</em> (bao gồm cả Sure Thing — '
                f'không cần email), trong khi uplift target đúng nhóm Persuadable.'
            )
        st.markdown(f"""
<div class="iq-insight">
💡 <b>Insight</b>: Chỉ cần gửi email cho <b>top {k_opt}%</b> khách hàng theo uplift score
để đạt lợi nhuận tối đa. Gửi nhiều hơn = tốn cost không tạo thêm conversion (đường cong đi xuống sau k*).
{insight_extra}
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

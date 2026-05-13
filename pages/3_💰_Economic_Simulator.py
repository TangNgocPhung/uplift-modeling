"""
Trang 3 — Economic Simulator: slider cost/profit, real-time profit-vs-k% curve.
"""
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from utils.load_models import load_causal_forest, load_test_data, predict_cate
from utils.policy import (optimal_action, ips_policy_value,
                           policy_no_treat, policy_treat_all,
                           policy_random, policy_uplift_top)
from utils.plots import profit_curve_plotly, policy_comparison_bar

st.set_page_config(page_title='Economic Simulator', page_icon='💰', layout='wide')

st.title('💰 Economic Simulator')
st.caption('Slider tham số kinh tế → Real-time profit comparison giữa các chính sách')

# === Load data + model ===
test_df = load_test_data()
cf_model = load_causal_forest()

if test_df is None or cf_model is None:
    st.error('❌ Cần file `cf_final.pkl` và `test_quadrant_final.parquet`. Quay lại trang chủ.')
    st.stop()

# Lấy CATE đã có sẵn trong test_df, hoặc compute nếu chưa có
if 'uplift_max' not in test_df.columns:
    st.warning('CATE chưa có trong test_df, đang compute...')
    from utils.load_models import FEAT
    X_test = test_df[FEAT].values.astype(np.float32)
    cate = predict_cate(cf_model, X_test)
    test_df = test_df.copy()
    test_df['cate_men'] = cate[:, 0]
    test_df['cate_women'] = cate[:, 1]
else:
    # Reconstruct CATE từ stored predictions
    if 'cate_men' not in test_df.columns:
        from utils.load_models import FEAT
        X_test = test_df[FEAT].values.astype(np.float32)
        cate = predict_cate(cf_model, X_test)
        test_df = test_df.copy()
        test_df['cate_men'] = cate[:, 0]
        test_df['cate_women'] = cate[:, 1]
    cate = test_df[['cate_men', 'cate_women']].values

n = len(test_df)
T_actual = test_df['actual_T'].values if 'actual_T' in test_df.columns else None
y_actual = test_df['actual_y'].values if 'actual_y' in test_df.columns else None

# === Sidebar: tham số ===
with st.sidebar:
    st.subheader('🎛️ Tham số kinh tế')

    profit_per_conv = st.slider(
        'Lợi nhuận / conversion (VND)',
        min_value=50_000, max_value=500_000, value=200_000, step=10_000,
        help='Lợi nhuận biên gross trên 1 đơn hàng convert thành công',
    )
    cost_per_email = st.slider(
        'Chi phí / email (VND)',
        min_value=500, max_value=20_000, value=5_000, step=500,
        help='Chi phí gửi 1 email + voucher khuyến mãi',
    )

    threshold = cost_per_email / profit_per_conv
    st.metric('Break-even threshold τ', f'{threshold:.4f}',
                help='Chỉ gửi email nếu uplift > ngưỡng này')

    st.markdown('---')
    st.subheader('📊 Thông tin data')
    st.metric('Test size', f'{n:,} khách')
    if y_actual is not None:
        st.metric('Tỷ lệ conversion', f'{y_actual.mean():.4f}')

# === Tính toán policies ===
@st.cache_data(ttl=10)
def compute_policies(_cate_tuple_shape, profit, cost, _T_actual_hash, _y_actual_hash):
    """Cache theo profit/cost — tránh recompute khi không thay đổi."""
    pass  # placeholder, không dùng cache vì np.array unhashable


# Tính tất cả policies
policies_actions = {
    '1. Không gửi ai':        policy_no_treat(n),
    '2. Gửi tất cả Mens':     policy_treat_all(n, 1),
    '3. Gửi tất cả Womens':   policy_treat_all(n, 2),
    '4. Random 30%':          policy_random(n, 0.3),
    '5. Uplift top 30%':      policy_uplift_top(cate, 0.3),
    '⭐ 6. Uplift threshold': optimal_action(cate, profit_per_conv, cost_per_email),
}

if T_actual is not None and y_actual is not None:
    # Có actual data → IPS evaluation
    policy_results = []
    for name, a in policies_actions.items():
        pv = ips_policy_value(a, T_actual, y_actual,
                                profit=profit_per_conv, cost=cost_per_email)
        n_treated = (a != 0).sum()
        policy_results.append({
            'Policy': name,
            'N_treated': n_treated,
            '%_treated': f'{n_treated/n*100:.1f}%',
            'Profit/user (VND)': round(pv),
            'Total profit (VND)': round(pv * n),
        })
    policy_df = pd.DataFrame(policy_results)

# === Tab layout ===
tab1, tab2, tab3 = st.tabs(['📊 So sánh policies', '📈 Profit-vs-k% Curve', '🔬 Sensitivity'])

with tab1:
    st.subheader('So sánh 6 chính sách phân bổ')

    if T_actual is not None:
        st.dataframe(policy_df, use_container_width=True, hide_index=True)
        st.plotly_chart(policy_comparison_bar(policy_df), use_container_width=True)

        # Highlight best
        best_idx = policy_df['Profit/user (VND)'].idxmax()
        best_policy = policy_df.iloc[best_idx]
        st.success(f"""
        🏆 **Chính sách tốt nhất**: {best_policy['Policy']}
        - Profit/user: **{best_policy['Profit/user (VND)']:,} VND**
        - Tổng profit: **{best_policy['Total profit (VND)']:,} VND**
        - Số khách gửi: {best_policy['N_treated']:,} ({best_policy['%_treated']})
        """)

        # Compare uplift vs treat-all
        uplift_pv = policy_df.iloc[5]['Profit/user (VND)']
        treat_all_pv = max(policy_df.iloc[1]['Profit/user (VND)'],
                            policy_df.iloc[2]['Profit/user (VND)'])
        lift_vs_all = uplift_pv - treat_all_pv

        col1, col2 = st.columns(2)
        with col1:
            st.metric('Uplift Threshold profit/user', f'{uplift_pv:,} VND',
                        f'{lift_vs_all:+,} VND vs treat-all')
        with col2:
            scale = 1_000_000
            saved = lift_vs_all * scale
            st.metric(f'Tiết kiệm khi áp dụng cho 1M khách',
                        f'{saved:+,.0f} VND',
                        delta_color='normal')
    else:
        st.warning('Test data không có cột actual_T/actual_y, không thể IPS evaluate.')


with tab2:
    st.subheader('Profit-vs-k% Curve — tìm k tối ưu')

    if T_actual is not None:
        ks = list(range(0, 101, 5))
        profits_uplift = []
        profits_random = []
        for k_pct in ks:
            a_uplift = policy_uplift_top(cate, k_pct / 100)
            a_random = policy_random(n, k_pct / 100)
            profits_uplift.append(ips_policy_value(
                a_uplift, T_actual, y_actual,
                profit=profit_per_conv, cost=cost_per_email))
            profits_random.append(ips_policy_value(
                a_random, T_actual, y_actual,
                profit=profit_per_conv, cost=cost_per_email))

        k_opt = ks[int(np.argmax(profits_uplift))]
        max_profit = max(profits_uplift)

        col1, col2 = st.columns([3, 1])
        with col1:
            st.plotly_chart(profit_curve_plotly(ks, profits_uplift, profits_random, k_opt),
                              use_container_width=True)
        with col2:
            st.metric('k* tối ưu', f'{k_opt}%')
            st.metric('Max profit/user', f'{max_profit:,.0f} VND')
            st.metric('Profit @ k*=100% (treat-all)',
                        f'{profits_uplift[-1]:,.0f} VND')
            lift = max_profit - profits_uplift[-1]
            st.metric('Lift vs treat-all', f'{lift:+,.0f} VND')

        st.info(f"""
        💡 **Insight**: Chỉ cần gửi email cho **top {k_opt}%** khách hàng theo uplift score
        để đạt lợi nhuận tối đa. Gửi nhiều hơn = tốn cost không tạo thêm conversion.
        """)


with tab3:
    st.subheader('🔬 Sensitivity Analysis')
    st.caption('Lợi nhuận thay đổi thế nào khi cost/profit khác đi?')

    if T_actual is not None:
        with st.spinner('Đang tính sensitivity...'):
            costs = [1_000, 2_000, 5_000, 10_000, 20_000]
            profits_vals = [100_000, 200_000, 300_000]

            sens_data = []
            for prof in profits_vals:
                for c in costs:
                    a = optimal_action(cate, profit=prof, cost=c)
                    pv = ips_policy_value(a, T_actual, y_actual,
                                            profit=prof, cost=c)
                    n_send = (a != 0).sum()
                    sens_data.append({
                        'Profit/conv (VND)': prof,
                        'Cost/email (VND)': c,
                        '%_treated': n_send / n * 100,
                        'Profit/user (VND)': round(pv),
                        'Break-even τ': round(c / prof, 4),
                    })
            sens_df = pd.DataFrame(sens_data)

        # Pivot heatmap
        pivot = sens_df.pivot(index='Profit/conv (VND)', columns='Cost/email (VND)',
                                values='Profit/user (VND)')

        fig = go.Figure(data=go.Heatmap(
            z=pivot.values, x=pivot.columns, y=pivot.index,
            colorscale='RdYlGn', zmid=0,
            text=pivot.values, texttemplate='%{text:,}',
            textfont={'size': 11},
            colorbar=dict(title='Profit/user'),
        ))
        fig.update_layout(
            title='Heatmap: Profit/user theo (Cost, Profit)',
            xaxis_title='Cost/email (VND)',
            yaxis_title='Profit/conversion (VND)',
            height=400,
        )
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(sens_df, use_container_width=True, hide_index=True)

        st.info("""
        📐 **Đọc bảng**: % treated **giảm khi cost tăng** — uplift modeling tự động
        chọn lọc khách hàng có uplift đủ cao để bù chi phí. Đây chính là giá trị
        cốt lõi của uplift modeling so với gửi đại trà.
        """)


# === Summary cuối ===
st.markdown('---')
st.markdown(f"""
### 📌 Tham số hiện tại
- **Profit/conv**: {profit_per_conv:,} VND
- **Cost/email**: {cost_per_email:,} VND
- **Break-even threshold**: {threshold:.4f} (chỉ gửi nếu uplift dự đoán > giá trị này)
""")

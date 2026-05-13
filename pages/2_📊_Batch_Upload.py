"""
Trang 2 — Upload CSV danh sách khách → batch scoring → download kết quả.
"""
import streamlit as st
import pandas as pd
import numpy as np
import io
from utils.load_models import (load_causal_forest, load_response_model,
                                predict_cate, predict_response, FEAT)
from utils.policy import (optimal_action, expected_profit_per_user,
                           DEFAULT_PROFIT, DEFAULT_COST,
                           QUADRANT_COLORS)
from utils.plots import policy_comparison_bar

st.set_page_config(page_title='Batch Upload', page_icon='📊', layout='wide')

st.title('📊 Batch Scoring — Upload CSV danh sách khách hàng')
st.caption('Upload file CSV → app tự score từng khách → trả CSV với recommendation và lợi nhuận kỳ vọng')

# === Load model ===
cf_model = load_causal_forest()
if cf_model is None:
    st.error('❌ Chưa có file `cf_final.pkl`. Quay lại trang chủ.')
    st.stop()

# === Sidebar ===
with st.sidebar:
    st.subheader('⚙️ Tham số kinh tế')
    profit_per_conv = st.number_input(
        'Lợi nhuận/conversion (VND)', value=DEFAULT_PROFIT,
        min_value=10_000, max_value=1_000_000, step=10_000)
    cost_per_email = st.number_input(
        'Chi phí/email (VND)', value=DEFAULT_COST,
        min_value=500, max_value=50_000, step=500)
    threshold = cost_per_email / profit_per_conv
    st.metric('Break-even τ', f'{threshold:.4f}')

# === Required columns ===
st.subheader('📥 Upload CSV')

with st.expander('📋 Yêu cầu format CSV'):
    st.markdown(f"""
    File CSV phải có **10 cột features** sau (đúng tên):

    `{', '.join(FEAT)}`

    Các cột zip_code và channel là **one-hot** (0/1), tổng mỗi nhóm = 1.
    File có thể có thêm cột tùy chọn `customer_id` để tracking.
    """)

    # Sample template
    sample = pd.DataFrame({
        'customer_id': [1001, 1002, 1003],
        'recency': [1, 5, 10],
        'womens': [1, 0, 1],
        'newbie': [1, 0, 0],
        'history_log': [7.5, 4.0, 3.2],
        'zip_code_Rural': [0, 0, 1],
        'zip_code_Surburban': [0, 1, 0],
        'zip_code_Urban': [1, 0, 0],
        'channel_Multichannel': [1, 0, 0],
        'channel_Phone': [0, 1, 0],
        'channel_Web': [0, 0, 1],
    })
    csv_bytes = sample.to_csv(index=False).encode('utf-8')
    st.download_button('📥 Tải template CSV mẫu', csv_bytes,
                        'template_customers.csv', 'text/csv')

uploaded = st.file_uploader('Chọn file CSV', type=['csv'])

if uploaded is None:
    st.info('👆 Upload CSV để bắt đầu scoring.')
    st.stop()

# === Read CSV ===
try:
    df = pd.read_csv(uploaded)
except Exception as e:
    st.error(f'❌ Lỗi đọc file: {e}')
    st.stop()

st.success(f'✅ Đã đọc {len(df):,} dòng từ `{uploaded.name}`')
st.dataframe(df.head(), use_container_width=True)

# Validate
missing = [f for f in FEAT if f not in df.columns]
if missing:
    st.error(f'❌ Thiếu cột: {missing}')
    st.stop()

# === Run prediction ===
with st.spinner(f'🔮 Đang score {len(df):,} khách hàng...'):
    X = df[FEAT].values.astype(np.float32)
    cate = predict_cate(cf_model, X)

    action = optimal_action(cate, profit=profit_per_conv, cost=cost_per_email)

    df_out = df.copy()
    df_out['uplift_men'] = cate[:, 0].round(4)
    df_out['uplift_women'] = cate[:, 1].round(4)
    df_out['recommended_action'] = pd.Series(action).map({
        0: 'Không gửi',
        1: 'Gửi Mens E-Mail',
        2: 'Gửi Womens E-Mail',
    })
    df_out['expected_profit_VND'] = expected_profit_per_user(
        cate, action, profit=profit_per_conv, cost=cost_per_email
    ).round(0).astype(int)

st.success('✅ Đã scoring xong!')

# === Summary metrics ===
st.markdown('## 📈 Tổng quan kết quả')

n = len(df_out)
n_send_men = (action == 1).sum()
n_send_women = (action == 2).sum()
n_no_send = (action == 0).sum()
total_profit = df_out['expected_profit_VND'].sum()
total_cost = (n_send_men + n_send_women) * cost_per_email

col1, col2, col3, col4 = st.columns(4)
col1.metric('Tổng khách', f'{n:,}')
col2.metric('Gửi Mens', f'{n_send_men:,}', f'{n_send_men/n*100:.1f}%')
col3.metric('Gửi Womens', f'{n_send_women:,}', f'{n_send_women/n*100:.1f}%')
col4.metric('Không gửi', f'{n_no_send:,}', f'{n_no_send/n*100:.1f}%')

st.markdown('---')

col1, col2, col3 = st.columns(3)
col1.metric('💰 Lợi nhuận tổng', f'{total_profit:,.0f} VND')
col2.metric('📤 Chi phí gửi tổng', f'{total_cost:,.0f} VND')
col3.metric('💵 Lợi nhuận trung bình/user', f'{total_profit/n:,.0f} VND')

# === Compare với baseline ===
st.markdown('## 🔁 So sánh với các chính sách khác')

action_treat_all_men = np.ones(n, dtype=int)
action_treat_all_women = np.full(n, 2, dtype=int)
action_no_treat = np.zeros(n, dtype=int)

profit_no = expected_profit_per_user(cate, action_no_treat,
                                       profit=profit_per_conv, cost=cost_per_email).sum()
profit_men_all = expected_profit_per_user(cate, action_treat_all_men,
                                            profit=profit_per_conv, cost=cost_per_email).sum()
profit_women_all = expected_profit_per_user(cate, action_treat_all_women,
                                              profit=profit_per_conv, cost=cost_per_email).sum()
profit_uplift = total_profit

policy_df = pd.DataFrame({
    'Policy': ['Không gửi ai', 'Gửi tất cả Mens', 'Gửi tất cả Womens',
                '⭐ Uplift Optimal'],
    'Profit/user (VND)': [
        round(profit_no / n),
        round(profit_men_all / n),
        round(profit_women_all / n),
        round(profit_uplift / n),
    ],
    'Total profit (VND)': [
        round(profit_no), round(profit_men_all),
        round(profit_women_all), round(profit_uplift),
    ],
})
st.dataframe(policy_df, use_container_width=True, hide_index=True)
st.plotly_chart(policy_comparison_bar(policy_df), use_container_width=True)

uplift_advantage = profit_uplift - max(profit_men_all, profit_women_all, profit_no)
if uplift_advantage > 0:
    st.success(f'🎉 **Uplift Optimal vượt baseline tốt nhất: +{uplift_advantage:,.0f} VND**')
else:
    st.warning(f'⚠️ Uplift Optimal hiện không vượt baseline. '
                f'Có thể tăng cost giả định để có lift rõ hơn.')

# === Download ===
st.markdown('## 💾 Download kết quả')

csv_out = df_out.to_csv(index=False).encode('utf-8')
st.download_button(
    '📥 **Download CSV với recommendation**',
    csv_out, f'scored_{uploaded.name}', 'text/csv',
    type='primary', use_container_width=True,
)

# Excel option
try:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_out.to_excel(writer, sheet_name='Scored Customers', index=False)
        policy_df.to_excel(writer, sheet_name='Policy Comparison', index=False)
    excel_bytes = output.getvalue()
    st.download_button(
        '📊 Download Excel (.xlsx)',
        excel_bytes, f'scored_{uploaded.name.replace(".csv", ".xlsx")}',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
except ImportError:
    st.caption('Cài `openpyxl` để có option Excel: `pip install openpyxl`')

# Preview table
st.markdown('### 📋 Preview kết quả (200 dòng đầu)')

def color_action(val):
    if val == 'Gửi Mens E-Mail':     return 'background-color: #D1FAE5'
    if val == 'Gửi Womens E-Mail':   return 'background-color: #FEF3C7'
    if val == 'Không gửi':            return 'background-color: #F3F4F6'
    return ''

preview = df_out.head(200)
st.dataframe(
    preview.style.map(color_action, subset=['recommended_action']),
    use_container_width=True, height=400,
)

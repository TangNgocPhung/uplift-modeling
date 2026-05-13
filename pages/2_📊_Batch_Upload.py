"""
Trang 2 — Batch Upload (Editorial design v4)
Upload CSV danh sách khách → batch scoring → download kết quả.
"""
import streamlit as st
import pandas as pd
import numpy as np
import io
from utils.load_models import load_causal_forest, predict_cate, FEAT
from utils.policy import (optimal_action, expected_profit_per_user,
                           DEFAULT_PROFIT, DEFAULT_COST)
from utils.plots import policy_comparison_bar
from utils.editorial import (inject_css, render_masthead, render_sidebar_header,
                              render_break_even, sidebar_section_title,
                              banner, section, error_card)

st.set_page_config(
    page_title='Batch Upload — UpliftIQ',
    page_icon='▲',
    layout='wide',
    initial_sidebar_state='expanded',
)

inject_css()


# ═════════════════════════════════════════════════════════════
# LOAD MODEL
# ═════════════════════════════════════════════════════════════
cf_model = load_causal_forest()
if cf_model is None:
    render_masthead(2, 'BATCH UPLOAD',
                    'Batch scoring', 'danh sách khách hàng',
                    'Upload CSV → app tự score → trả CSV với recommendation')
    error_card('Chưa có file mô hình',
               'Vui lòng copy file <code>cf_final.pkl</code> vào thư mục '
               '<code>./models/</code> rồi reload trang.')
    st.stop()


# ═════════════════════════════════════════════════════════════
# PAGE HEADER
# ═════════════════════════════════════════════════════════════
render_masthead(2, 'BATCH UPLOAD',
                'Batch scoring', 'danh sách khách hàng',
                'Upload CSV → app tự score → trả CSV với recommendation và lợi nhuận kỳ vọng')


# ═════════════════════════════════════════════════════════════
# SIDEBAR
# ═════════════════════════════════════════════════════════════
with st.sidebar:
    render_sidebar_header(active_idx=2)

    sidebar_section_title('⚙ Tham số kinh tế')
    profit_per_conv = st.number_input(
        'Lợi nhuận / conversion (VND)', value=DEFAULT_PROFIT,
        min_value=10_000, max_value=1_000_000, step=10_000)
    cost_per_email = st.number_input(
        'Chi phí / email (VND)', value=DEFAULT_COST,
        min_value=500, max_value=50_000, step=500)

    threshold = cost_per_email / profit_per_conv
    render_break_even(threshold)


# ═════════════════════════════════════════════════════════════
# BODY — UPLOAD
# ═════════════════════════════════════════════════════════════
st.markdown('<div class="iq-body">', unsafe_allow_html=True)

section('import dữ liệu',
        'Upload file CSV để batch scoring',
        'File CSV cần có đúng 10 cột features. Tải template bên dưới để có format chuẩn.')

with st.expander('📋 Yêu cầu format CSV', expanded=False):
    st.markdown(f"""
File CSV phải có **10 cột features** sau (đúng tên):

`{', '.join(FEAT)}`

Các cột zip_code và channel là **one-hot** (0/1), tổng mỗi nhóm = 1.
File có thể có thêm cột tùy chọn `customer_id` để tracking.
""")

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
    banner('info', '👆 <b>Upload CSV</b> để bắt đầu batch scoring.')
    st.markdown('<div style="height:18px"></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()


# ═════════════════════════════════════════════════════════════
# READ + VALIDATE
# ═════════════════════════════════════════════════════════════
try:
    df = pd.read_csv(uploaded)
except Exception as e:
    banner('error', f'❌ <b>Lỗi đọc file</b>: {e}')
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

banner('success', f'✓ Đã đọc <b>{len(df):,}</b> dòng từ <code>{uploaded.name}</code>')

missing = [f for f in FEAT if f not in df.columns]
if missing:
    banner('error', f'❌ <b>Thiếu cột bắt buộc</b>: {missing}')
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
st.markdown('<div class="iq-col-title">Xem trước 5 dòng đầu</div>', unsafe_allow_html=True)
st.dataframe(df.head(), use_container_width=True)


# ═════════════════════════════════════════════════════════════
# RUN PREDICTION
# ═════════════════════════════════════════════════════════════
with st.spinner(f'Đang score {len(df):,} khách hàng...'):
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


# ═════════════════════════════════════════════════════════════
# SUMMARY METRICS
# ═════════════════════════════════════════════════════════════
n = len(df_out)
n_send_men = int((action == 1).sum())
n_send_women = int((action == 2).sum())
n_no_send = int((action == 0).sum())
total_profit = int(df_out['expected_profit_VND'].sum())
total_cost = (n_send_men + n_send_women) * cost_per_email

st.markdown('<div style="height:24px"></div>', unsafe_allow_html=True)
section('tổng quan kết quả', 'Phân bổ recommendation')

st.markdown(f"""
<div class="iq-lead">
<div class="iq-ls">
<div class="v">{n:,}</div>
<div class="l">Tổng khách hàng</div>
<div class="s">đã scoring</div>
</div>
<div class="iq-ls">
<div class="v red">{n_send_men:,}</div>
<div class="l">Gửi Mens E-mail</div>
<div class="s">{n_send_men/n*100:.1f}% danh sách</div>
</div>
<div class="iq-ls">
<div class="v sage">{n_send_women:,}</div>
<div class="l">Gửi Womens E-mail</div>
<div class="s">{n_send_women/n*100:.1f}% danh sách</div>
</div>
<div class="iq-ls">
<div class="v tan">{n_no_send:,}</div>
<div class="l">Không gửi</div>
<div class="s">{n_no_send/n*100:.1f}% danh sách</div>
</div>
</div>

<div class="iq-lead cols3">
<div class="iq-ls">
<div class="v sage sm">{total_profit:,.0f}</div>
<div class="l">Lợi nhuận tổng (VND)</div>
<div class="s">expected profit</div>
</div>
<div class="iq-ls">
<div class="v sm">{total_cost:,.0f}</div>
<div class="l">Chi phí gửi tổng (VND)</div>
<div class="s">{n_send_men + n_send_women:,} email</div>
</div>
<div class="iq-ls">
<div class="v sm">{total_profit/n:,.0f}</div>
<div class="l">Lợi nhuận trung bình / user</div>
<div class="s">VND / khách</div>
</div>
</div>
""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════
# POLICY COMPARISON
# ═════════════════════════════════════════════════════════════
section('so sánh chính sách', 'Uplift Optimal vs Baseline',
        'So sánh chính sách uplift-driven với các baseline naive (gửi tất cả, không gửi ai).')

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

policy_rows = [
    ('Không gửi ai',       profit_no,        False),
    ('Gửi tất cả Mens',    profit_men_all,   False),
    ('Gửi tất cả Womens',  profit_women_all, False),
    ('★ Uplift Optimal',   profit_uplift,    True),
]

table_html = '<table class="iq-dt">'
table_html += '<tr><th>Policy</th><th style="text-align:right">Profit / user (VND)</th><th style="text-align:right">Total profit (VND)</th></tr>'
for name, total, is_best in policy_rows:
    cls = 'highlight' if is_best else ''
    table_html += (f'<tr class="{cls}"><td>{name}</td>'
                   f'<td class="num">{total/n:,.0f}</td>'
                   f'<td class="num">{total:,.0f}</td></tr>')
table_html += '</table>'
st.markdown(table_html, unsafe_allow_html=True)

policy_df = pd.DataFrame({
    'Policy': [r[0] for r in policy_rows],
    'Profit/user (VND)': [round(r[1]/n) for r in policy_rows],
    'Total profit (VND)': [round(r[1]) for r in policy_rows],
})
st.plotly_chart(policy_comparison_bar(policy_df), use_container_width=True)

uplift_advantage = profit_uplift - max(profit_men_all, profit_women_all, profit_no)
if uplift_advantage > 0:
    banner('success',
           f'🎉 <b>Uplift Optimal vượt baseline tốt nhất</b>: '
           f'+{uplift_advantage:,.0f} VND tổng / +{uplift_advantage/n:,.0f} VND mỗi user.')
else:
    banner('warning',
           '⚠ Uplift Optimal hiện không vượt baseline. '
           'Có thể tăng <code>cost/email</code> để thấy lợi thế rõ hơn.')


# ═════════════════════════════════════════════════════════════
# DOWNLOAD
# ═════════════════════════════════════════════════════════════
st.markdown('<div style="height:24px"></div>', unsafe_allow_html=True)
section('download kết quả', 'Xuất file đã scoring')

csv_out = df_out.to_csv(index=False).encode('utf-8')
c1, c2 = st.columns(2)
with c1:
    st.download_button(
        '▼  CSV với recommendation',
        csv_out, f'scored_{uploaded.name}', 'text/csv',
        use_container_width=True,
    )
with c2:
    try:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_out.to_excel(writer, sheet_name='Scored Customers', index=False)
            policy_df.to_excel(writer, sheet_name='Policy Comparison', index=False)
        excel_bytes = output.getvalue()
        st.download_button(
            '▼  Excel (.xlsx)',
            excel_bytes, f'scored_{uploaded.name.replace(".csv", ".xlsx")}',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            use_container_width=True,
        )
    except ImportError:
        st.markdown('<div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;color:#8C7B6B;padding-top:8px">Cài <code>openpyxl</code> để có option Excel.</div>',
                    unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════
# PREVIEW
# ═════════════════════════════════════════════════════════════
st.markdown('<div style="height:24px"></div>', unsafe_allow_html=True)
section('preview kết quả', 'Xem trước 200 dòng đầu')


def color_action(val):
    if val == 'Gửi Mens E-Mail':    return 'background-color: #FBF8F2; color: #B22234; font-weight: 600'
    if val == 'Gửi Womens E-Mail':  return 'background-color: #FBF8F2; color: #6B8068; font-weight: 600'
    if val == 'Không gửi':           return 'background-color: #ECE5D7; color: #4A6378'
    return ''


preview = df_out.head(200)
st.dataframe(
    preview.style.map(color_action, subset=['recommended_action']),
    use_container_width=True, height=420,
)

st.markdown('</div>', unsafe_allow_html=True)

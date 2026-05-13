"""
utils/plots.py — Plotly charts theo editorial palette.
"""
import plotly.graph_objects as go
import numpy as np

# Editorial palette
PAL = {
    'ink':    '#1A2A47',
    'cream':  '#F4EFE6',
    'red':    '#B22234',
    'tan':    '#C7A270',
    'slate':  '#4A6378',
    'sage':   '#6B8068',
    'rust':   '#92400E',
    'olive':  '#7B8B3C',
    'taupe':  '#8C7B6B',
    'rule':   '#C8BFB0',
}

FONT_MONO  = 'IBM Plex Mono, monospace'
FONT_SERIF = 'Playfair Display, serif'
FONT_SANS  = 'IBM Plex Sans Condensed, sans-serif'


def gauge_uplift(value, threshold, label='Uplift'):
    """
    Gauge chart hiển thị giá trị uplift so với threshold break-even.
    """
    # Phân vùng: âm (đỏ) → vàng (chưa đủ) → xanh (vượt threshold)
    max_val = max(abs(value), abs(threshold)) * 2.5
    max_val = max(max_val, 0.01)

    color = PAL['sage'] if value >= threshold else (
        PAL['rust'] if value > 0 else PAL['red']
    )

    fig = go.Figure(go.Indicator(
        mode='gauge+number+delta',
        value=value,
        number={'valueformat': '+.4f', 'font': {'size': 36, 'family': FONT_SERIF, 'color': PAL['ink']}},
        delta={'reference': threshold, 'valueformat': '+.4f',
                'font': {'size': 14, 'family': FONT_MONO},
                'increasing': {'color': PAL['sage']},
                'decreasing': {'color': PAL['red']}},
        title={'text': label, 'font': {'size': 14, 'family': FONT_MONO, 'color': PAL['slate']}},
        gauge={
            'axis': {'range': [-max_val, max_val],
                      'tickfont': {'size': 10, 'family': FONT_MONO, 'color': PAL['taupe']},
                      'tickformat': '.3f'},
            'bar': {'color': color, 'thickness': 0.7},
            'bgcolor': PAL['cream'],
            'borderwidth': 1,
            'bordercolor': PAL['rule'],
            'steps': [
                {'range': [-max_val, 0], 'color': '#E8DCC8'},
                {'range': [0, threshold], 'color': '#F4E7CC'},
                {'range': [threshold, max_val], 'color': '#D4E0CC'},
            ],
            'threshold': {
                'line': {'color': PAL['red'], 'width': 3},
                'thickness': 0.85,
                'value': threshold,
            },
        },
    ))
    fig.update_layout(
        paper_bgcolor=PAL['cream'],
        plot_bgcolor=PAL['cream'],
        height=260,
        margin=dict(l=30, r=30, t=50, b=20),
        font_family=FONT_SANS,
    )
    return fig


def policy_comparison_bar(policy_df):
    """Bar chart so sánh profit/user giữa các policies."""
    fig = go.Figure(go.Bar(
        x=policy_df['Profit/user (VND)'],
        y=policy_df['Policy'],
        orientation='h',
        marker_color=[PAL['red'] if 'Uplift' in p or '⭐' in p else PAL['slate']
                       for p in policy_df['Policy']],
        text=[f'{v:,.0f}' for v in policy_df['Profit/user (VND)']],
        textposition='outside',
        textfont={'family': FONT_MONO, 'size': 11, 'color': PAL['ink']},
    ))
    fig.update_layout(
        title={'text': 'Profit per user — So sánh policies',
                'font': {'family': FONT_SERIF, 'size': 18, 'color': PAL['ink']}},
        xaxis_title='Profit/user (VND)',
        yaxis_title='',
        paper_bgcolor=PAL['cream'],
        plot_bgcolor=PAL['cream'],
        font_family=FONT_SANS,
        font_color=PAL['ink'],
        height=350,
        margin=dict(l=140, r=40, t=60, b=40),
        xaxis=dict(gridcolor=PAL['rule'], zerolinecolor=PAL['ink']),
        yaxis=dict(gridcolor=PAL['rule']),
    )
    return fig


def profit_curve_plotly(ks, profits_uplift, profits_random, k_opt):
    """Profit-vs-k% curve cho Economic Simulator."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=ks, y=profits_uplift, mode='lines+markers',
        name='Uplift Top-k%',
        line=dict(color=PAL['red'], width=3),
        marker=dict(size=7, color=PAL['red']),
    ))
    fig.add_trace(go.Scatter(
        x=ks, y=profits_random, mode='lines+markers',
        name='Random k%',
        line=dict(color=PAL['slate'], width=2, dash='dash'),
        marker=dict(size=6, color=PAL['slate']),
    ))
    # Đánh dấu k optimal
    idx = ks.index(k_opt) if k_opt in ks else 0
    fig.add_trace(go.Scatter(
        x=[k_opt], y=[profits_uplift[idx]],
        mode='markers+text',
        marker=dict(size=15, color=PAL['sage'], symbol='star'),
        text=[f'  k*={k_opt}%'],
        textposition='middle right',
        textfont={'family': FONT_MONO, 'size': 12, 'color': PAL['sage']},
        name='k* tối ưu',
        showlegend=False,
    ))
    fig.update_layout(
        title={'text': 'Profit per user vs. % khách được gửi email',
                'font': {'family': FONT_SERIF, 'size': 18, 'color': PAL['ink']}},
        xaxis_title='% Treated',
        yaxis_title='Profit/user (VND)',
        paper_bgcolor=PAL['cream'],
        plot_bgcolor=PAL['cream'],
        font_family=FONT_SANS,
        font_color=PAL['ink'],
        height=430,
        margin=dict(l=70, r=40, t=70, b=50),
        xaxis=dict(gridcolor=PAL['rule'], zerolinecolor=PAL['ink']),
        yaxis=dict(gridcolor=PAL['rule'], zerolinecolor=PAL['ink']),
        legend=dict(bgcolor=PAL['cream'], bordercolor=PAL['rule'], borderwidth=1),
    )
    return fig


def quadrant_pie(counts, colors):
    """Pie chart phân bổ 4 quadrant."""
    labels = list(counts.keys())
    values = list(counts.values())
    color_list = [colors.get(l, PAL['taupe']) for l in labels]

    fig = go.Figure(go.Pie(
        labels=labels, values=values,
        marker=dict(colors=color_list, line=dict(color=PAL['cream'], width=3)),
        textfont={'family': FONT_MONO, 'size': 12, 'color': '#fff'},
        textinfo='label+percent',
    ))
    fig.update_layout(
        title={'text': 'Phân bổ 4 nhóm khách hàng',
                'font': {'family': FONT_SERIF, 'size': 18, 'color': PAL['ink']}},
        paper_bgcolor=PAL['cream'],
        plot_bgcolor=PAL['cream'],
        font_family=FONT_SANS,
        height=400,
        margin=dict(l=20, r=20, t=60, b=20),
    )
    return fig


def quadrant_scatter(df):
    """Scatter uplift vs response, màu theo quadrant."""
    color_map = {
        'Persuadable':  PAL['red'],
        'Sure Thing':   PAL['slate'],
        'Sleeping Dog': PAL['rust'],
        'Lost Cause':   PAL['taupe'],
    }

    fig = go.Figure()
    for q in sorted(df['quadrant'].unique()):
        sub = df[df['quadrant'] == q]
        # Sample tối đa 2000 điểm để render nhanh
        if len(sub) > 2000:
            sub = sub.sample(2000, random_state=42)
        fig.add_trace(go.Scatter(
            x=sub['response'] if 'response' in sub.columns else sub['uplift_max'] * 0,
            y=sub['uplift_max'] if 'uplift_max' in sub.columns else np.zeros(len(sub)),
            mode='markers',
            name=q,
            marker=dict(color=color_map.get(q, PAL['taupe']),
                         size=5, opacity=0.6,
                         line=dict(width=0)),
        ))
    fig.update_layout(
        title={'text': 'Bản đồ Persona — Uplift × Response',
                'font': {'family': FONT_SERIF, 'size': 18, 'color': PAL['ink']}},
        xaxis_title='Response (P[Y|control])',
        yaxis_title='Predicted uplift',
        paper_bgcolor=PAL['cream'],
        plot_bgcolor=PAL['cream'],
        font_family=FONT_SANS,
        font_color=PAL['ink'],
        height=520,
        xaxis=dict(gridcolor=PAL['rule'], zerolinecolor=PAL['ink']),
        yaxis=dict(gridcolor=PAL['rule'], zerolinecolor=PAL['ink']),
        legend=dict(bgcolor=PAL['cream'], bordercolor=PAL['rule'], borderwidth=1),
    )
    return fig

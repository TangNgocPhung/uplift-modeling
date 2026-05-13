"""
utils/policy.py — Policy / decision rules + quadrant labeling.
"""
import numpy as np

DEFAULT_PROFIT = 200_000   # VND/conversion
DEFAULT_COST   = 5_000     # VND/email

# Palette editorial (đồng bộ với app.py homepage)
QUADRANT_COLORS = {
    'Persuadable':  '#B22234',  # đỏ Vietnamese
    'Sure Thing':   '#4A6378',  # slate blue
    'Sleeping Dog': '#92400E',  # rust/brown
    'Lost Cause':   '#8C7B6B',  # taupe
}

QUADRANT_RECOMMENDATION = {
    'Persuadable':  'GỬI EMAIL — Uplift cao, response thấp. Email kích hoạt mua hàng.',
    'Sure Thing':   'KHÔNG GỬI — Khách tự mua, gửi email tốn chi phí không tạo thêm giá trị.',
    'Sleeping Dog': 'TUYỆT ĐỐI KHÔNG GỬI — Email phản tác dụng, giảm tỷ lệ mua.',
    'Lost Cause':   'BỎ QUA — Không phản hồi với bất kỳ treatment nào.',
}


def optimal_action(cate, profit=DEFAULT_PROFIT, cost=DEFAULT_COST):
    """
    Returns (n,) array of {0, 1, 2}: 0=no send, 1=mens, 2=womens.
    Chọn treatment có expected profit cao nhất.
    """
    cate = np.asarray(cate)
    if cate.ndim == 1:
        cate = cate.reshape(-1, 2)
    threshold = cost / profit

    # Expected profit per treatment
    profit_men   = profit * cate[:, 0] - cost
    profit_women = profit * cate[:, 1] - cost
    profit_none  = np.zeros(len(cate))

    profits = np.column_stack([profit_none, profit_men, profit_women])
    actions = np.argmax(profits, axis=1)

    # Đảm bảo: nếu uplift dưới threshold thì action = 0
    best_uplift = cate.max(axis=1)
    actions = np.where(best_uplift < threshold, 0, actions)
    return actions.astype(int)


def expected_profit_per_user(cate, action, profit=DEFAULT_PROFIT, cost=DEFAULT_COST):
    """
    Expected profit per user given chosen action.
    """
    cate = np.asarray(cate)
    if cate.ndim == 1:
        cate = cate.reshape(-1, 2)
    action = np.asarray(action)

    result = np.zeros(len(cate))
    mask_men = (action == 1)
    mask_women = (action == 2)
    result[mask_men] = profit * cate[mask_men, 0] - cost
    result[mask_women] = profit * cate[mask_women, 1] - cost
    return result


def quadrant_label(uplift, response, u_p10, u_med, r_med):
    """
    Phân loại 1 khách vào 4 quadrant dựa trên uplift và response.

    - Persuadable:  uplift cao, response thấp
    - Sure Thing:   response cao, uplift thấp
    - Sleeping Dog: uplift âm hoặc rất thấp
    - Lost Cause:   cả 2 thấp
    """
    if uplift < u_p10:
        return 'Sleeping Dog'
    if uplift >= u_med and response < r_med:
        return 'Persuadable'
    if response >= r_med and uplift < u_med:
        return 'Sure Thing'
    return 'Lost Cause'


# ─────────────────────────────────────────────────────────────
# POLICIES cho Economic Simulator
# ─────────────────────────────────────────────────────────────
def policy_no_treat(n):
    return np.zeros(n, dtype=int)


def policy_treat_all(n, treatment=1):
    return np.full(n, treatment, dtype=int)


def policy_random(n, k_pct):
    """Treat k_pct ngẫu nhiên với mens (treatment=1)."""
    n_treat = int(n * k_pct)
    rng = np.random.RandomState(42)
    idx = rng.choice(n, size=n_treat, replace=False)
    a = np.zeros(n, dtype=int)
    a[idx] = 1
    return a


def policy_uplift_top(cate, k_pct):
    """Treat top k_pct theo max uplift."""
    cate = np.asarray(cate)
    if cate.ndim == 1:
        cate = cate.reshape(-1, 2)
    n = len(cate)
    n_treat = int(n * k_pct)
    best_uplift = cate.max(axis=1)
    best_treat = cate.argmax(axis=1) + 1  # 1=mens, 2=womens
    order = np.argsort(-best_uplift)
    top_idx = order[:n_treat]
    a = np.zeros(n, dtype=int)
    a[top_idx] = best_treat[top_idx]
    return a


def policy_response_top(response_scores, k_pct, treatment=1):
    """
    Baseline response-model policy: gửi `treatment` cho top k_pct theo response score.
    Đây là cách marketing truyền thống — "ai sẽ mua" → gửi email.
    So sánh với policy_uplift_top sẽ cho thấy giá trị của uplift modeling.

    response_scores: (n,) array P(Y=1|X) từ response model.
    treatment: 1=Mens (default), 2=Womens.
    """
    response_scores = np.asarray(response_scores).ravel()
    n = len(response_scores)
    n_treat = int(n * k_pct)
    order = np.argsort(-response_scores)
    top_idx = order[:n_treat]
    a = np.zeros(n, dtype=int)
    a[top_idx] = treatment
    return a


def ips_policy_value(action, T_actual, y_actual,
                      profit=DEFAULT_PROFIT, cost=DEFAULT_COST,
                      propensities=None):
    """
    Inverse Propensity Score policy evaluation.
    Returns expected profit per user dưới policy đề xuất.

    T_actual: array với values {'control', 'treat_men', 'treat_women'} hoặc {0,1,2}.
    y_actual: array binary conversion.
    """
    T_actual = np.asarray(T_actual)
    y_actual = np.asarray(y_actual).astype(int)
    action = np.asarray(action).astype(int)

    # Convert string → int nếu cần
    if T_actual.dtype.kind in ('U', 'O'):
        mp = {'control': 0, 'treat_men': 1, 'treat_women': 2,
              'no_email': 0, 'mens_email': 1, 'womens_email': 2,
              'No E-Mail': 0, 'Mens E-Mail': 1, 'Womens E-Mail': 2}
        T_int = np.array([mp.get(str(t), 0) for t in T_actual])
    else:
        T_int = T_actual.astype(int)

    # Propensities mặc định = 1/3 mỗi treatment
    if propensities is None:
        propensities = np.full(len(action), 1/3)

    # Match: action == T_actual
    matched = (action == T_int).astype(float)
    weights = matched / np.clip(propensities, 1e-6, None)

    # Revenue khi match
    rev = np.where(action == 0, 0,
                    profit * y_actual - cost)
    weighted = rev * weights
    if matched.sum() < 1:
        return 0.0
    return weighted.sum() / matched.sum() if matched.sum() > 0 else 0.0

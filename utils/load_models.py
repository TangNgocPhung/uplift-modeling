"""
utils/load_models.py — Load model artifacts từ ./models/
"""
import os
import joblib
import numpy as np
import pandas as pd
import streamlit as st

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(HERE, 'models')

FEAT = [
    'recency', 'womens', 'newbie', 'history_log',
    'zip_code_Rural', 'zip_code_Surburban', 'zip_code_Urban',
    'channel_Multichannel', 'channel_Phone', 'channel_Web',
]

TREAT_DISPLAY = {
    0: 'Không gửi (control)',
    1: 'Mens E-Mail',
    2: 'Womens E-Mail',
}


@st.cache_resource
def load_causal_forest():
    fp = os.path.join(MODELS_DIR, 'cf_final.pkl')
    if not os.path.exists(fp):
        return None
    try:
        return joblib.load(fp)
    except Exception as e:
        st.error(f'Lỗi load CausalForest: {e}')
        return None


@st.cache_resource
def load_xlearner():
    fp = os.path.join(MODELS_DIR, 'xlearner_final.pkl')
    if not os.path.exists(fp):
        return None
    try:
        return joblib.load(fp)
    except Exception:
        return None


@st.cache_resource
def load_response_model():
    fp = os.path.join(MODELS_DIR, 'response_model.pkl')
    if not os.path.exists(fp):
        return None
    try:
        return joblib.load(fp)
    except Exception:
        return None


@st.cache_data
def load_test_data():
    fp = os.path.join(MODELS_DIR, 'test_quadrant_FINAL.parquet')
    if not os.path.exists(fp):
        return None
    try:
        return pd.read_parquet(fp)
    except Exception:
        return None


@st.cache_data
def load_persona_profile():
    fp = os.path.join(MODELS_DIR, 'persona_detailed.csv')
    if not os.path.exists(fp):
        return None
    try:
        return pd.read_csv(fp)
    except Exception:
        return None


@st.cache_data
def load_classify_thresholds():
    fp = os.path.join(MODELS_DIR, 'classify_thresholds.csv')
    defaults = {'u_p10': 0.002, 'u_med': 0.008, 'r_med': 0.009}
    if not os.path.exists(fp):
        return defaults
    try:
        df = pd.read_csv(fp)
        out = defaults.copy()
        for _, row in df.iterrows():
            k = str(row.get('name', '')).strip().lower()
            v = row.get('value', None)
            if v is not None and k in out:
                out[k] = float(v)
        return out
    except Exception:
        return defaults


def predict_cate(model, X):
    """Returns (n, 2) — cột 0 = uplift_men, cột 1 = uplift_women."""
    if model is None:
        return np.zeros((len(X), 2))
    X = np.asarray(X, dtype=np.float32)

    if isinstance(model, tuple) and len(model) == 2:
        mode, m = model
        if mode == 'causalforest':
            try:
                cm = m.effect(X, T0=0, T1=1)
                cw = m.effect(X, T0=0, T1=2)
                return np.column_stack([cm, cw])
            except Exception:
                pass
        return _predict_generic(m, X)

    if isinstance(model, dict):
        if 'mens' in model and 'womens' in model:
            try:
                cm = model['mens'].predict(X) if hasattr(model['mens'], 'predict') else model['mens'](X)
                cw = model['womens'].predict(X) if hasattr(model['womens'], 'predict') else model['womens'](X)
                return np.column_stack([cm, cw])
            except Exception:
                pass

    return _predict_generic(model, X)


def _predict_generic(m, X):
    if hasattr(m, 'effect'):
        try:
            cm = m.effect(X, T0=0, T1=1)
            cw = m.effect(X, T0=0, T1=2)
            return np.column_stack([cm, cw])
        except Exception:
            try:
                out = m.effect(X)
                if out.ndim == 1:
                    return np.column_stack([out, np.zeros_like(out)])
                return out
            except Exception:
                pass
    if hasattr(m, 'predict'):
        try:
            out = m.predict(X)
            if isinstance(out, tuple):
                out = out[0]
            out = np.asarray(out)
            if out.ndim == 1:
                return np.column_stack([out, np.zeros_like(out)])
            if out.shape[1] >= 2:
                return out[:, :2]
            return np.column_stack([out[:, 0], np.zeros(len(X))])
        except Exception:
            pass
    return np.zeros((len(X), 2))


def predict_response(model, X):
    if model is None:
        return np.zeros(len(X))
    X = np.asarray(X, dtype=np.float32)
    try:
        return model.predict_proba(X)[:, 1]
    except Exception:
        try:
            return model.predict(X)
        except Exception:
            return np.zeros(len(X))


def predict_single(model, x_dict):
    X = np.array([[x_dict.get(f, 0) for f in FEAT]], dtype=np.float32)
    return predict_cate(model, X)[0]


def predict_batch(model, df):
    X = df[FEAT].values.astype(np.float32)
    return predict_cate(model, X)


def check_models_status():
    files = {
        'CausalForest model':    'cf_final.pkl',
        'X-Learner backup':      'xlearner_final.pkl',
        'Response model':        'response_model.pkl',
        'Test + quadrant':       'test_quadrant_FINAL.parquet',
        'Qini results':          'final_qini_pool_cv.csv',
        'Policy comparison':     'policy_comparison_FINAL.csv',
        'Thresholds':            'classify_thresholds.csv',
        'Persona profile':       'persona_detailed.csv',
    }
    return {lbl: os.path.exists(os.path.join(MODELS_DIR, fn))
            for lbl, fn in files.items()}

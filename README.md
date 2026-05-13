# 🎯 Uplift Modeling — Streamlit App

Demo app cho tiểu luận **"Mô hình hóa Uplift để Tối ưu hóa Chiến dịch Tặng điểm/Khuyến mãi"**.

## 📂 Cấu trúc

```
uplift_app/
├── app.py                              # Trang chủ
├── pages/
│   ├── 1_🎯_Single_Predict.py          # Predict 1 khách
│   ├── 2_📊_Batch_Upload.py            # Upload CSV → batch scoring
│   ├── 3_💰_Economic_Simulator.py      # Slider cost/profit interactive
│   └── 4_👥_Persona_Explorer.py        # Khám phá 4 quadrant
├── utils/
│   ├── load_models.py                  # Load .pkl files (cached)
│   ├── policy.py                       # Optimal allocation, IPS estimator
│   └── plots.py                        # Plotly charts
├── models/                             # Copy artifacts vào đây
│   ├── cf_final.pkl                    # CausalForest champion
│   ├── xlearner_final.pkl              # X-Learner backup
│   ├── response_model.pkl              # Response baseline
│   ├── test_quadrant_final.parquet     # Test data với quadrant
│   ├── final_qini_pool_cv.csv          # Qini results
│   └── persona_detailed.csv            # Persona profile
├── data/                               # Sample CSV templates
├── .streamlit/config.toml              # Theme config
├── requirements.txt
└── README.md
```

## 🚀 Chạy local

### 1. Setup môi trường

```bash
# Tạo virtual env
python -m venv .venv

# Activate (Windows)
.\.venv\Scripts\activate

# Activate (Mac/Linux)
source .venv/bin/activate

# Cài dependencies
pip install -r requirements.txt
```

### 2. Copy artifacts từ Google Drive

Vào folder `MyDrive/uplift/artifacts/` trên Drive, download 6 file vào `uplift_app/models/`:
- `cf_final.pkl`
- `xlearner_final.pkl`
- `response_model.pkl`
- `test_quadrant_final.parquet` (hoặc `test_with_quadrant.parquet`)
- `final_qini_pool_cv.csv`
- `persona_detailed.csv`

### 3. Train response model nếu chưa có

Nếu thiếu `response_model.pkl`, chạy snippet này trong notebook Colab và tải file về:

```python
from sklearn.ensemble import GradientBoostingClassifier
import joblib

# Train trên data control
control_mask = Ttr_str == CONTROL
resp_model = GradientBoostingClassifier(n_estimators=200, max_depth=4, random_state=42)
resp_model.fit(Xtr[control_mask], ytr[control_mask])

joblib.dump(resp_model, f'{ARTIFACT_DIR}/response_model.pkl')
```

### 4. Chạy app

```bash
streamlit run app.py
```

App tự mở browser tại `http://localhost:8501`.

## ☁️ Deploy lên Streamlit Cloud (miễn phí)

1. Push folder `uplift_app/` lên GitHub repo public.
2. Đăng ký [streamlit.io/cloud](https://streamlit.io/cloud) bằng GitHub.
3. Click "New app" → chọn repo → main file `app.py`.
4. Chờ 5 phút → có URL `https://yourapp.streamlit.app`.

**Lưu ý kích thước**: file `cf_final.pkl` có thể nặng > 25 MB (giới hạn GitHub).
Giải pháp:
- Dùng Git LFS, **hoặc**
- Re-train model với `n_estimators=200` (giảm từ 500) để file < 25 MB, **hoặc**
- Lưu model trên Hugging Face Hub và download khi app khởi động.

## 🐛 Troubleshooting

### `causalml` không cài được trên Windows

```bash
pip install --upgrade pip setuptools wheel cython
pip install "numpy<2.0" "scipy<1.13"
pip install causalml --no-build-isolation
```

Nếu vẫn fail: app **không cần `causalml`** để chạy, chỉ cần:
```bash
pip install streamlit pandas numpy scikit-learn lightgbm joblib plotly pyarrow
```

### Model file quá lớn

Re-train với `n_estimators=200` thay vì 500:
```python
cf_final = CausalForestDML(..., n_estimators=200, ...)
cf_final.fit(Y=ytr, T=Ttr_int, X=Xtr)
joblib.dump(cf_final, 'cf_final.pkl', compress=3)
```

### Port 8501 bị chiếm

```bash
streamlit run app.py --server.port 8502
```

## Học viên thực hiện
Tăng Ngọc Phụng - KHMT836027
Hoàng Châu Ngọc Phương -  KHMT836028
Lê Thị Mai Len - KHMT836015
Giảng viên hướng dẫn: TS. Huỳnh Lê Tấn Tài

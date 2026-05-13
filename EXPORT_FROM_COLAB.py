"""
Snippet để PASTE vào notebook Colab cuối cùng để export TẤT CẢ artifacts
cần thiết cho Streamlit app.

Chạy cell này TRONG NOTEBOOK COLAB (không phải local), nó sẽ:
1. Train response_model nếu chưa có
2. Tạo sample CSV cho test
3. Lưu tất cả vào Drive: MyDrive/uplift/artifacts/

Sau đó bạn download các file đó về local folder uplift_app/models/.
"""

# ============================================================
# PASTE TỪ ĐÂY VÀO 1 CELL TRONG NOTEBOOK COLAB
# ============================================================

import joblib, os
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier

ARTIFACT_DIR = '/content/drive/MyDrive/uplift/artifacts'  # đổi nếu khác
os.makedirs(ARTIFACT_DIR, exist_ok=True)

print('=== Export artifacts cho Streamlit app ===\n')

# 1. Train response_model nếu chưa có
resp_path = f'{ARTIFACT_DIR}/response_model.pkl'
if not os.path.exists(resp_path):
    print('[1/4] Training response_model...')
    control_mask = Ttr_str == CONTROL
    resp_model = GradientBoostingClassifier(
        n_estimators=200, max_depth=4, random_state=42)
    resp_model.fit(Xtr[control_mask], ytr[control_mask])
    joblib.dump(resp_model, resp_path, compress=3)
    print(f'  → Saved: {resp_path}')
else:
    print('[1/4] response_model.pkl đã có')

# 2. Compress CausalForest model
cf_path = f'{ARTIFACT_DIR}/cf_final.pkl'
if 'cf_final' in dir() or 'cf_best' in dir():
    cf_to_save = locals().get('cf_final', locals().get('cf_best'))
    print('[2/4] Re-saving CausalForest with compress=3...')
    joblib.dump(cf_to_save, cf_path, compress=3)
    size_mb = os.path.getsize(cf_path) / 1024 / 1024
    print(f'  → Size: {size_mb:.1f} MB')
    if size_mb > 25:
        print(f'  ⚠️ File > 25MB, có thể vượt giới hạn GitHub free.')
        print(f'     Cân nhắc retrain với n_estimators=200.')
else:
    print('[2/4] CausalForest model không có trong namespace, bỏ qua.')

# 3. Lưu test_df có quadrant + cate columns
test_path = f'{ARTIFACT_DIR}/test_quadrant_final.parquet'
if 'test_df' in dir():
    print('[3/4] Saving test_quadrant_final.parquet...')
    # Đảm bảo có cột cate_men, cate_women
    test_export = test_df.copy()
    if 'CausalForest' in TUNED_PREDS['test']:
        cate_test = TUNED_PREDS['test']['CausalForest']
        test_export['cate_men'] = cate_test[:, 0]
        test_export['cate_women'] = cate_test[:, 1]
    test_export.to_parquet(test_path)
    print(f'  → Saved: {test_path} ({len(test_export):,} rows)')
else:
    print('[3/4] test_df không có trong namespace, bỏ qua.')

# 4. Tạo sample CSV cho user upload thử
sample_path = f'{ARTIFACT_DIR}/sample_customers.csv'
if 'test_df' in dir():
    sample = test_df.sample(100, random_state=42)
    feat_cols = ['recency', 'womens', 'newbie', 'history_log',
                 'zip_code_Rural', 'zip_code_Surburban', 'zip_code_Urban',
                 'channel_Multichannel', 'channel_Phone', 'channel_Web']
    sample_export = sample[feat_cols].reset_index(drop=True)
    sample_export.insert(0, 'customer_id', range(1001, 1001 + len(sample_export)))
    sample_export.to_csv(sample_path, index=False)
    print(f'[4/4] Sample CSV saved: {sample_path}')

print('\n=== HOÀN TẤT ===')
print(f'\nDownload các file sau về local PC:')
for f in ['cf_final.pkl', 'xlearner_final.pkl', 'response_model.pkl',
          'test_quadrant_final.parquet', 'final_qini_pool_cv.csv',
          'persona_detailed.csv', 'sample_customers.csv']:
    p = f'{ARTIFACT_DIR}/{f}'
    if os.path.exists(p):
        size = os.path.getsize(p) / 1024
        print(f'  ✓ {f}  ({size:.1f} KB)')
    else:
        print(f'  ✗ {f}  (chưa có)')

print(f'\nCopy về folder local: C:\\Users\\Phung\\Desktop\\Uplift\\uplift_app\\models\\')

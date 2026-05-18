import pandas as pd
import numpy as np
from datetime import datetime
import lightgbm as lgb
import joblib
import os
from app.config import SYMBOL

os.makedirs("models", exist_ok=True)
os.makedirs("logs", exist_ok=True)

def train_model():
    print(f"[{datetime.now()}] Начинаем обучение модели для {SYMBOL}...")

    # Загружаем данные
    df = pd.read_csv(f"data/{SYMBOL.replace('/', '')}_historical.csv") if os.path.exists(f"data/{SYMBOL.replace('/', '')}_historical.csv") else None
    
    if df is None or len(df) < 5000:
        print("Скачиваем свежие данные...")
        from app.ml_engine import fetch_ohlcv
        df = fetch_ohlcv(SYMBOL, limit=10000)
        df.to_csv(f"data/{SYMBOL.replace('/', '')}_historical.csv", index=False)

    df = df.sort_values('timestamp')

    # Добавляем признаки (то же, что в ml_engine)
    from app.ml_engine import add_features
    df = add_features(df)

    # Цель — предсказание сильного движения
    df['target'] = (df['close'].shift(-6) > df['close'] * 1.003).astype(int)  # +0.3% за ~6 баров

    features = [col for col in df.columns if col not in ['timestamp', 'target', 'close']]
    X = df[features]
    y = df['target']

    train_size = int(len(X) * 0.8)
    X_train, X_val = X.iloc[:train_size], X.iloc[train_size:]
    y_train, y_val = y.iloc[:train_size], y.iloc[train_size:]

    print(f"Размер train: {len(X_train)}, val: {len(X_val)}")

    # Параметры с логированием
    params = {
        'objective': 'binary',
        'metric': 'auc,binary_logloss',
        'boosting_type': 'gbdt',
        'num_leaves': 31,
        'learning_rate': 0.05,
        'feature_fraction': 0.8,
        'bagging_fraction': 0.8,
        'bagging_freq': 5,
        'verbose': -1,
        'seed': 42
    }

    lgb_train = lgb.Dataset(X_train, y_train)
    lgb_val = lgb.Dataset(X_val, y_val, reference=lgb_train)

    print("Начинаем обучение с валидацией...")

    evals_result = {}
    model = lgb.train(
        params,
        lgb_train,
        num_boost_round=800,
        valid_sets=[lgb_train, lgb_val],
        valid_names=['train', 'valid'],
        callbacks=[
            lgb.early_stopping(50),
            lgb.log_evaluation(50),
            lgb.record_evaluation(evals_result)
        ]
    )

    # Сохраняем метрики
    pd.DataFrame(evals_result['valid']).to_csv("logs/training_metrics.csv", index=False)

    # Feature importance
    importance = pd.DataFrame({
        'feature': model.feature_name(),
        'importance': model.feature_importance()
    }).sort_values('importance', ascending=False)

    importance.to_csv("logs/feature_importance.csv", index=False)
    print("\nТОП-10 самых важных признаков:")
    print(importance.head(10))

    # Сохраняем модель
    joblib.dump(model, "models/model.pkl")
    print(f"[{datetime.now()}] Модель успешно обучена и сохранена! AUC на валидации: {model.best_score['valid']['auc']:.4f}")

if __name__ == "__main__":
    train_model()

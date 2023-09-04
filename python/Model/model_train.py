import pandas as pd
from datetime import datetime, timezone
import MetaTrader5 as mt5
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
import numpy as np
import matplotlib.pyplot as plt
import pickle
from util import *


symbol = "EURUSD"
date_ini = datetime(2000, 1, 1, tzinfo=timezone.utc)
date_end = datetime(2022, 12, 31, tzinfo=timezone.utc)
period = mt5.TIMEFRAME_W1

df = get_rates_between(symbol=symbol, period=period, ini=date_ini, end=date_end)

smoothed_df = df.ewm(alpha=0.1).mean()
smoothed_df['macd'], smoothed_df['signal'] = macd(smoothed_df)
smoothed_df['ema'] = ema(smoothed_df)
smoothed_df['rsi'] = rsi(smoothed_df)

selected_df = smoothed_df[['open', 'macd', 'ema', 'rsi', 'close']].dropna()

scaler = MinMaxScaler()
normalized_df = pd.DataFrame(scaler.fit_transform(selected_df), columns=selected_df.columns, index=selected_df.index)

window_size = 2
X, y = sliding_window(normalized_df, window_size)

train_size = int(len(X) * 0.7)
X_train, X_test = X[:train_size], X[train_size:]
y_train, y_test = y[:train_size], y[train_size:]

X_train = X_train.reshape(X_train.shape[0], -1)
X_test = X_test.reshape(X_test.shape[0], -1)

regressor = GradientBoostingRegressor(random_state=42)

'''
param_grid = {
    'n_estimators': [50, 100, 150, 200, 250],
    'learning_rate': [0.01, 0.05, 0.1, 0.15, 0.2, 0.25],
    'max_depth': [None] + list(range(3, 16)),
    'min_samples_split': [2, 3, 4, 5, 6, 7, 8, 9, 10],
    'min_samples_leaf': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    'max_features': ['auto', 'sqrt', 'log2'],
    'subsample': [0.8, 0.9, 1.0],
    'min_weight_fraction_leaf': [0.0, 0.1, 0.2, 0.3, 0.4, 0.5],
    'max_leaf_nodes': [None, 5, 10, 20, 50, 100],
    'alpha': [0.0, 0.1, 0.01, 0.001],
    'beta': [0.0, 0.1, 0.01, 0.001]
}


param_grid = {
    'n_estimators': [50, 100, 500],
    'learning_rate': [0.01, 0.05],
    'max_depth': [10, 50, 100],
    'max_features': ['sqrt', 'log2'],
}

tscv = TimeSeriesSplit(n_splits=2)
grid_search = GridSearchCV(estimator=regressor, param_grid=param_grid, scoring='neg_mean_squared_error', cv=tscv, n_jobs=2, verbose=2)
grid_search.fit(X_train, y_train)

best_params = grid_search.best_params_
print(f"Melhores hiperparâmetros: {best_params}")
'''

best_params = {'learning_rate': 0.001, 'max_depth': 5000, 'max_features': 'log2', 'n_estimators': 10000}

best_regressor = GradientBoostingRegressor(**best_params, random_state=42, verbose=2)
best_regressor.fit(X_train, y_train)

# Salvar o modelo em um arquivo
with open(r'C:\Users\letha\AppData\Roaming\MetaQuotes\Terminal\B8C209507DCA35B09B2C3483BD67B706\MQL5\Experts\Desenvolvimento\Publicacao_Parte_IIII\python\Model\model_train\modelo.pkl', 'wb') as file:
    pickle.dump(best_regressor, file)

# Importar o modelo de um arquivo
with open(r'C:\Users\letha\AppData\Roaming\MetaQuotes\Terminal\B8C209507DCA35B09B2C3483BD67B706\MQL5\Experts\Desenvolvimento\Publicacao_Parte_IIII\python\Model\model_train\modelo.pkl', 'rb') as file:
    loaded_model = pickle.load(file)


y_pred_optimized = loaded_model.predict(X_test)

mae_optimized = mean_absolute_error(y_test, y_pred_optimized)
mse_optimized = mean_squared_error(y_test, y_pred_optimized)
rmse_optimized = np.sqrt(mse_optimized)

print(f"MAE otimizado: {mae_optimized:.4f}")
print(f"MSE otimizado: {mse_optimized:.4f}")
print(f"RMSE otimizado: {rmse_optimized:.4f}")

y_test_real = denormalize_price(normalized_df, scaler, y_test, 'close')
y_pred_optimized_real = denormalize_price(normalized_df, scaler, y_pred_optimized, 'close')

test_index = normalized_df.index[-len(X_test):]
y_test_real = pd.Series(y_test_real, index=test_index)
y_pred_optimized_real = pd.Series(y_pred_optimized_real, index=test_index)

plt.figure(figsize=(10, 6))
plt.plot(y_test_real.index, y_test_real, label='Preço Real', color='blue', marker='o', linestyle='-')
plt.plot(y_pred_optimized_real.index, y_pred_optimized_real, label='Preço Previsto', color='red', marker='o', linestyle='--')
plt.xlabel('Data')
plt.ylabel('Preço')
plt.title('Preço Real vs. Preço Previsto')
plt.legend()
plt.show()

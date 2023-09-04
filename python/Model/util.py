import numpy as np
import pandas as pd
from pandas import to_datetime, DataFrame
from datetime import datetime
import MetaTrader5 as mt5
from sklearn.preprocessing import MinMaxScaler
import pickle

def get_rates_between(symbol: str, period: int, ini: datetime, end: datetime):
    """
    Obtém dados históricos de cotações entre duas datas para um determinado símbolo.

    Args:
        symbol (str): O símbolo do ativo para obter os dados.
        period (int): O período de cotação.
        ini (datetime): Data inicial para obter as cotações.
        end (datetime): Data final para obter as cotações.

    Returns:
        pandas.DataFrame: DataFrame contendo os dados históricos de cotações.
    """
    if not mt5.initialize():
        print("initialize() falhou")
        mt5.shutdown()
        raise Exception("Erro ao obter dados")

    rates = mt5.copy_rates_range(symbol, period, ini, end)
    mt5.shutdown()
    rates = DataFrame(rates)

    if rates.empty:
        raise Exception("Erro ao obter dados")

    rates['time'] = to_datetime(rates['time'], unit='s')
    rates.set_index(['time'], inplace=True)

    return rates

def sliding_window(df, window_size):
    """
    Divide o DataFrame em janelas deslizantes.

    Esta função recebe um DataFrame contendo dados temporais e divide-o em janelas deslizantes
    para uso em tarefas de séries temporais.

    Args:
        df (pandas.DataFrame): DataFrame contendo os dados temporais.
        window_size (int): Tamanho da janela deslizante.

    Returns:
        tuple: Retorna uma tupla contendo duas matrizes numpy:
            - X (numpy.ndarray): Matriz de entrada, contendo as janelas de dados.
            - y (numpy.ndarray): Matriz de saída, contendo os valores correspondentes à última coluna
              do DataFrame original para cada janela.

    Exemplo:
        >>> df = pd.DataFrame({'feature1': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        ...                    'feature2': [11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
        ...                    'target': [21, 22, 23, 24, 25, 26, 27, 28, 29, 30]})
        >>> X, y = sliding_window(df, window_size=3)
        >>> print(X)
        array([[ 1,  2,  3, 11, 12, 13],
               [ 2,  3,  4, 12, 13, 14],
               [ 3,  4,  5, 13, 14, 15],
               [ 4,  5,  6, 14, 15, 16],
               [ 5,  6,  7, 15, 16, 17],
               [ 6,  7,  8, 16, 17, 18],
               [ 7,  8,  9, 17, 18, 19]])
        >>> print(y)
        array([24, 25, 26, 27, 28, 29])
    """
    X = []
    y = []
    for i in range(len(df) - window_size):
        window_X = df.iloc[i:i+window_size, :-1].values  # Características de entrada
        window_y = df.iloc[i+window_size, -1]            # Valor alvo
        X.append(window_X)
        y.append(window_y)
    return np.array(X), np.array(y)


def denormalize_price(dataset, scaler, normalized_price, column_name):
    """
    Denormaliza os preços normalizados.

    Args:
        dataset (pandas.DataFrame): DataFrame original contendo os dados normalizados.
        scaler (sklearn.preprocessing.MinMaxScaler): O scaler usado para normalizar os dados.
        normalized_price (numpy.array): Array contendo os preços normalizados.
        column_name (str): Nome da coluna de preços no DataFrame original.

    Returns:
        numpy.array: Array contendo os preços denormalizados.
    """
    dummy_df = DataFrame(np.zeros((len(normalized_price), len(dataset.columns))), columns=dataset.columns)
    dummy_df[column_name] = normalized_price
    denormalized_df = scaler.inverse_transform(dummy_df)
    return denormalized_df[:, dataset.columns.get_loc(column_name)]

def macd(df, fast_period=12, slow_period=26, signal_period=9):
    """
    Calcula o Moving Average Convergence Divergence (MACD) para um DataFrame.

    Args:
        df (pandas.DataFrame): DataFrame contendo os dados.
        fast_period (int, optional): Período da média exponencial rápida. Default é 12.
        slow_period (int, optional): Período da média exponencial lenta. Default é 26.
        signal_period (int, optional): Período da linha de sinal. Default é 9.

    Returns:
        tuple: Tupla contendo a linha MACD e a linha de sinal.
    """
    ema_fast = df['close'].ewm(span=fast_period).mean()
    ema_slow = df['close'].ewm(span=slow_period).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal_period).mean()
    return macd_line, signal_line

def ema(df, period=30):
    """
    Calcula a Média Móvel Exponencial (EMA) para um DataFrame.

    Args:
        df (pandas.DataFrame): DataFrame contendo os dados.
        period (int, optional): Período da EMA. Default é 30.

    Returns:
        pandas.Series: A EMA calculada.
    """
    return df['close'].ewm(span=period).mean()

def rsi(df, period=14):
    """
    Calcula o Índice de Força Relativa (RSI) para um DataFrame.

    Args:
        df (pandas.DataFrame): DataFrame contendo os dados.
        period (int, optional): Período do RSI. Default é 14.

    Returns:
        pandas.Series: O RSI calculado.
    """
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def prepare_data(data, steps, N):
    """
    Prepara os dados em sequências para treinamento do modelo.

    Args:
        data (pandas.Series): Série temporal contendo os dados.
        steps (int): Tamanho da janela de entrada.
        N (int): Número de amostras a serem previstas.

    Returns:
        list: Lista contendo as sequências preparadas.
    """
    prepared_data = []
    for i in range(len(data)-steps-N+1):
        prepared_data.append(data[i:i+steps+N])
    return prepared_data

def predict_series(data: pd.DataFrame, model_path: str, window_size: int = 26):
    """
    Faz previsões usando um modelo treinado.

    Args:
        data (pandas.DataFrame): DataFrame contendo os dados para prever.
        model_path (str): Caminho para o arquivo do modelo treinado.
        window_size (int, optional): Tamanho da janela para a preparação dos dados. Default é 26.

    Returns:
        numpy.array: Array contendo as previsões desnormalizadas.
    """
    if not isinstance(data, pd.DataFrame):
        raise ValueError("Os dados devem ser um DataFrame do pandas.")
        
    if len(data) < window_size:
        raise ValueError(f"Os dados devem conter pelo menos {window_size} linhas.")
    
    scaler = MinMaxScaler()
    normalized_data = pd.DataFrame(scaler.fit_transform(data), columns=data.columns, index=data.index)
    
    if len(normalized_data) < window_size:
        raise ValueError(f"A série de dados deve conter pelo menos {window_size} linhas para usar uma janela de tamanho {window_size}.")

    X, _ = sliding_window(normalized_data, window_size)

    with open(model_path, 'rb') as file:
        loaded_model = pickle.load(file)

    normalized_prediction = loaded_model.predict(X)
    
    denormalized_prediction = denormalize_price(normalized_data, scaler, normalized_prediction, 'close')
    
    return denormalized_prediction

def predict_next_week(data: pd.DataFrame, model_path: str, window_size: int = 26):
    """
    Faz uma previsão de um passo à frente usando um modelo treinado.

    Args:
        data (pandas.DataFrame): DataFrame contendo os dados para prever.
        model_path (str): Caminho para o arquivo do modelo treinado.
        window_size (int, optional): Tamanho da janela para a preparação dos dados. Default é 26.

    Returns:
        numpy.array: Array contendo a previsão desnormalizada.
    """
    if not isinstance(data, pd.DataFrame):
        raise ValueError("Os dados devem ser um DataFrame do pandas.")
        
    if len(data) < window_size:
        raise ValueError(f"Os dados devem conter pelo menos {window_size} linhas.")
    
    scaler = MinMaxScaler()
    normalized_data = pd.DataFrame(scaler.fit_transform(data), columns=data.columns, index=data.index)
    
    if len(normalized_data) < window_size:
        raise ValueError(f"A série de dados deve conter pelo menos {window_size} linhas para usar uma janela de tamanho {window_size}.")

    X, _ = sliding_window(normalized_data, window_size)
    X = X.reshape(X.shape[0], -1)    

    with open(model_path, 'rb') as file:
        loaded_model = pickle.load(file)

    # Pega a janela de dados mais recentes e faz a previsão
    normalized_prediction = loaded_model.predict(X[-1].reshape(1, -1))
    
    denormalized_prediction = denormalize_price(normalized_data, scaler, normalized_prediction, 'close')
    
    return denormalized_prediction

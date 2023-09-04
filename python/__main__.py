from Services import File
from pandas import DataFrame
import ast
import time
import pandas as pd
from datetime import datetime, timezone
import MetaTrader5 as mt5
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import pickle
from Model import *
import os

PATH_COMMON = r'C:\Users\letha\AppData\Roaming\MetaQuotes\Terminal\Common\Files\TransferML\{}.csv'
INIT_ARCHIVE = 'init'
INIT_OK_ARCHIVE = 'init_checked'
TESTE_ARCHIVE = 'mode_test'
TESTE_PREDICT = 'predict_test'
MODEL_PATH = r'C:\Users\letha\AppData\Roaming\MetaQuotes\Terminal\B8C209507DCA35B09B2C3483BD67B706\MQL5\Experts\Desenvolvimento\Publicacao_Parte_IIII\python\Model\model_train\modelo.pkl'  # caminho para o modelo promovido

IDX = lambda n: n
window_size = 2  # tamanho da janela

def main():
    file = File()
    file.delete_file(PATH_COMMON.format(INIT_ARCHIVE))
    file.delete_file(PATH_COMMON.format(INIT_OK_ARCHIVE))
    file.delete_file(PATH_COMMON.format(TESTE_ARCHIVE))
    file.delete_file(PATH_COMMON.format(TESTE_PREDICT))

    while True:
        print("<<--Aguardando o arquivo de configuração-->>")
        typerun = file.check_init_param(PATH_COMMON.format(INIT_ARCHIVE))
        time.sleep(1)

        file.save_file_csv(PATH_COMMON.format(INIT_OK_ARCHIVE))

        if typerun == 0:
            print('<<-- {} -->>'.format("Script Python - Modo Teste"))
            while True:
                receive = file.check_open_file(PATH_COMMON.format(TESTE_ARCHIVE))
                file.delete_file(PATH_COMMON.format(TESTE_ARCHIVE))

                if len(receive) == 0:
                    continue

                if receive["command"][0].upper() == "START":
                    header = ["open", "close"]
                    payload = []

                    for i in range(len(receive)):
                        row = [
                            str(receive["open"][i]),
                            str(receive["close"][i])
                        ]
                        payload.append(row)

                    df = pd.DataFrame(payload, columns=header)
                    smoothed_df = df.ewm(alpha=0.1).mean()
                    smoothed_df['macd'], smoothed_df['signal'] = macd(smoothed_df)
                    smoothed_df['ema'] = ema(smoothed_df)
                    smoothed_df['rsi'] = rsi(smoothed_df)
                    selected_df = smoothed_df[['open', 'macd', 'ema', 'rsi', 'close']].dropna()
   
                    # Fazendo previsões
                    next_week_prediction = predict_next_week(selected_df, MODEL_PATH, window_size)
                    file.save(PATH_COMMON.format(TESTE_PREDICT), str(next_week_prediction[0]))
                    continue

                elif receive["command"][0].upper() == "STOP":
                    file.delete_file(PATH_COMMON.format(TESTE_PREDICT))
                    continue


if __name__ == "__main__":
    main()
from pathlib import Path
from time import sleep
from typing import Tuple
import pandas as pd
from pandas.core.frame import DataFrame
import os
from errno import EACCES, EPERM, ENOENT
import sys

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

CSV_SEPARATOR = ';'

class File(metaclass=Singleton):

    def __init__(self) -> None:
        pass

    def __init_file(self, name_arq: str) -> bool:
        return Path(name_arq).is_file() or sleep(1) or False

    def __handle_error(self, e, name_arq: str):
        ERRORS = {
            EPERM: "PermissionError",
            EACCES: "PermissionError",
            ENOENT: "FileNotFoundError"
        }
        print(f"{ERRORS.get(e.errno, 'Unknown error')} error({e.errno}): {e.strerror} for:\n{name_arq}")

    def check_init_param(self, name_arq : str) -> Tuple[str]:
        while True:
            try:
                if self.__init_file(name_arq):
                    df = pd.read_csv(name_arq, sep=CSV_SEPARATOR)
                    return (df.typerun.values[0])
            except (IOError, OSError) as e:
                self.__handle_error(e, name_arq)
            except:
                print('Unexpected error:', sys.exc_info()[0])

    def check_open_file(self, name_arq: str) -> pd.DataFrame():
        while True:
            try:
                if self.__init_file(name_arq):
                    return pd.read_csv(name_arq, sep=CSV_SEPARATOR)
            except (IOError, OSError) as e:
                self.__handle_error(e, name_arq)
            except:
                print('Unexpected error:', sys.exc_info()[0])

    @staticmethod
    def save_file_csv(name_arq: str, dataset:DataFrame = pd.DataFrame({'col':['ok']})):
        dataset.to_csv(name_arq, sep=CSV_SEPARATOR)

    @staticmethod
    def save(name_arq:str, data:str):
        with open(name_arq, 'w') as f:
            f.write(data)

    @staticmethod
    def delete_file(name_arq: str):
        try:
            os.remove(name_arq)
        except:
            pass
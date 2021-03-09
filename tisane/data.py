import os
import pandas as pd 
from typing import Union

class Dataset(object): 
    # data_vectors: dict
    data : pd.DataFrame

    # Takes input in either a CSV or a Pandas DataFrame
    def __init__(self, source: Union[str, pd.DataFrame]): 
        df = None
        if isinstance(source, str): 
            df = pd.read_csv(source)

        if isinstance(source, pd.DataFrame): 
            data = source

class DataVector(object): 
    name: str
    values: pd.DataFrame 

    # def __init__(self, name: str, values: pd.DataFrame): 
    #     self.name = name
    #     self.values = values

    def get_cardinality(self): 
        pass
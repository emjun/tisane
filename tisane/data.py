import pandas as pd 

class Dataset(object): 
    data_vectors: dict


class DataVector(object): 
    name: str
    values: pd.DataFrame 

    # def __init__(self, name: str, values: pd.DataFrame): 
    #     self.name = name
    #     self.values = values

    def get_cardinality(self): 
        pass
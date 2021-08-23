import os
import pandas as pd
from typing import Union

from pandas.core.frame import DataFrame


def absolute_path(p: str) -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), p)


class Dataset(object):
    dataset: pd.DataFrame
    data_path: os.path

    # Takes input in either a CSV or a Pandas DataFrame
    def __init__(self, source: Union[str, pd.DataFrame]):
        df = None
        # Read in data
        if isinstance(source, str):
            abs_path = absolute_path(p=source)
            self.data_path = abs_path  # store
            df = pd.read_csv(abs_path)
        elif isinstance(source, pd.DataFrame):
            df = source
            self.data_path = None

        # TODO: post-processing? E.g., break up into DataVectors?
        self.dataset = df

    def get_data(self) -> pd.DataFrame:
        return self.dataset

    def get_column(self, name: str):
        cols = self.dataset.columns
        if name in cols:
            return self.dataset[name]
        else:
            raise ValueError(
                f"Variable with name {name} is not part of the dataset. Columns: {cols}"
            )

    def get_length(self):
        if self.dataset is not None:
            return len(self.dataset.index)
            # else:
            return 0


class DataVector(object):
    name: str
    values: pd.DataFrame

    # def __init__(self, name: str, values: pd.DataFrame):
    #     self.name = name
    #     self.values = values

    def get_cardinality(self):
        pass

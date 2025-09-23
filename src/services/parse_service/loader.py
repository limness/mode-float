from typing import Optional, Any, Union
from abc import ABC, abstractmethod
import pandas as pd


class Loader(ABC):
    @abstractmethod
    def load(self) -> Union[pd.DataFrame, pd.Series]:
        pass


class ExcelLoader(Loader):
    def __init__(self, source: Any, sheet_name: Optional[str] = 0, usecols=None):
        self.source = source
        self.sheet_name = sheet_name
        self.usecols = usecols

    def load(self) -> pd.DataFrame:
        df = pd.read_excel(self.source, sheet_name=self.sheet_name,
                           usecols=self.usecols, engine="openpyxl")
        return df

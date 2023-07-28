from abc import ABC, abstractmethod
from typing import Union

import pandas as pd


class MetData:
    """
    A class to represent weather data.
    """

    def __init__(self, metadata: dict, data: pd.DataFrame):
        self.metadata = metadata
        self.data = data


class GlmMet(ABC):
    """
    An abstract class for GLM weather data.
    """

    def __init__(
        self,
        location: tuple[float, float],
        date_range: tuple[str, str],
        variables: list[str],
        met_data: Union[None, MetData],
        glm_met_data: Union[None, pd.DataFrame],
    ):
        self.location = location
        self.date_range = date_range
        self.variables = variables
        self.met_data = met_data
        self.glm_met_data = glm_met_data

    @abstractmethod
    def get_variables(self) -> None:
        """Get variables from weather data provider."""
        pass

    @abstractmethod
    def write_met(self) -> None:
        """Save weather data from data provider."""
        pass

    @abstractmethod
    def convert_to_glm(self) -> None:
        """Convert weather data to GLM format."""
        pass

    @abstractmethod
    def write_glm_met(self) -> None:
        """Save weather data in GLM format."""
        pass

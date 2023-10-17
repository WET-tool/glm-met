import json
import os
import tempfile
import zipfile
from typing import Union

import pandas as pd
import requests

from io import StringIO

from glm_met import glm_met

from . import settings


class MetData(glm_met.MetData):
    """
    Class for meteorological data and its associated metadata.

    Used  to store meteoroligcal data downloaded from the
    SILO API.

    Attributes
    ----------
    metadata : (dict)
        Metadata associated with the meteorological data.
    data : (pd.DataFrame)
        Meteorological data in a Pandas DataFrame.
    """

    def __init__(self, metadata: dict, data: pd.DataFrame):
        self.metadata = metadata
        self.data = data


class Silo(glm_met.GlmMet):
    """
    Class for retrieving and processing historical meteorological data from
    the SILO API.

    Examples
    --------
    >>> import os
    >>> import glm_met.silo.silo as silo
    >>> s = silo.Silo(
    ...            location=(116.6, -32.17),
    ...            date_range=("20220101", "20220131"),
    ...            met_data=None,
    ...            format="csv",
    ...            comment="rxel",
    ...            username="test@email.com",
    ...            api="data_drill"
    ...        )
    >>> s.get_variables(request_settings=None)
    >>> s.write_met(path="silo-data")

    After successful call to `get_variables()`, the `met_data` attribute
    of the `Silo` type object, `s`, is a `MetData` type object.
    This object has two attributes: a metadata dict and a DataFrame of
    met data values.

    >>> metadata = s.met_data.metadata
    >>> met_data_df = s.met_data.data
    """

    def __init__(
        self,
        location: Union[int, tuple[float, float]],
        date_range: tuple[str, str],
        met_data: Union[None, MetData],
        comment: Union[None, str],
        username: str,
        api: str,
    ):
        """
        Initialise object to download data from the SILO API.

        Parameters
        ----------
        location : Union[int, tuple[float, float]]
            Station number for the patch point API or
            latitude and longitude tuple for the drill down grid
            API.
        date_range : tuple[str, str]
            Start and end dates for the data retrieval
            (in "YYYYMMDD" format).
        met_data : Union[None, MetData]
            Attribute to store meteorological data downloaded from SILO API.
        comment :  str
            String codes representing meteorological variables to download.
            See list of variables here: `https://www.longpaddock.qld.gov.au/silo/about/climate-variables/`
            For example, `"rxel"` will download rainfall, max temperature,
            evaporation, and Morton's shallow lake evaporation.
        username : str
            Email address that must be provided.
        api :  str
            Either "drill_down" for the retrieving point-like data from the gridded
            SILO product or "patch_point" for station data.

        """
        self.location = location
        self.date_range = date_range
        self.met_data = met_data
        self.format = "csv"
        self.comment = comment
        self.username = username
        self.api = api

    def get_variables(self, request_settings: Union[None, dict]) -> MetData:
        """
        Get variables from the SILO API and store them
        in the `met_data` attribute.

        Parameters
        ----------
        request_settings : Union[None, dict]
            Dictionary object of extra settings to pass in as query parameters to
            the SILO API.
        """

        if self.api == "data_drill":
            # location should be tuple - lat and lon
            if type(self.location) == tuple:
                if self.format == "json" or self.format == "csv":
                    payload = {
                        "lon": self.location[0],
                        "lat": self.location[1],
                        "start": self.date_range[0],
                        "finish": self.date_range[1],
                        "format": self.format,
                        "comment": self.comment,
                        "username": self.username,
                        "password": "apirequest",
                    }

                else:
                    payload = {
                        "lon": self.location[0],
                        "lat": self.location[1],
                        "start": self.date_range[0],
                        "finish": self.date_range[1],
                        "format": self.format,
                        "username": self.username,
                        "password": "apirequest",
                    }

                # if user has supplied extra query parameters, append them here.
                if request_settings:
                    payload = {**payload, **request_settings}

                r = requests.get(settings.data_drill_api, params=payload)

                df = pd.read_csv(StringIO(r.text))

                # make meta data dict
                metadata_col = df.loc[:, "metadata"]
                elevation = metadata_col.iloc[0].split("= ")[1].split(" m")[0]
                metadata = {
                    "longitude": self.location[0],
                    "latitude": self.location[1],
                    "start": self.date_range[0],
                    "finish": self.date_range[1],
                    "api": self.api,
                    "format": self.format,
                    "comment": self.comment,
                    "elevation": elevation,
                }

                df = df.drop(columns=["metadata"])
                self.met_data = MetData(metadata=metadata, data=df)

        elif self.api == "patch_point":
            # location should be int type - station number
            if type(self.location) == int:
                if self.format == "json" or self.format == "csv":
                    payload = {
                        "station": self.location,
                        "start": self.date_range[0],
                        "finish": self.date_range[1],
                        "format": self.format,
                        "comment": self.comment,
                        "username": self.username,
                        "password": "apirequest",
                    }

                else:
                    payload = {
                        "station": self.location,
                        "start": self.date_range[0],
                        "finish": self.date_range[1],
                        "format": self.format,
                        "username": self.username,
                        "password": "apirequest",
                    }

                # if user has supplied extra query parameters, append them here.
                if request_settings:
                    payload = {**payload, **request_settings}

                r = requests.get(settings.patch_point_api, params=payload)

                df = pd.read_csv(StringIO(r.text))

                # make meta data dict
                metadata_col = df.loc[:, "metadata"]
                elevation = metadata_col.iloc[3].split("= ")[1].split(" m")[0]
                lat = metadata_col.iloc[1].split("= ")[1]
                lon = metadata_col.iloc[2].split("= ")[1]
                name = metadata_col.iloc[0].split("=")[1]

                metadata = {
                    "station": self.location,
                    "station_name": name,
                    "longitude": lon,
                    "latitude": lat,
                    "start": self.date_range[0],
                    "finish": self.date_range[1],
                    "api": self.api,
                    "format": self.format,
                    "comment": self.comment,
                    "elevation": elevation,
                }

                df = df.drop(columns=["metadata"])
                self.met_data = MetData(metadata=metadata, data=df)

    def write_met(self, path: str) -> None:
        """
        Save meteorological data and its metadata to a zip file.

        Parameters
        ----------
        path : str
            Path to the directory where the zip file should be saved.
        """

        with tempfile.TemporaryDirectory() as tmpdir:
            self.met_data.data.to_csv(
                os.path.join(tmpdir, "met_raw.csv"), index=False
            )

            with open(
                os.path.join(tmpdir, "met_raw_metadata.json"), "w"
            ) as dst:
                json.dump(self.met_data.metadata, dst)

            data_fpath = os.path.join(tmpdir, "met_raw.csv")
            metadata_fpath = os.path.join(tmpdir, "met_raw_metadata.json")

            files = [data_fpath, metadata_fpath]

            with zipfile.ZipFile(
                os.path.join(path, "met_raw.zip"), mode="w"
            ) as z_dst:
                for file in files:
                    z_dst.write(file, arcname=file.split("/")[-1])

    def convert_to_glm(self) -> None:
        """Convert weather data to GLM format."""
        pass

    def write_glm_met(self) -> None:
        """Save weather data in GLM format."""
        pass

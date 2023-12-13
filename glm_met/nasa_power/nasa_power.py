import json
import os
import tempfile
import zipfile
from typing import Union

import pandas as pd
import requests

from glm_met import glm_met

from . import settings


class MetData(glm_met.MetData):
    """
    Class for meteorological data and its associated metadata.

    Used  to store meteoroligcal data downloaded from the
    NASA POWER API.

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


class Power(glm_met.GlmMet):
    """
    Class for retrieving and processing meteorological data from
    the NASA POWER API.
    """

    # class attribute storing base URL for openmeteo historical API
    nasa_power_api_url = settings.nasa_power_api_url

    def __init__(
        self,
        location: tuple[float, float],
        date_range: tuple[str, str],
        met_data: Union[None, MetData],
        glm_met_data: Union[None, pd.DataFrame],
        parameters: Union[None, list[str]],
        timezone: str = "LST",
        community: str = "SB",
    ):
        """Initialises a `Power` object retrieving and storing
        meteorological data from NASA POWER's API.

        Parameters
        ----------
        location : tuple[float, float]
            Latitude and longitude of the location for the data retrieval.
        date_range : tuple[str, str]
            Start and end dates for the data retrieval
            (in ISO 8601 format, e.g., "YYYY-MM-DD").
        met_data : Union[None, MetData]
            Attribute to store meteorological data downloaded from open-meteo.
        glm_met_data : Union[None, pd.DataFrame]
            Attribute to store meteorological data downloaded from open-meteo
            in GLM format.
        parameters : Union[None, list[str]]
            List of meteorological variables to retrieve. The default is
            to use the list specified in `settings.hourly_glm_default`.
        timezone : str
            LST - local solar time or UTC.
        community : str
            `SB` for sustainable buildings and `AG` for agroclimatology.
        """
        self.location = location
        self.date_range = date_range
        self.met_data = met_data
        self.glm_met_data = glm_met_data
        self.timezone = timezone
        self.parameters = parameters
        self.community = community
        self.r_format = "JSON"

    def get_variables(self, request_settings: Union[None, dict]) -> MetData:
        """
        Get variables from the NASA POWER hourly API and store them
        in the `met_data` attribute.

        If you need to pass in extra settings to the API, pass these into
        the `get_variables()` method as a dict object. These settings will
        be appended to the API request as query parameters.

        Parameters
        ----------
        request_settings : Union[None, dict]
            Dictionary object of extra settings to pass in as query parameters.
        """

        # hourly
        if self.parameters is None:
            self.parameters = settings.hourly_glm_default

        payload = {
            "longitude": self.location[0],
            "latitude": self.location[1],
            "start": self.date_range[0].replace("-", ""),
            "end": self.date_range[1].replace("-", ""),
            "parameters": (",").join(self.parameters),
            "timezone": self.timezone,
            "community": self.community,
            "format": self.r_format,
        }

        # if user has supplied extra query parameters, append them here.
        if request_settings:
            payload = {**payload, **request_settings}

        r = requests.get(Power.nasa_power_api_url, params=payload)
        r_json = r.json()
        df = pd.DataFrame(r_json["properties"]["parameter"])
        metadata = {
            key: r_json[key]
            for key in r_json.keys() & {"header", "parameters"}
        }

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
        """
        Convert hourly meteorological data to GLM format
        and store it in the `glm_met_data` attribute.

        This function only works with hourly data, this method expects the
        `met_data.data` attribute of the `Power` object to have the
        following variables: `"ALLSKY_SFC_SW_DWN"`, `"CLOUD_AMT"`, `"T2M"`, `"RH2M"`,
        `"WS2M"`, `"PRECTOTCORR"`.

        If the data in `met_data.data` has different
        variables, you will need to write your own function to convert the data
        to GLM format.

        `CLOUD_AMT` from NASA POWER is in percentage units. GLM requires it as
        a proportion (0.0 to 1.0).

        `precipitation` is in mm. GLM requires it in m / day even if
        using hourly data, so it is converted.
        """

        df_glm = pd.DataFrame(
            # glm requires time to have "hh:mm:ss" - append :00 to date-time string
            data={
                "time": pd.to_datetime(
                    self.met_data.data.index, format="%Y%m%d%H"
                ).astype(str),
                "ShortWave": self.met_data.data["ALLSKY_SFC_SW_DWN"],
                "Cloud": self.met_data.data["CLOUD_AMT"] / 100,
                "AirTemp": self.met_data.data["T2M"],
                "RelHum": self.met_data.data["RH2M"],
                "WindSpeed": self.met_data.data["WS2M"],
                "Rain": (self.met_data.data["PRECTOTCORR"] / 1000) * 24,
            }
        ).reset_index(drop=True)

        self.glm_met_data = df_glm

    def write_glm_met(self, path: str, zip_f: bool, fname: str) -> None:
        """
        Save meteorological data in GLM format and its metadata to file.

        Only works after a call to `convert_to_glm()` and with hourly
        data.

        Parameters
        ----------
        path : str
            Path to the directory where the zip file should be saved.
        zip_f : bool
            Whether to save output to a zip file.
        fname : str
            If zip_f is `True`, filename for GLM meteorological data csv.
        """

        glm_metadata = self.met_data.metadata

        if zip_f:
            with tempfile.TemporaryDirectory() as tmpdir:
                self.glm_met_data.to_csv(
                    os.path.join(tmpdir, "met.csv"), index=False
                )

                with open(
                    os.path.join(tmpdir, "met_glm_metadata.json"), "w"
                ) as dst:
                    json.dump(glm_metadata, dst)

                data_fpath = os.path.join(tmpdir, "met.csv")
                metadata_fpath = os.path.join(tmpdir, "met_glm_metadata.json")

                files = [data_fpath, metadata_fpath]

                with zipfile.ZipFile(
                    os.path.join(path, "met_glm.zip"), mode="w"
                ) as z_dst:
                    for file in files:
                        z_dst.write(file, arcname=file.split("/")[-1])
        else:
            self.glm_met_data.to_csv(os.path.join(path, fname), index=False)

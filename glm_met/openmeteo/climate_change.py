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
    def __init__(self, metadata: dict, data: pd.DataFrame):
        """
        Class for meteorological data and its associated metadata.

        Used within instances of the `ClimateChange` class to store
        meteoroligcal data downloaded from the open-meteo
        climate API.

        Attributes
        ----------
        metadata : (dict)
            Metadata associated with the meteorological data.
        data : (pd.DataFrame)
            Meteorological data in a Pandas DataFrame.
        """
        self.metadata = metadata
        self.data = data


class ClimateChange(glm_met.GlmMet):
    """
    Class for retrieving and processing daily climate change data from
    open-meteo's Climate API.

    Examples
    --------
    >>> import os
    >>> import glm_met.openmeteo.climate_change as climate
    >>> clim = climate.ClimateChange(
    ...            location=(116.691155, -34.225812),
    ...            date_range=("2022-01-01", "2032-12-31"),
    ...            met_data=None,
    ...            glm_met_data=None
    ...        )
    >>> clim.get_variables(request_settings=None)
    >>> clim.convert_to_glm()
    >>> clim.write_glm_met(path=os.getcwd())
    """

    # class attribute storing base URL for openmeteo climate API
    climate_api_url = settings.climate_api_url

    def __init__(
        self,
        location: tuple[float, float],
        date_range: tuple[str, str],
        met_data: Union[None, MetData],
        glm_met_data: Union[None, dict],
        models: list[str] = settings.climate_models,
        variables: list[str] = settings.climate_glm_default,
    ):
        """
        Initialize the `ClimateChange` object for retrieving and storing
        meteorological data from open-meteo's Climate API.

        Parameters
        ----------
        location : tuple[float, float]
            Latitude and longitude of the location for the data retrieval.
        date_range : tuple[str, str]
            Start and end dates for the data retrieval
            (in ISO 8601 format, e.g., "YYYY-MM-DD").
        met_data : Union[None, MetData]
            Attribute to store meteorological data downloaded from open-meteo.
        glm_met_data : Union[None, dict]
            Attribute to store meteorological data downloaded from open-meteo
            in GLM format. Dictionary of DataFrames with each DataFrame
            corresponding to a climate model in models.
        models : list[str]
            List of Climate models to download data from.
            Seven models are supported by open-meteo's Climate API:
            https://open-meteo.com/en/docs/climate-api. The default is
            to use all seven models, as specified in `settings.climate_models`.
        variables : list[str]
            List of meteorological variables to retrieve. The default is
            to use the list specified in `settings.climate_glm_default`.
        """
        self.location = location
        self.date_range = date_range
        self.met_data = met_data
        self.glm_met_data = glm_met_data
        self.models = models
        self.variables = variables

    def get_variables(self, request_settings: Union[None, dict]) -> MetData:
        """
        Get variables from the open-meteo Climate API provider and store them
        in the `met_data` attribute.

        Here, windspeed is requested in units of m/s.

        If you need to pass in extra settings to the API, pass these into
        the `get_variables()` method as a dict object. These settings will
        be appended to the API request as query parameters.

        Parameters
        ----------
        request_settings : Union[None, dict]
            Dictionary object of extra settings to pass in as query parameters
            to the open-meteo Climate API. Latitude, longitude, start data,
            end date, daily weather variables, and windspeed units are set from
            the ClimateChange object attributes. Find a list of settings here:
            https://open-meteo.com/en/docs/climate-api
        """

        payload = {
            "longitude": self.location[0],
            "latitude": self.location[1],
            "start_date": self.date_range[0],
            "end_date": self.date_range[1],
            "daily": self.variables,
            "models": self.models,
            "windspeed_unit": "ms",
        }

        # if user has supplied extra query parameters, append them here.
        if request_settings:
            payload = {**payload, **request_settings}

        r = requests.get(self.climate_api_url, params=payload)
        r_json = r.json()
        df = pd.DataFrame(r_json.pop("daily"))
        metadata = r_json

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
        Convert meteorological data to GLM format
        and store it in the `glm_met_data` attribute.

        This method expects the `met_data.data` attribute of the `ClimateChange`
        object to have the following variables: `time`, `shortwave_radiation_sum`,
        `cloudcover_mean`, `temperature_2m_mean`, `relative_humidity_2m_mean`,
        `windspeed_10m_mean` and `precipitation_sum`.

        If the data in `met_data.data` has different variables,
        you will need to write your own function to convert the data
        to GLM format.

        `cloudcover` from openmeteo is in percentage. GLM requires it as a proportion
        (0.0 to 1.0).

        `precipitation` is in mm. GLM requires it in m so it is converted.

        Not all meteorological variables required by GLM are available for every
        model. Missing data values will be returned for these cases. Values in the
        `time` column are in `YYYY-MM-DD` format. If `hh:mm:ss` values are
        required, these will need to be added in a subsequent processing step.
        """

        climate_models_glm = {}

        for m in self.models:
            tmp_data = {
                "time": self.met_data.data["time"],
                "ShortWave": self.met_data.data[
                    f"shortwave_radiation_sum_{m}"
                ],
                "Cloud": self.met_data.data[f"cloudcover_mean_{m}"] / 100,
                "AirTemp": self.met_data.data[f"temperature_2m_mean_{m}"],
                "RelHum": self.met_data.data[f"relative_humidity_2m_mean_{m}"],
                "WindSpeed": self.met_data.data[f"windspeed_10m_mean_{m}"],
                "Rain": self.met_data.data[f"precipitation_sum_{m}"] / 1000,
            }

            climate_models_glm[m] = pd.DataFrame(tmp_data)

        self.glm_met_data = climate_models_glm

    def write_glm_met(self, path: str) -> None:
        """
        Save meteorological data in GLM format and its metadata to file.

        Data associated with a different climate model is written to
        a different csv file. The climate models name is included in
        the csv file's name.

        A zip file of csv files is written to `path`.

        Parameters
        ----------
        path : str
            Path to the directory where the zip file should be saved.
        """

        files = []
        with tempfile.TemporaryDirectory() as tmpdir:
            for m in self.models:
                tmp_df = self.glm_met_data[m]
                tmp_df.to_csv(
                    os.path.join(tmpdir, f"met_{m}.csv"), index=False
                )
                files.append(os.path.join(tmpdir, f"met_{m}.csv"))

            with zipfile.ZipFile(
                os.path.join(path, "met_glm.zip"), mode="w"
            ) as z_dst:
                for file in files:
                    z_dst.write(file, arcname=file.split("/")[-1])

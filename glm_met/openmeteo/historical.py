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

    Used within instances of the `Historical` class to store
    meteoroligcal data downloaded from the open-meteo
    historical API.

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


class Historical(glm_met.GlmMet):
    """
    Class for retrieving and processing historical meteorological data from
    open-meteo's historical API.

    Examples
    --------
    >>> import os
    >>> import glm_met.openmeteo.historical as historical
    >>> hist = historical.Historical(
    ...            location=(116.691155, -34.225812),
    ...            date_range=("1970-01-01", "2022-12-31"),
    ...            variables=["temperature_2m", "relativehumidity_2m"],
    ...            met_data=None,
    ...            glm_met_data=None
    ...        )
    >>> hist.get_variables(request_settings=None)
    >>> hist.convert_to_glm()
    >>> hist.write_glm_met(path=os.getcwd(), zip_f=False, fname="met.csv")

    After successful call to `get_variables()`, the `met_data` attribute
    of the `Historical` type object, `hist`, is a `MetData` type object.
    This object has two attributes: a metadata dict and a DataFrame of
    met data values.

    >>> metadata = hist.met_data.metadata
    >>> met_data_df = hist.met_data.data
    """

    # class attribute storing base URL for openmeteo historical API
    historical_api_url = settings.historical_api_url

    def __init__(
        self,
        location: tuple[float, float],
        date_range: tuple[str, str],
        met_data: Union[None, MetData],
        glm_met_data: Union[None, pd.DataFrame],
        variables: Union[None, list[str]],
        timezone: str = "auto",
        hourly: bool = True,
    ):
        """Initialises a `Historical` object retrieving and storing
        meteorological data from open-meteo's Historical API.

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
        variables : Union[None, list[str]]
            List of meteorological variables to retrieve. The default is
            to use the list specified in `settings.hourly_historical_glm_default`
            or `settings.daily_historical_glm_default.
        timezone : str, optional
            Timezone for the data retrieval. Default is "auto".
        hourly : bool, optional
            If True, retrieve hourly data; otherwise, retrieve daily data.
            Default is True.
        """
        self.location = location
        self.date_range = date_range
        self.met_data = met_data
        self.glm_met_data = glm_met_data
        self.timezone = timezone
        self.hourly = hourly
        self.variables = variables

    def get_variables(self, request_settings: Union[None, dict]) -> MetData:
        """
        Get variables from the open-meteo Historical API provider and store them
        in the `met_data` attribute.

        Here, windspeed is requested in units of m/s.

        If you need to pass in extra settings to the API, pass these into
        the `get_variables()` method as a dict object. These settings will
        be appended to the API request as query parameters.

        Parameters
        ----------
        request_settings : Union[None, dict]
            Dictionary object of extra settings to pass in as query parameters to
            the open-meteo Climate API. Latitude, longitude, start data, end date,
            timezone, daily weather variables, and windspeed units are set from the
            `Historical` object attributes. Find a list of settings here:
            https://open-meteo.com/en/docs/historical-weather-api
        """

        # hourly
        if self.hourly:
            if self.variables is None:
                self.variables = settings.hourly_historical_glm_default

            payload = {
                "longitude": self.location[0],
                "latitude": self.location[1],
                "start_date": self.date_range[0],
                "end_date": self.date_range[1],
                "hourly": (",").join(self.variables),
                "timezone": self.timezone,
                "windspeed_unit": "ms",
            }

            # if user has supplied extra query parameters, append them here.
            if request_settings:
                payload = {**payload, **request_settings}

            r = requests.get(self.historical_api_url, params=payload)
            r_json = r.json()
            df = pd.DataFrame(r_json.pop("hourly"))
            metadata = r_json
        # daily
        else:
            if self.variables is None:
                self.variables = settings.daily_historical_glm_default

            payload = {
                "longitude": self.location[0],
                "latitude": self.location[1],
                "start_date": self.date_range[0],
                "end_date": self.date_range[1],
                "daily": (",").join(self.variables),
                "timezone": self.timezone,
                "windspeed_unit": "ms",
            }

            # if user has supplied extra query parameters, append them here.
            if request_settings:
                payload = {**payload, **request_settings}

            r = requests.get(self.historical_api_url, params=payload)
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
        Convert hourly meteorological data to GLM format
        and store it in the `glm_met_data` attribute.

        This function only works with hourly data, this method expects the
        `met_data.data` attribute of the `Historical` object to have the
        following variables: `time`, `shortwave_radiation`, `cloudcover`,
        `temperature_2m`, `relativehumidity_2m`, `windspeed_10m` and
        `precipitation`.

        If the data in `met_data.data` has different
        variables, you will need to write your own function to convert the data
        to GLM format.

        `cloudcover` from openmeteo is in percentage units. GLM requires it as
        a proportion (0.0 to 1.0).

        `precipitation` is in mm. GLM requires it in m / day even if
        using hourly data, so it is converted.
        """

        if self.hourly:
            df_glm = pd.DataFrame(
                # glm requires time to have "hh:mm:ss" - append :00 to date-time string
                data={
                    "time": self.met_data.data["time"]
                    .str.replace("T", " ")
                    .astype(str)
                    + ":00",
                    "ShortWave": self.met_data.data["shortwave_radiation"],
                    "Cloud": self.met_data.data["cloudcover"] / 100,
                    "AirTemp": self.met_data.data["temperature_2m"],
                    "RelHum": self.met_data.data["relativehumidity_2m"],
                    "WindSpeed": self.met_data.data["windspeed_10m"],
                    "Rain": (self.met_data.data["precipitation"] / 1000) * 24,
                }
            )

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

        if self.hourly:
            glm_metadata = self.met_data.metadata.pop("hourly_units")

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
                    metadata_fpath = os.path.join(
                        tmpdir, "met_glm_metadata.json"
                    )

                    files = [data_fpath, metadata_fpath]

                    with zipfile.ZipFile(
                        os.path.join(path, "met_glm.zip"), mode="w"
                    ) as z_dst:
                        for file in files:
                            z_dst.write(file, arcname=file.split("/")[-1])
            else:
                self.glm_met_data.to_csv(
                    os.path.join(path, fname), index=False
                )

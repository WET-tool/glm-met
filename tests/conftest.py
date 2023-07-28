import pytest

@pytest.fixture
def valid_openmeteo_historical_init():
    init = {}
    init["longitude"] = 116.69115540712589
    init["latitude"] = -34.22581232495377
    init["date_range"] = ("2020-01-01", "2020-01-31")
    init["variables"] = [
                "temperature_2m",
                "relativehumidity_2m",
                "precipitation",
                "cloudcover",
                "et0_fao_evapotranspiration",
                "windspeed_10m",
                "winddirection_10m",
                "windgusts_10m",
                "shortwave_radiation",
                "direct_normal_irradiance"
            ]
    
    return init

@pytest.fixture
def valid_openmeteo_climate_init():
    init = {}
    init["longitude"] = 116.69115540712589
    init["latitude"] = -34.22581232495377
    init["date_range"] = ("2034-01-01", "2035-01-31")
    init["variables"] = [
                "shortwave_radiation_sum",
                "cloudcover_mean",
                "temperature_2m_mean",
                "relative_humidity_2m_mean",
                "windspeed_10m_mean",
                "precipitation_sum"
            ]
    
    return init
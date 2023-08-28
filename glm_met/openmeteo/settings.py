historical_api_url = "https://archive-api.open-meteo.com/v1/archive"

climate_api_url = "https://climate-api.open-meteo.com/v1/climate"

climate_models = [
    "CMCC_CM2_VHR4",
    "FGOALS_f3_H",
    "HiRAM_SIT_HR",
    "MRI_AGCM3_2_S",
    "EC_Earth3P_HR",
    "MPI_ESM1_2_XR",
    "NICAM16_8S",
]

climate_glm_default = [
    "shortwave_radiation_sum",
    "cloudcover_mean",
    "temperature_2m_mean",
    "temperature_2m_max",
    "temperature_2m_min",
    "relative_humidity_2m_mean",
    "windspeed_10m_mean",
    "precipitation_sum",
    "et0_fao_evapotranspiration_sum",
]

hourly_historical_glm_default = [
    "shortwave_radiation",
    "cloudcover",
    "temperature_2m",
    "relativehumidity_2m",
    "windspeed_10m",
    "precipitation",
]

daily_historical_glm_default = [
    "shortwave_radiation_sum",
    "temperature_2m_mean",
    "temperature_2m_max",
    "temperature_2m_min",
    "windspeed_10m_max",
    "precipitation_sum",
    "et0_fao_evapotranspiration",
]

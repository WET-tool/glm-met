nasa_power_api_url = "https://power.larc.nasa.gov/api/temporal/hourly/point"

# get parameter names from: https://power.larc.nasa.gov/#documentation
hourly_glm_default = [
    "ALLSKY_SFC_SW_DWN",  # W/m^2
    "CLOUD_AMT",  # %
    "T2M",  # degC
    "RH2M",  # %
    "WS2M",  # m/s
    "PRECTOTCORR",  # mm/hour
]

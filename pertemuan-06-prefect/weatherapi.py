import pandas as pd
import requests


def fetch_weatherapi_hourly(
    city: str = "Jakarta",
    date: str = "2026-07-17",
    api_key: str = "dff66563e0e2412a80414631261807",
) -> pd.DataFrame:
    url = "http://api.weatherapi.com/v1/history.json"
    params = {"key": api_key, "q": city, "dt": date}

    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()

    hours = data["forecast"]["forecastday"][0]["hour"]

    df = pd.DataFrame([
        {
            "time":             h["time"],
            "temp_c":           h["temp_c"],
            "feelslike_c":      h["feelslike_c"],
            "humidity":         h["humidity"],
            "pressure_mb":      h["pressure_mb"],
            "wind_kph":         h["wind_kph"],
            "wind_degree":      h["wind_degree"],
            "wind_dir":         h["wind_dir"],
            "cloud":            h["cloud"],
            "precip_mm":        h["precip_mm"],
            "vis_km":           h["vis_km"],
            "uv":               h["uv"],
            "is_day":           h["is_day"],
            "condition_text":   h["condition"]["text"],
            "condition_code":   h["condition"]["code"],
            "chance_of_rain":   h["chance_of_rain"],
            "will_it_rain":     h["will_it_rain"],
        }
        for h in hours
    ])

    df["time"] = pd.to_datetime(df["time"])
    return df


if __name__ == "__main__":
    df = fetch_weatherapi_hourly()
    print(f"Shape: {df.shape}")
    print(df.to_string())

import os
from datetime import datetime
from typing import Optional

from prefect import flow, task
from prefect.client.schemas.schedules import CronSchedule

from openmateo import fetch_weather_data
from weatherapi import fetch_weatherapi_hourly


# ── Task: Open-Meteo ──────────────────────────────────────────────────────────

@task
def task_fetch_openmateo(
    latitude: float = -6.5944,
    longitude: float = 106.7892,
) -> dict:
    df = fetch_weather_data(latitude=latitude, longitude=longitude)
    print(f"[open-meteo] Fetched {len(df)} rows")
    print(df)
    return {"rows": len(df), "columns": list(df.columns)}


# ── Task: WeatherAPI ──────────────────────────────────────────────────────────

@task
def task_fetch_weatherapi(
    city: str = "Jakarta",
    date: Optional[str] = None,
) -> dict:
    if date is None:
        date = datetime.today().strftime("%Y-%m-%d")
    df = fetch_weatherapi_hourly(city=city, date=date)
    print(f"[weatherapi] Fetched {len(df)} rows for {city} on {date}")
    print(df.to_string())
    return {"rows": len(df), "columns": list(df.columns), "city": city, "date": date}


# ── Flow: Open-Meteo ──────────────────────────────────────────────────────────

@flow(name="openmeteo-pipeline", log_prints=True)
def openmeteo_pipeline():
    result = task_fetch_openmateo()
    print(f"Pipeline complete: {result}")


# ── Flow: WeatherAPI ──────────────────────────────────────────────────────────

@flow(name="weatherapi-pipeline", log_prints=True)
def weatherapi_pipeline(city: str = "Jakarta", date: Optional[str] = None):
    result = task_fetch_weatherapi(city=city, date=date)
    print(f"Pipeline complete: {result}")


# ── Deploy ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    SOURCE = "/home/ffkhr/Documents/nusacode-de-beginner/pertemuan-06-prefect"
    POOL   = "default-agent-pool"
    SCHEDULE = [CronSchedule(cron="*/2 * * * *", timezone="Asia/Jakarta")]

    openmeteo_pipeline.from_source(
        source=SOURCE,
        entrypoint="weather_pipeline.py:openmeteo_pipeline",
    ).deploy(
        name="weather-open-meteo",
        work_pool_name=POOL,
        schedules=SCHEDULE,
    )

    weatherapi_pipeline.from_source(
        source=SOURCE,
        entrypoint="weather_pipeline.py:weatherapi_pipeline",
    ).deploy(
        name="weather-weatherapi",
        work_pool_name=POOL,
        schedules=SCHEDULE,
    )


# # 1. Definisikan deployment untuk OpenMeteo (tanpa langsung memanggil .deploy())
#     openmeteo_dep = openmeteo_pipeline.from_source(
#         source=SOURCE,
#         entrypoint="weather_pipeline.py:openmeteo_pipeline",
#     ).to_deployment(
#         name="weather-open-meteo",
#         schedules=SCHEDULE,
#     )

#     # 2. Definisikan deployment untuk WeatherAPI
#     weatherapi_dep = weatherapi_pipeline.from_source(
#         source=SOURCE,
#         entrypoint="weather_pipeline.py:weatherapi_pipeline",
#     ).to_deployment(
#         name="weather-weatherapi",
#         schedules=SCHEDULE,
#     )

#     # 3. Jalankan deploy sekaligus untuk kedua objek deployment di atas
#     print("Deploying both pipelines to Prefect...")
#     deploy(
#         openmeteo_dep,
#         weatherapi_dep,
#         work_pool_name=POOL,
#     )
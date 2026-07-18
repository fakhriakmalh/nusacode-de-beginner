import os
import subprocess
from datetime import datetime
from typing import Optional

from prefect import flow, task
from prefect.client.schemas.schedules import CronSchedule

from openmateo import fetch_weather_data
from weatherapi import fetch_weatherapi_hourly

DBT_PROJECT_DIR = "/home/ffkhr/Documents/nusacode-de-beginner/pertemuan-05-06-dbt"
DBT_PROFILES_DIR = DBT_PROJECT_DIR
DBT_BIN = "/home/ffkhr/my_env/bin/dbt"

DBT_ENV = {
    **os.environ,
    "DBT_HOST":            "localhost",
    "DBT_PORT":            "8123",
    "DBT_USER":            "clickhousedev",
    "DBT_PASSWORD":        "adminpass123",
    "DBT_SCHEMA":          "nusacode_db",
    "DBT_SECURE":          "false",
    "DBT_THREADS":         "4",
    "DBT_CONNECT_TIMEOUT": "10",
}


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


# ── Task: dbt ────────────────────────────────────────────────────────────────

@task
def task_dbt_run(selector: str) -> dict:
    cmd = [
        DBT_BIN, "run",
        "--select", selector,
        "--project-dir", DBT_PROJECT_DIR,
        "--profiles-dir", DBT_PROFILES_DIR,
    ]
    print(f"[dbt] Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, env=DBT_ENV)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        raise RuntimeError(f"dbt run --select {selector} failed:\n{result.stderr}")
    return {"selector": selector, "returncode": result.returncode}


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


# ── Flow: dbt Silver → Gold (sequential) ─────────────────────────────────────

@flow(name="dbt-pipeline", log_prints=True)
def dbt_pipeline():
    silver = task_dbt_run(selector="silver")
    print(f"dbt silver complete: {silver}")
    gold = task_dbt_run(selector="gold")
    print(f"dbt gold complete: {gold}")


# ── Deploy ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    SOURCE   = "/home/ffkhr/Documents/nusacode-de-beginner/pertemuan-06-prefect"
    POOL     = "default-agent-pool"
    SCHEDULE = [CronSchedule(cron="*/10 * * * *", timezone="Asia/Jakarta")]

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

    dbt_pipeline.from_source(
        source=SOURCE,
        entrypoint="weather_pipeline.py:dbt_pipeline",
    ).deploy(
        name="dbt-silver-gold",
        work_pool_name=POOL,
        schedules=SCHEDULE,
    )

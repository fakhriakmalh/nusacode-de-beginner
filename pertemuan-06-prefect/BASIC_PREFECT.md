# Prefect — Basic Concepts & Syntax

## Apa itu Prefect?

Prefect adalah framework orchestration untuk data pipeline. Digunakan untuk mendefinisikan, menjadwalkan, dan memonitor workflow sebagai kode (Python).

## Instalasi

```bash
pip install prefect
```

## Core Concepts

### Task

Unit kerja terkecil dalam pipeline. Sebuah fungsi Python yang didekorasi `@task`.

### Flow

Orchestrator yang mengatur urutan dan dependensi antar task. Sebuah fungsi Python yang didekorasi `@flow`.

---

## Basic Syntax

### 1. Task Sederhana

```python
from prefect import task

@task
def extract_data():
    return [1, 2, 3, 4, 5]
```

### 2. Flow Sederhana

```python
from prefect import flow

@flow
def my_pipeline():
    data = extract_data()
    print(data)
```

### 3. Task dengan Parameter

```python
@task
def transform_data(data: list, multiplier: int = 2) -> list:
    return [x * multiplier for x in data]
```

### 4. Flow dengan Multiple Task & Dependensi

```python
@task
def load_data(data: list) -> dict:
    return {"count": len(data), "total": sum(data)}

@flow
def etl_pipeline():
    raw = extract_data()
    transformed = transform_data(raw, multiplier=3)
    result = load_data(transformed)
    return result
```

### 5. Menjalankan Flow

```python
if __name__ == "__main__":
    etl_pipeline()
```

```bash
python my_pipeline.py
```

### 6. Menambahkan Schedule (Interval / Cron)

Gunakan `serve()` di blok `__main__` untuk menjalankan flow secara periodik:

```python
from datetime import timedelta
from prefect import flow, task

@task
def my_task():
    print("Working...")

@flow(log_prints=True)
def my_pipeline():
    my_task()

if __name__ == "__main__":
    my_pipeline.serve(
        name="my-hourly-pipeline",
        interval=timedelta(hours=1),   # tiap 1 jam
        # cron="0 * * * *",            # alternatif pakai cron
    )
```

### 7. Caching Task Result

```python
@task(cache_key_fn=lambda *args, **kwargs: "static_key")
def expensive_computation():
    return 42
```

Hasil task akan di-cache selama jangka waktu tertentu (default task run tidak diulang dengan input yang sama).

---

## Contoh Lengkap (dari project ini)

```python
from prefect import flow, task
from openmateo import fetch_weather_data


@task
def fetch_openmateo_data(latitude: float = -6.5944, longitude: float = 106.7892) -> dict:
    df = fetch_weather_data(latitude=latitude, longitude=longitude)
    return {"rows": len(df), "columns": list(df.columns)}


@flow
def weather_pipeline():
    result = fetch_openmateo_data()
    print(f"Pipeline complete: {result}")


if __name__ == "__main__":
    weather_pipeline()
```

---

## Deployment & Prefect Server (Agar Ada UI seperti Airflow)

### Kenapa `serve()` Tidak Punya Tombol Run?

`serve()` hanyalah Python process biasa — tidak ada web UI, tidak ada database, tidak ada tombol "Run".

Agar bisa trigger job dari UI (seperti Airflow), Prefect butuh:

| Komponen | Fungsi | Analogi Airflow |
|---|---|---|
| **Prefect Server** | Web UI + API + database scheduler | Webserver + Scheduler |
| **Deployment** | Registrasi flow + schedule ke server | DAG on/off toggle |
| **Work Pool / Worker** | Menjalankan flow deployment | Celery Executor |

---

### 1. Start Prefect Server (UI + API)

```bash
# Terminal 1 — jalankan server
prefect server start
```

UI akan terbuka di **http://127.0.0.1:4200**. Di sini kamu bisa melihat Flow Runs, Deployment, Work Queue, dan tombol **"Run"** untuk trigger manual.

---

### 2. Buat Deployment

Ada dua cara:

#### A. Via `.deploy()` di code (recommended)

```python
from prefect import flow, task
from datetime import timedelta

@task
def my_task():
    print("Working...")

@flow(log_prints=True)
def my_pipeline():
    my_task()

if __name__ == "__main__":
    my_pipeline.deploy(
        name="my-deployment",
        work_pool_name="default-agent-pool",
        schedule=None,                              # triger manual saja
        # interval=timedelta(hours=1),              # atau pakai schedule
        # cron="0 * * * *",
    )
```

Kemudian jalankan:

```bash
python my_pipeline.py          # mendaftarkan deployment ke server
```

Setelah terdaftar, flow akan muncul di UI Prefect → tab **Deployments** → bisa di-trigger manual via tombol **"Run"**.

#### B. Via CLI (`prefect deploy`)

```bash
prefect deploy --name weather-pipeline --interval 3600
```

---

### 3. Jalankan Worker (Agar Deployment Dieksekusi)

```bash
# Terminal 2
prefect worker start --pool "default-agent-pool"
```

Worker akan mengambil task dari work queue dan menjalankannya.

---

### 4. Trigger dari UI

1. Buka http://127.0.0.1:4200
2. Klik tab **Deployments**
3. Klik nama deployment (misal `weather-pipeline/my-deployment`)
4. Klik tombol **▶ Run** → **Custom Run** → **Run**

---

### 5. Quick Start (Prefect Server + Worker + Deploy)

```bash
# Terminal 1 — Server
prefect server start

# Terminal 2 — Worker
prefect worker start --pool "default-agent-pool"

# Terminal 3 — Daftarkan deployment
python weather_pipeline.py
```

Setelah itu buka UI http://127.0.0.1:4200 → **Deployments** → klik **▶ Run**.

---

## Perbandingan Airflow vs Prefect

| Fitur | Airflow | Prefect |
|---|---|---|
| Web UI | `airflow webserver` | `prefect server start` |
| Scheduler | `airflow scheduler` | Built-in di server |
| Executor / Worker | Celery, Kubernetes | Work Pool + Worker |
| Trigger manual via UI | DAG → Trigger DAG | Deployment → Run |
| Syntax | Python DAG file | Python `@flow` / `@task` |
| Schedule | cron di DAG args | `interval=`, `cron=`, atau `schedule=` |

---

## Referensi

- [Prefect Docs](https://docs.prefect.io/v3/)
- [Prefect Deployments](https://docs.prefect.io/v3/deploy/)
- [Prefect Server](https://docs.prefect.io/v3/server/)
- [Prefect Tasks & Flows](https://docs.prefect.io/v3/develop/write-tasks/)

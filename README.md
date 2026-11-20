# Bookstore & Warehouse Microservice Platform (`ProjectA` + `ProjectB`)

Вебдодаток "Книжковий магазин" на базі **Django**, **Django REST Framework**, **PostgreSQL**, **Redis**, **Celery**, **Docker Compose**, **NGINX** та **pytest**, інтегрований із мікросервісом складу (`warehouse_service`).

[![Django CI/CD](https://github.com/snitkazhenya-a11y/bookstore/actions/workflows/django.yml/badge.svg)](https://github.com/snitkazhenya-a11y/bookstore/actions/workflows/django.yml)
[![codecov](https://codecov.io/gh/snitkazhenya-a11y/bookstore/branch/main/graph/badge.svg)](https://codecov.io/gh/snitkazhenya-a11y/bookstore)

---

## Архітектура системи

```mermaid
flowchart LR
    Client["Клієнт / Браузер / API споживач"] --> Nginx["NGINX (:80)"]

    subgraph ProjectA["ProjectA — bookstore (:8000)"]
        WebA["Gunicorn / Django + DRF + JWT"]
        CeleryW["Celery Worker"]
        CeleryB["Celery Beat"]
        DbA[("PostgreSQL (db_a)")]
        RedisA[("Redis (redis_a)")]
        WebA --> DbA
        WebA <--> RedisA
        CeleryW --> DbA
        CeleryW <--> RedisA
        CeleryB --> RedisA
    end

    subgraph ProjectB["ProjectB — warehouse_service (:8001)"]
        WebB["Gunicorn / Django + DRF + JWT"]
        DbB[("PostgreSQL (db_b)")]
        WebB --> DbB
    end

    Nginx --> WebA
    Nginx --> WebB
    WebA -- "HTTP резервування залишків\n(/api/warehouse/stock/.../reserve/)" --> WebB
    WebA -. "Помилки та трейси" .-> Sentry["Sentry"]
    WebB -. "Помилки та трейси" .-> Sentry
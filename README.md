# ShopKart Data Platform on Databricks

An end-to-end e-commerce data pipeline built on **Databricks Free Edition** with **PySpark**, **Spark SQL** and **Delta Lake**, using the **medallion architecture** (Bronze → Silver → Gold).

The project is run like a real data team: every piece of work is a Jira ticket with a business request, acceptance criteria and review.

## Architecture

```
 Source files (CSV / JSON)
        │  Auto Loader, COPY INTO
        ▼
 BRONZE   raw data as received, plus audit columns (_ingested_at, _source_file)
        │  dedup, type casting, joins, quarantine of bad rows, MERGE, SCD2
        ▼
 SILVER   clean, conformed, trusted entities (orders, order_lines, dim_customers, events)
        │  aggregations, window functions
        ▼
 GOLD     business-ready tables  →  AI/BI dashboard
```

Orchestrated with Lakeflow Jobs; deployed with Databricks Asset Bundles; tested with pytest in GitHub Actions.

## Data

Synthetic data with the same schema as the public Olist Brazilian E-Commerce dataset: 20,000 orders, 19,412 customers, 2,800 products and about 77,000 clickstream events. Data files are **not** stored in this repo. Rebuild them with the scripts in [`data_generators/`](data_generators/):

```bash
python data_generators/gen_shopkart.py   # orders, customers, products, ... + incremental files
python data_generators/gen_events.py     # clickstream JSON (run after gen_shopkart.py)
```

See [`data_generators/README.md`](data_generators/README.md) for the data dictionary and the deliberate data-quality issues.

## Repository layout

| Path | Contents |
|---|---|
| `notebooks/` | Databricks notebooks, numbered by layer and run order |
| `src/shopkart/` | Reusable transformation functions (added in SK-21) |
| `tests/` | pytest unit tests (added in SK-21) |
| `resources/`, `databricks.yml` | Job definitions as code (added in SK-22) |
| `.github/workflows/` | CI/CD pipeline (added in SK-22) |
| `data_generators/` | Scripts that generate the dataset |
| `docs/` | Screenshots, incident reports, design notes |

## Progress

| Phase | Tickets | Status |
|---|---|---|
| 1. Platform setup & ingestion (Bronze) | SK-01 – SK-03 | ⏳ |
| 2. Data cleansing (Silver) | SK-04 – SK-06 | ⏳ |
| 3. Business analytics (Gold) | SK-07 – SK-09 | ⏳ |
| 4. Production readiness | SK-10 – SK-14 | ⏳ |
| 5. Performance & optimization | SK-15 | ⏳ |
| 6. Advanced topics | SK-16 – SK-22 | ⏳ |

## Skills demonstrated

Unity Catalog · Delta Lake · PySpark DataFrames · Spark SQL · window functions · MERGE / upserts · SCD Type 2 · time travel · Auto Loader · Structured Streaming with watermarks · nested JSON · data quality & quarantine · Lakeflow Jobs · Lakeflow Declarative Pipelines · query tuning · row filters & column masks · secrets · pytest · Asset Bundles · GitHub Actions

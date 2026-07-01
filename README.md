markdown
#  Real‑Time E‑Commerce Data Platform

**End‑to‑end analytics pipeline for an online marketplace — built with Azure, Databricks, and Power BI.**

---

##  Business Scenario

An online marketplace needs a scalable analytics platform that processes **orders, customers, products, payments, reviews, and live clickstream events** to deliver real‑time business insights.

---

##  Architecture
[Python Data Generators]
│
▼
Azure Data Lake Gen2 ─── Bronze (raw JSON)
│
▼
Azure Databricks (Auto Loader)
│
├── Silver Layer (cleaned Delta tables)
│
▼
Databricks Batch Job (every 2 min)
│
▼
Gold Layer (Star Schema – managed Delta tables)
│
▼
Power BI (DirectQuery, auto‑refresh every 5s)

text

**Data flows:**
- **Historical data** (customers, products, orders, payments, reviews) loaded once.
- **Streaming clickstream** generated continuously by a local Python producer.
- Auto Loader ingests both into Silver Delta tables.
- A scheduled Databricks notebook rebuilds the Gold star schema every 2 minutes.
- Power BI queries the Gold layer via Databricks SQL Warehouse using DirectQuery and page refresh for real‑time dashboards.

---

##  Tech Stack

| Category               | Tools & Services                                           |
|------------------------|------------------------------------------------------------|
| Cloud Storage          | Azure Data Lake Storage Gen2                               |
| Data Ingestion         | Databricks Auto Loader (cloudFiles), Python producers       |
| Processing & ETL       | Azure Databricks, PySpark, Spark SQL                       |
| Lakehouse Format       | Delta Lake (ACID, time travel)                             |
| Data Modeling          | Star Schema (SCD Type 1)                                   |
| Governance (optional)  | Unity Catalog (Premium) / Hive Metastore (Standard)        |
| Visualization          | Power BI Desktop (DirectQuery)                             |
| Orchestration          | Databricks Workflows (scheduled job)                       |

---

##  Project Structure

ecom-realtime-platform/
├── README.md
├── architecture.png
├── notebooks/
│ ├── 00_configure_storage.py
│ ├── 01_bronze_to_silver_historical.py
│ ├── 02_streaming_clickstream.py
│ └── 03_silver_to_gold_managed.py
├── data-generators/
│ ├── historical_data_loader.py
│ └── streaming_producer.py
├── powerbi/
  └── ecom_dashboard.pbix

---

### Dashboard
<img width="3005" height="1145" alt="ecommerce_data_platform" src="https://github.com/user-attachments/assets/d90c78f3-cda9-4548-9365-f9187b7afcf2" />

##  Setup & Run (Free Azure Subscription)

### 1. Azure Resources
- Resource group `rg-ecom-platform`
- ADLS Gen2 (`ecomdatalakegen2`) with containers `bronze`, `silver`, `gold`
- Azure Databricks workspace (`dbw-ecom`), **Standard tier**
- **Single User cluster** (Single Node, 13.3 LTS or 14.3 LTS)

### 2. Secrets
- Store storage account key in Databricks Secrets scope `azure` → key `storage-key`

### 3. Data Generators
```bash
pip install azure-storage-file-datalake faker
python data-generators/historical_data_loader.py   # once
python data-generators/streaming_producer.py       # keep running
4. Databricks Notebooks (run in order)
00_configure_storage – sets spark.conf with the storage key

01_bronze_to_silver_historical – Auto Loader ingests historical files into Silver Delta

02_streaming_clickstream – Auto Loader for continuous clickstream events

03_silver_to_gold_managed – builds Gold star schema as managed tables

5. Schedule Gold Refresh
Databricks Job → Notebook 03 → every 2 minutes

6. Power BI
Start Databricks SQL Warehouse (2X‑Small)

Connect Power BI via Azure Databricks connector (DirectQuery)

Build real‑time dashboard with auto‑page refresh every 5 seconds

### Dashboard Highlights
Live Event Counter (card) – total clickstream events

Events per Minute (line chart) – real‑time trend

Conversion Rate (gauge) – purchases / total events

Top Products by Clicks (table)

Revenue KPI (card) – from historical orders

Slicers – date, event type, payment method (cross‑filtering via star schema)

### Key Learnings & Challenges
Bronze → Silver → Gold architecture ensures data quality and query performance.

Auto Loader gracefully handles both batch and streaming sources with schema inference.

DirectQuery + page refresh eliminates the need for streaming datasets in Power BI.

Standard tier vs. Premium/Unity Catalog – adapted from mount‑based access to direct ABFSS and managed tables.

Incremental checkpointing prevents re‑processing and enables exactly‑once semantics.

Scheduling the Gold refresh is essential; otherwise dashboards show stale data.

### Demo
[TBD]

**License**

MIT – feel free to use and modify for your own learning or portfolio.

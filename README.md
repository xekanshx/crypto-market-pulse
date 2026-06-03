# Crypto Market Analytics & ETL Platform

Crypto analytics platform built using **Python, PostgreSQL, Apache Superset, SQL, and Docker** for automated cryptocurrency data ingestion, historical backfilling, statistical analysis, and interactive dashboard visualization.

The project fetches historical and daily cryptocurrency market data from the CoinGecko API, stores it in PostgreSQL, and powers a fully interactive Apache Superset dashboard featuring rolling trend analysis, volatility analytics, market dominance tracking, anomaly detection, and performance comparisons.

<img width="1771" height="980" alt="image" src="https://github.com/user-attachments/assets/531fcb20-c55c-4f0d-858d-003f1d93b119" />



---

# Project Overview

This project simulates a real-world analytics and BI workflow involving:

* Automated API ingestion
* Historical backfill pipelines
* Scheduled ETL jobs
* PostgreSQL data warehousing
* SQL-based analytical transformations
* Statistical analysis
* Interactive dashboarding
* Dockerized deployment architecture

The dashboard provides insights into:

* Cryptocurrency price trends
* Market volatility
* Trading volume behavior
* Market cap dominance
* Volume spike anomalies
* Top gainers and losers
* Historical performance windows

---

# Tech Stack

| Component            | Technology              |
| -------------------- | ----------------------- |
| Programming Language | Python                  |
| Database             | PostgreSQL              |
| Dashboarding         | Apache Superset         |
| Containerization     | Docker & Docker Compose |
| Data Source          | CoinGecko API           |
| Querying             | SQL                     |
| Scheduling           | APScheduler             |
| Data Processing      | Pandas                  |

---

# System Architecture

(will paste architecture diagram here)

Example Flow:

CoinGecko API
↓
Historical Backfill Pipeline
↓
Daily Automated ETL Pipeline
↓
PostgreSQL Database
↓
SQL Analytics Layer
↓
Apache Superset Dashboard

---

# Containerized Architecture

The project uses a multi-container Docker architecture:

* PostgreSQL container for persistent storage
* Apache Superset container for dashboarding and visualization
* Python ETL container for automated data ingestion
* Docker Compose for orchestration and service management

---

# Key Features

## Historical Data Backfill Pipeline

* Fetches 1 year of historical cryptocurrency market data
* Uses CoinGecko Market Chart API
* Prevents duplicate inserts using conflict handling
* Safe to rerun incrementally
* Handles CoinGecko API rate limiting gracefully

---

## Automated Daily ETL Pipeline

* Scheduled ingestion using APScheduler
* Automated daily cryptocurrency market updates
* Retry handling for transient API failures
* Batch database inserts using PostgreSQL execute_values
* UPSERT-based incremental updates
* Environment-variable driven configuration

---

## Rolling Price Trend Analysis

* 30-day rolling average price analysis
* Normalized cross-asset comparison
* Time-series smoothing for trend visualization

<img width="1106" height="746" alt="image" src="https://github.com/user-attachments/assets/de5b424a-e508-44ca-a6a7-e22d29532cb4" />

Insights:
- Bitcoin and Ethereum showed comparatively stable long-term price movement relative to smaller-cap assets.
- Solana demonstrated higher momentum swings, indicating increased short-term volatility.
- Normalized rolling averages helped compare cross-asset trends despite large price-scale differences.
---

## Trading Volume Spike Detection

* Detects abnormal volume spikes
* Compares current volume against rolling 30-day baselines
* Identifies unusual market activity patterns

<img width="1104" height="748" alt="image" src="https://github.com/user-attachments/assets/41c18639-2a3b-4862-8674-821b986028c8" />

Insights:
- Several mid-cap assets experienced trading volume spikes exceeding 10× their historical baseline.
- High spike ratios suggest periods of speculative activity and sudden liquidity inflows.
- Rolling volume baselines helped identify abnormal market participation patterns.
---

## Volatility Analytics

* Calculates relative price volatility using statistical measures
* Uses coefficient of variation for normalized cross-asset comparison

<img width="1093" height="761" alt="image" src="https://github.com/user-attachments/assets/d05c2c67-d79c-46b4-a815-3636309d9d10" />

Insights:
- Smaller-cap cryptocurrencies exhibited significantly higher relative volatility than large-cap assets.
- Bitcoin and Ethereum maintained comparatively lower volatility percentages over the 90-day window.
- Stablecoins were excluded to avoid distortion in comparative volatility analysis.
---

## Market Dominance Analysis

* Tracks market cap dominance trends over time
* Compares relative market share across major cryptocurrencies

<img width="1101" height="741" alt="image" src="https://github.com/user-attachments/assets/4bbfbf17-db23-4b30-b97a-d7f0d38e8dc1" />

Insights:
- Bitcoin maintained relatively stable market dominance throughout the observed period.
- Solana and Binance Coin showed noticeable fluctuations in relative market share.
- Dominance trends reflected changing investor concentration across major crypto assets.
---

## Gainers vs Losers Analysis

* Calculates 7-day and 30-day returns
* Identifies strongest and weakest performing assets

<img width="1092" height="491" alt="image" src="https://github.com/user-attachments/assets/6cf20d73-7bd9-4907-813f-10106190800b" />

Insights:
- Short-term returns varied significantly across assets, highlighting the highly dynamic nature of crypto markets.
- Several assets showed strong weekly momentum but weaker monthly performance, indicating short-lived rallies.
- Comparative return analysis helped identify both sustained and temporary market movements.
---

## Historical Performance Window Analysis

* Detects best and worst 7-day performance windows
* Uses SQL window functions and ranking operations

<img width="1119" height="771" alt="image" src="https://github.com/user-attachments/assets/abe3e75a-c5b2-496e-a6b8-a9039dab8b69" />

Insights:
- Some assets experienced extreme short-term price swings exceeding 300% within 7-day windows.
- High variance in performance windows reflects speculative behavior and rapid sentiment shifts in crypto markets.
- Window-based analysis highlighted historical periods of exceptional momentum and drawdowns.
---

# SQL Concepts Used

This project heavily utilizes advanced SQL concepts including:

* Common Table Expressions (CTEs)
* Window Functions
* LEAD() and LAG()
* Rolling Averages
* Ranking Functions
* Statistical Aggregations
* Time-Series Analysis
* Percentage Change Calculations
* Normalization Techniques
* Partitioned Analytics

---

# Example Analytical Queries

Implemented analytical workflows include:

* Normalized rolling price trends
* Volume anomaly detection
* Volatility percentage calculations
* Market dominance tracking
* Historical performance window detection
* Top gainers vs losers analysis

All SQL queries are available inside the `SQL-queries/` directory.

---

# Folder Structure

```bash
.
├── SQL-queries/
├── data_fetcher/
│   ├── Dockerfile
│   ├── backfill.py
│   ├── fetcher.py
│   └── requirements.txt
├── dashboard_screenshots/
├── docker-compose.yml
├── .env.example
├── README.md
└── .gitignore
```

---

# Running the Project

## Clone Repository

```bash
git clone <your-repo-url>
cd <repo-name>
```

---

## Configure Environment Variables

Create a `.env` file:

```env
POSTGRES_USER=crypto_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=crypto_data
SUPERSET_SECRET_KEY=your_secret_key
```

---

## Start Docker Containers

```bash
docker compose up --build
```

---

## Run Historical Backfill

```bash
docker exec -it crypto_fetcher python backfill.py
```

---

## Access Apache Superset

```bash
http://localhost:8088
```

---

# Dashboard Preview

(paste full dashboard screenshot here)

---

# Learning Outcomes

Through this project, I gained hands-on experience with:

* End-to-end analytics pipeline development
* Dockerized deployment workflows
* PostgreSQL-based analytical storage
* Advanced SQL analytics
* API integration and ETL automation
* Business intelligence dashboarding
* Statistical and time-series analysis
* Data visualization best practices

---

# Future Improvements

* Real-time crypto streaming support
* Airflow-based orchestration
* Public cloud deployment
* Predictive analytics integration
* Automated alerting systems
* Additional technical indicators

---

# Disclaimer

This project is intended for educational and analytical purposes only and does not provide financial advice.

# Microsoft Fabric Pipeline Extension

This document explains how the Behavioral Health Risk-to-Treatment Alignment dashboard was extended into a Microsoft Fabric data pipeline.

The purpose of this pipeline is to turn raw behavioral health admissions data into trusted, reusable, dashboard-ready KPI tables.

```text
Raw CSV in Lakehouse Files
-> Bronze Delta table
-> Silver cleaned admissions table
-> Gold KPI and aggregate tables
-> Power BI dashboard
```

---

## Business Purpose

Behavioral health teams need a repeatable way to monitor whether higher-risk admissions are being routed to care pathways that match their operational risk profile.

A one-time dashboard can identify the issue, but a pipeline makes the analysis repeatable, auditable, and easier to refresh when new admissions data becomes available.

This pipeline supports three operational monitoring questions:

1. How many admissions are classified as high risk?
2. Are high-risk admissions routed to low-, medium-, or high-intensity care?
3. What share of high-risk admissions experience delayed admission exposure?

---

## Fabric Architecture

| Layer | Fabric Component | Purpose |
|---|---|---|
| Raw | Lakehouse Files | Stores the original SAMHSA TEDS-A CSV file |
| Bronze | Delta table | Preserves the raw admissions data as a managed table |
| Silver | Spark Notebook | Cleans coded fields and creates business-readable features |
| Gold | Delta tables | Produces dashboard-ready KPI and aggregate tables |
| Orchestration | Fabric Data Pipeline | Runs the notebook to refresh the full data workflow |
| Reporting | Power BI | Visualizes treatment alignment and operational risk KPIs |

---

## Pipeline Output Tables

| Table | Purpose |
|---|---|
| `bronze_tedsa_admissions_2023` | Raw admissions data stored as a Delta table |
| `silver_tedsa_admissions_cleaned` | Cleaned admissions data with risk, wait-time, and treatment intensity fields |
| `gold_kpi_summary` | Core KPI table for dashboard-level metrics |
| `gold_risk_treatment_matrix` | Admissions by risk profile and treatment intensity |
| `gold_treatment_distribution` | Admissions by treatment category and intensity |
| `gold_wait_time_by_risk` | Wait-time distribution by risk profile |

---

## Spark Transformation Logic

The Spark notebook creates the Silver layer by translating coded administrative fields into business-readable analytical fields.

Key transformations include:

- Mapping `PSYPROB` into co-occurring mental health status
- Mapping `EMPLOY` into employment status
- Mapping `DAYWAIT` into wait-time tiers
- Creating `Risk_Profile`
- Creating `Treatment_Intensity`
- Generating Gold KPI tables for dashboard consumption

---

## Pipeline Validation

The Gold KPI output was validated against the dashboard-level metrics.

| KPI | Value |
|---|---:|
| Total Admissions | 1,625,833 |
| High-Risk Admissions | 412,766 |
| High Risk Rate | 25.39% |
| High-Risk Low-Intensity Admissions | 186,385 |
| Treatment Mismatch Rate | 45.16% |
| High-Risk Alignment Rate | 54.84% |
| High-Risk Delayed Admission Rate | 7.06% |

---

## Orchestration Result

The Fabric Data Pipeline successfully ran the Spark notebook and rebuilt the Bronze, Silver, and Gold tables.

The first full orchestration run completed successfully on Fabric F2 capacity. The notebook was then optimized by removing interactive preview steps and reducing repeated full-table scans for scheduled pipeline execution.

---

## Why This Matters

This extension turns the project from a static dashboard into a repeatable analytics workflow.

It demonstrates the ability to:

- Ingest raw data into a Lakehouse
- Build Bronze, Silver, and Gold data layers
- Use Spark for data transformation
- Create reusable KPI tables
- Orchestrate refresh logic with Fabric Data Pipeline
- Connect curated data outputs to business reporting

This pipeline establishes a reusable analytics lifecycle that moves raw admissions data into governed KPI tables, making the output available for dashboarding, operational monitoring, and future integration with additional healthcare datasets.


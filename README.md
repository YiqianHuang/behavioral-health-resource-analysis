# Behavioral Health Resource Allocation Analysis

### Investigating treatment access patterns and operationalizing findings with Microsoft Fabric and Power BI

---

## Overview

This project investigates whether admissions with higher operational risk are being routed to treatment intensity levels that may warrant additional review.

The project began with a high-risk low-intensity placement signal: a meaningful share of admissions classified as high risk were routed to low-intensity treatment. I then explored observable access-context variables, including age, wait time, state, and employment status, to understand where that pattern was most concentrated.

Employment status emerged as the clearest segmentation finding. Among admissions with co-occurring mental health needs, employed patients, especially part-time employed patients, had the highest low-intensity placement rates.

I then extended the analysis into a reusable Microsoft Fabric data product that converts public SAMHSA admissions and facility data into curated Gold tables, a Power BI dashboard, semantic model inputs, and SQL views for downstream analysis.

The analysis is descriptive, not causal. It identifies patterns that may warrant operational review, but it does not determine why those patterns occur.

---

## Architecture

```text
Raw public datasets
  |-- TEDS-A admissions CSV
  |-- N-SUMHSS facility CSV
        |
        v
Bronze Delta tables
        |
        v
Silver cleaned analytical tables
        |
        v
Gold KPI and aggregate tables
        |
        |-- Power BI dashboard
        |-- Fabric semantic model
        |-- SQL Analytics Endpoint views
```

![Pipeline Canvas](fabric-pipeline/images/pipeline-canvas.png)

The canvas above shows the orchestrated Fabric pipeline. The downstream serving layers are documented in the detailed Fabric pipeline write-up.

### Project Scale

| Component | Scale |
|---|---:|
| TEDS-A admissions processed | 1,625,833 |
| Statistical validation sample | 538,172 |
| Public datasets integrated | 2 |
| Pipeline activities | 4 |
| Serving layers | 3 |

---

## Dashboard

The Power BI dashboard examines treatment intensity among admissions with co-occurring mental health needs and compares low-intensity placement rates by employment status.

![Treatment Access Friction by Employment Status](dashboards/images/employment-low-intensity-placement-by-status.png)

The dashboard insight was then validated through a statistical notebook and operationalized through Microsoft Fabric Gold outputs.

Detailed validation: [Statistical Validation](docs/statistical-validation.md)

---

## Core Metric Definitions

The initial monitoring signal is the **High-Risk Low-Intensity Placement Rate**:

```text
High-Risk Low-Intensity Placement Rate =
High-risk admissions routed to low-intensity treatment
/ All high-risk admissions
```

In this project, `High Risk` is an operational risk segment defined in the Silver admissions table as admissions with a co-occurring mental health condition (`PSYPROB = 1`) and an employment status of unemployed or not in the labor force. Low-intensity treatment is an analytical grouping based on the TEDS-A service setting code.

The employment analysis uses the **Employment-Based Low-Intensity Placement Rate**:

```text
Employment-Based Low-Intensity Placement Rate =
Co-occurring mental health admissions routed to low-intensity treatment
/ All co-occurring mental health admissions in the same employment group
```

Both metrics are review signals. They do not mean low-intensity care was clinically inappropriate for every admission.

---

## Key Finding

Among admissions with a co-occurring mental health condition (`PSYPROB = 1`), the employment-based low-intensity placement rate was highest for employed patients.

| Employment Status | Low-Intensity Placement Rate |
|---|---:|
| Part-time employed | 68.7% |
| Full-time employed | 65.5% |
| Not in labor force | 48.7% |
| Unemployed | 42.0% |

Statistical validation supported the dashboard finding:

- Chi-square testing found a statistically significant association between employment status and low-intensity placement.
- Logistic regression showed the association remained after adjusting for age, sex, race, state, and wait-time category.
- Sensitivity checks showed the pattern was not isolated to one age group, wait-time category, or small set of states.

This supports employment status as a meaningful access-context variable for operational monitoring. It does not prove that employment causes low-intensity placement.

---

## Additional Resource Planning View

The project also includes a state-level resource priority framework that compares high-risk admission burden with listed behavioral health treatment facility availability.

![State Resource Priority Quadrant](resource-priority/images/state-resource-priority-quadrant.png)

This framework is intended for high-level resource review, not as proof of unmet need at the facility level.

---

## Tools

| Tool | Purpose |
|---|---|
| Microsoft Fabric Lakehouse | Store raw, cleaned, and curated Delta tables |
| Fabric Notebooks / PySpark | Data cleaning, feature engineering, validation, and Gold table generation |
| Fabric Data Pipeline | Orchestrate ingestion and transformation activities |
| Fabric Semantic Model | Expose Gold tables and reusable fields for reporting |
| SQL Analytics Endpoint | Publish department-facing query views |
| Power BI Report | Build dashboard visuals using semantic model tables |
| Python / scipy / statsmodels | Run chi-square testing, logistic regression, and odds-ratio interpretation |

---

## Documentation

- [Statistical Validation](docs/statistical-validation.md)
- [Power BI Dashboard Case Study](dashboards/powerbi-dashboard-case-study.md)
- [Fabric Pipeline Documentation](docs/fabric-pipeline.md)
- [SQL Analytics Endpoint Views](docs/sql-analytics-views.md)
- [State Resource Priority Framework](docs/resource-priority-framework.md)

---

## Interpretation Boundary

This project uses public administrative data for operational analytics. Low-intensity placement among higher-risk or co-occurring admissions is an operational monitoring proxy, not a clinical appropriateness judgment. The results describe associations and patterns that may warrant review; they do not establish causality or patient-level clinical need.

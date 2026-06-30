# Behavioral Health Resource Allocation Analysis

### Investigating treatment access patterns and operationalizing findings with Microsoft Fabric and Power BI

---

## Overview

This project is an end-to-end healthcare analytics case study that turns public SAMHSA admissions and facility data into a repeatable Microsoft Fabric and Power BI monitoring workflow.

The analysis has two connected workstreams:

- **Treatment access friction**: among admissions with co-occurring mental health needs, identify which observable access-context segments have higher low-intensity placement rates.
- **State resource planning**: compare state-level admission burden with listed behavioral health facility availability to create a high-level planning view.

The strongest descriptive finding is in the treatment access workstream: among admissions with co-occurring mental health needs, employed patients, especially part-time employed patients, had the highest low-intensity placement rates. The result was then operationalized through curated Gold tables, a Power BI dashboard, semantic model inputs, and SQL views for downstream analysis.

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

The pipeline includes a **High-Risk Low-Intensity Placement Rate** as an operational review signal:

```text
High-Risk Low-Intensity Placement Rate =
High-risk admissions routed to low-intensity treatment
/ All high-risk admissions
```

In this project, `High Risk` is a high-risk operational review segment defined in the Silver admissions table as admissions with a co-occurring mental health condition (`PSYPROB = 1`) and an employment status of unemployed or not in the labor force. This segment is used for monitoring and state-level resource views; it is not used to define the employment-based finding below.

The employment analysis uses the **Employment-Based Low-Intensity Placement Rate**:

```text
Employment-Based Low-Intensity Placement Rate =
Co-occurring mental health admissions routed to low-intensity treatment
/ All co-occurring mental health admissions in the same employment group
```

Both metrics are review signals. They do not mean low-intensity care was clinically inappropriate for every admission.

Treatment intensity is an analytical grouping of the TEDS-A `SERVICES` service setting field. TEDS-A defines `SERVICES` as the type of treatment service or setting at admission. This project groups those service settings into three monitoring categories:

| TEDS-A `SERVICES` Code | TEDS-A Service Setting | Project Treatment Intensity |
|---:|---|---|
| 7 | Ambulatory, non-intensive outpatient | Low Intensity |
| 1 | Detox, 24-hour, hospital inpatient | Medium Intensity |
| 2 | Detox, 24-hour, free-standing residential | Medium Intensity |
| 6 | Ambulatory, intensive outpatient | Medium Intensity |
| 3 | Rehab/residential, hospital, non-detox | High Intensity |
| 4 | Rehab/residential, short term, 30 days or fewer | High Intensity |
| 5 | Rehab/residential, long term, more than 30 days | High Intensity |
| 8 | Ambulatory, detoxification | High Intensity |

This grouping is intended for operational monitoring, not clinical appropriateness scoring. It makes treatment setting patterns easier to compare across segments, but it should not be interpreted as a universal clinical severity hierarchy.

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

The project also includes a separate state-level resource priority framework that compares high-risk admission burden with listed behavioral health treatment facility availability.

![State Resource Priority Quadrant](resource-priority/images/state-resource-priority-quadrant.png)

This framework is intended for high-level resource review, not as proof of unmet need at the facility level. The current quadrant thresholds use state averages as a simple planning heuristic; a production allocation model should test alternative thresholds and add population, capacity, staffing, utilization, and geography measures.

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

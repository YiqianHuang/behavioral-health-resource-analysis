# SQL Analytics Endpoint Views

This document describes the department-facing SQL views created from the Microsoft Fabric Gold tables.

The purpose of these views is to make curated metrics reusable outside the notebook workflow. Other departments can query stable, business-readable views through the Fabric SQL Analytics Endpoint without needing access to raw CSV files, PySpark notebooks, or intermediate transformation logic.

---

## Serving Layer Purpose

The Fabric pipeline produces Gold tables for dashboarding, semantic modeling, and downstream analysis.

SQL views add a lightweight access layer on top of those Gold tables:

```text
Gold Delta tables
-> SQL Analytics Endpoint views
-> Department-facing query access
```

This keeps the Gold tables as the governed source while giving analysts a simpler interface for recurring questions.

The SQL Endpoint view list confirms that both curated views are available under `dbo > Views`.

![SQL Views Created](../fabric-pipeline/images/sql-view-created.png)

---

## View 1: Employment Access Friction

```sql
CREATE OR ALTER VIEW dbo.vw_employment_access_friction AS
SELECT
    EMPLOY_Label AS Employment_Status,
    Treatment_Intensity,
    Admissions,
    Employment_Total_Admissions,
    Low_Intensity_Admissions,
    Mismatch_Rate,
    Employment_Sort_Order,
    Treatment_Intensity_Sort_Order
FROM dbo.gold_employment_treatment_mix;
```

### Business Use

This view supports recurring monitoring of low-intensity placement rate by employment status.

It is designed for teams asking:

1. Which employment groups have the highest low-intensity placement rate?
2. How does treatment intensity mix differ across employment groups?
3. Are employed patients continuing to show higher low-intensity placement over time?

### Source Table

```text
gold_employment_treatment_mix
```

### Query Result Example

![Employment Access Friction View Result](../fabric-pipeline/images/sql-view-query-result.png)

### Key Fields

| Field | Meaning |
|---|---|
| `Employment_Status` | Business-readable employment group |
| `Treatment_Intensity` | Low, medium, or high treatment intensity grouping |
| `Admissions` | Admissions in the employment and treatment-intensity group |
| `Employment_Total_Admissions` | Total co-occurring mental health admissions in the employment group |
| `Low_Intensity_Admissions` | Low-intensity admissions in the employment group |
| `Mismatch_Rate` | Low-intensity admissions divided by total admissions in the employment group; retained as the existing field name for the employment access-friction view |
| `Employment_Sort_Order` | Sort key for Power BI and SQL result ordering |
| `Treatment_Intensity_Sort_Order` | Sort key for treatment intensity ordering |

---

## View 2: State Resource Priority

```sql
CREATE OR ALTER VIEW dbo.vw_state_resource_priority AS
SELECT
    State,
    Total_Admissions,
    High_Risk_Admissions,
    High_Risk_Low_Intensity_Admissions,
    High_Risk_Rate,
    Treatment_Mismatch_Rate,
    Facility_Count,
    Inpatient_Facility_Count,
    Residential_Facility_Count,
    Outpatient_Facility_Count,
    High_Risk_Admissions_Per_Facility,
    High_Risk_Admissions_Per_Residential_Facility,
    High_Risk_Low_Intensity_Admissions_Per_Outpatient_Facility,
    Priority_Quadrant
FROM dbo.gold_state_resource_priority;
```

### Business Use

This view supports state-level resource planning review.

It is designed for teams asking:

1. Which states show high-risk admission burden relative to listed facility availability?
2. Which states are flagged as `Expansion Priority`, `Optimization Zone`, `Low Priority`, or `Resource Rich`?
3. Where should resource-availability review or resource-planning discussions begin?

### Source Table

```text
gold_state_resource_priority
```

### Query Result Example

![State Resource Priority View Result](../fabric-pipeline/images/sql-view_state_resource_priority.png)

### Key Fields

| Field | Meaning |
|---|---|
| `State` | State abbreviation |
| `Total_Admissions` | Total TEDS-A admissions in the state |
| `High_Risk_Admissions` | Admissions classified as high risk by the operational risk framework |
| `Treatment_Mismatch_Rate` | High-risk low-intensity admissions divided by high-risk admissions; retained as the existing field name in the current Gold table |
| `Facility_Count` | Listed N-SUMHSS treatment facilities in the state |
| `High_Risk_Admissions_Per_Facility` | High-risk admission burden relative to listed facility count |
| `Priority_Quadrant` | State-level resource planning classification |

---

## How To Create The Views In Fabric

1. Open the Fabric Lakehouse.
2. Open the SQL Analytics Endpoint.
3. Create a new SQL query.
4. Run the SQL statements in `notebooks/04_sql_views.sql`.
5. Confirm the views appear under `dbo > Views`.
6. Query the views to validate the result shape.

Example validation query:

```sql
SELECT *
FROM dbo.vw_employment_access_friction
ORDER BY Employment_Sort_Order, Treatment_Intensity_Sort_Order;
```

Example state resource query:

```sql
SELECT *
FROM dbo.vw_state_resource_priority
WHERE Priority_Quadrant = 'Expansion Priority'
ORDER BY High_Risk_Admissions_Per_Facility DESC;
```

---

## Interpretation Boundary

These views expose curated operational metrics. They do not create new statistical evidence by themselves.

The employment view supports recurring monitoring of access-friction patterns. The state resource view supports high-level resource planning review. Neither view proves causality, clinical appropriateness, or unmet need at the facility level.

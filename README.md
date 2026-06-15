# Behavioral Health Risk-to-Treatment Alignment Analysis
### Turning behavioral risk signals into operational care pathway metrics

## TL;DR

Using 2023 SAMHSA TEDS-A admissions data, this project analyzes whether higher-risk behavioral health admissions are routed to treatment pathways that match their operational risk profile.

- **1.63M** total admissions analyzed
- **413K** high-risk admissions identified
- **25.39%** of all admissions were classified as high risk
- **45.16%** of high-risk admissions were routed to low-intensity care
- **186K** high-risk admissions were routed to standard outpatient care
- **7.06%** of high-risk admissions had delayed admission exposure (8+ days)

---

## The Problem

Behavioral health providers need a practical way to monitor whether patients with higher support needs are routed to care pathways that match their level of operational risk.

Admission volume alone does not show whether treatment intensity is aligned with patient risk. A patient may enter care, but still be routed to a setting that provides less support than their risk profile suggests.

This project treats risk segmentation as an **operational monitoring framework**, not a clinical diagnosis.

---

## Business Question

Are high-risk behavioral health admissions being routed to treatment pathways that match their level of need?

---

## What This Analysis Does

Using 2023 SAMHSA Treatment Episode Data Set - Admissions (TEDS-A), this dashboard creates a risk-to-treatment alignment framework:

1. Classify admissions into operational risk tiers
2. Map treatment types into low, medium, and high intensity levels
3. Measure how many high-risk admissions are routed to low-intensity care
4. Track alignment and mismatch rates as operational KPIs
5. Translate findings into intake, routing, and follow-up recommendations

---

## Key Findings

- **25.39%** of all admissions were classified as high risk.
- **45.16%** of high-risk admissions were routed to low-intensity treatment.
- **186K** high-risk admissions were routed to standard outpatient care.
- **54.84%** of high-risk admissions were routed to medium- or high-intensity care.
- **7.06%** of high-risk admissions had delayed admission exposure (8+ days).

---

## Behavioral Perspective

Patients with co-occurring mental health needs and employment instability may face compounding barriers, including financial pressure, reduced daily structure, and higher difficulty sustaining engagement with care.

From an operational perspective, this group may benefit from closer intake review, stronger pathway monitoring, and proactive follow-up workflows.

This analysis does **not** determine clinical appropriateness. It identifies measurable operational signals that care teams could review.

---

## Dashboard Pages

### 1. Executive Overview

Summarizes total admissions, high-risk admissions, high-risk rate, treatment mismatch rate, treatment type distribution, and admissions by risk profile.

### 2. Risk and Treatment Alignment

Focuses on high-risk patients and shows how they are distributed across treatment types and treatment intensity levels.

Core KPIs:

- High-Risk Alignment Rate
- Treatment Mismatch Rate
- High-Risk Low-Intensity Admissions
- High-Risk Admissions

### 3. Operational Actions

Connects the analysis to operational recommendations:

- Standardize intake risk screening
- Monitor high-risk low-intensity placement
- Review delayed admission exposure

---

## Metric Definitions

### Total Admissions

Distinct count of admission records.

### High-Risk Admissions

Admissions classified as high risk based on the operational risk segmentation logic below.

### High-Risk Rate

```text
High-Risk Admissions / Total Admissions
```

### High-Risk Low-Intensity Admissions

High-risk admissions routed to low-intensity treatment.

### Treatment Mismatch Rate

```text
High-Risk Low-Intensity Admissions / High-Risk Admissions
```

This metric measures the share of high-risk admissions routed to low-intensity care.

### High-Risk Alignment Rate

```text
Aligned High-Risk Admissions / High-Risk Admissions
```

This metric measures the share of high-risk admissions routed to medium- or high-intensity treatment pathways.

In this project, a high-risk admission is considered aligned when the treatment intensity is not low intensity. This does not prove clinical appropriateness; it is an operational routing indicator used to monitor whether higher-risk patients are being directed toward more supportive care settings.

### High-Risk Delayed Admission Rate

```text
High-risk admissions with DAYWAIT = 2, 3, or 4 / High-Risk Admissions
```

This metric measures the share of high-risk admissions with an admission wait time of 8 days or more.

Based on the TEDS-A `DAYWAIT` codebook, the delayed admission group includes:

- `DAYWAIT = 2`: 8-14 days
- `DAYWAIT = 3`: 15-30 days
- `DAYWAIT = 4`: 31+ days

This KPI is used as an operational warning signal. It does not prove that longer wait time causes dropout, but it helps identify high-risk admissions that may need additional follow-up before admission.

---

## Risk Segmentation Logic

Risk tiers are based on two available admission indicators:

- `PSYPROB`: co-occurring mental health / psychiatric problem flag
- `EMPLOY`: employment status

### Codebook Reference

The segmentation uses two coded fields from the TEDS-A dataset:

| Field | Code | Meaning |
|---|---:|---|
| `PSYPROB` | `1` | Co-occurring mental health / psychiatric problem reported |
| `PSYPROB` | `2` | No co-occurring mental health / psychiatric problem reported |
| `EMPLOY` | `1` | Full-time employment |
| `EMPLOY` | `2` | Part-time employment |
| `EMPLOY` | `3` | Unemployed |
| `EMPLOY` | `4` | Not in labor force |

### High Risk

```text
PSYPROB = 1
AND
EMPLOY IN (3, 4)
```

Interpretation: co-occurring mental health flag plus unemployment or not-in-labor-force status.

### Medium Risk

```text
PSYPROB = 1 AND EMPLOY = 2
OR
PSYPROB = 2 AND EMPLOY = 3
```

Interpretation: partial employment instability or unemployment without a co-occurring mental health flag.

### Low Risk

```text
EMPLOY = 1
```

Interpretation: full-time employment, with or without a co-occurring mental health flag.

This segmentation is an **operational proxy**, not a clinical diagnosis.

---

## Treatment Intensity Mapping

### Low Intensity

- Standard Outpatient

### Medium Intensity

- Detox - Outpatient
- Rehab - Outpatient
- Intensive Outpatient (IOP)

### High Intensity

- Detox - Residential
- Rehab - Long-term Residential
- Rehab - Short-term Residential
- Intensive Residential

---

## Recommendations

### 1. Standardize Intake Risk Screening

Use available admission indicators to flag high-risk patients before treatment pathway assignment.

### 2. Monitor High-Risk Low-Intensity Placement

Track the percentage of high-risk admissions routed to standard outpatient care as an operational quality indicator.

### 3. Review Delayed Admission Exposure

Monitor high-risk patients with 8+ day admission waits and consider proactive follow-up workflows.

---

## Tools & Methods

| Tool | Purpose |
|---|---|
| SAMHSA TEDS-A 2023 | Public admissions dataset |
| Power Query | Data cleaning and feature engineering |
| DAX | KPI and metric design |
| Power BI | Dashboard design and visualization |
| Microsoft Fabric | Planned end-to-end pipeline extension |

---

## Limitations

- TEDS-A is admission-based, not person-based. One person may appear more than once.
- Risk segmentation is based on available administrative fields.
- The analysis does not prove clinical appropriateness or treatment outcomes.
- The analysis does not make causal claims about wait time and dropout.
- Unknown or missing values affect some distributions.
- Recommendations should be validated with clinical and operational stakeholders before use in a real care setting.

---

## Next Step

The next version of this project will extend the dashboard into a Microsoft Fabric pipeline:

```text
Raw admissions data
-> Lakehouse / Warehouse
-> Dataflow Gen2 or Notebook transformations
-> Curated Gold tables
-> Semantic model
-> Power BI dashboard
```

This will demonstrate the full data workflow behind the analysis, from raw behavioral health data to business-ready operational metrics.


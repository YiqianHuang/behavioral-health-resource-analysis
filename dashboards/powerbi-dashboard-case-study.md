# Behavioral Health Treatment Access Friction Analysis

### Power BI dashboard case study: using employment context to explain treatment mismatch

## TL;DR

Among admissions with co-occurring mental health needs, Treatment Mismatch Rate is highest for employed patients:

- Part-time employed admissions: **68.7%**
- Full-time employed admissions: **65.5%**
- Unemployed admissions: **42.0%**

This suggests that mismatch is not only a capacity issue. For employed patients, low-intensity placement may also reflect **access-design friction**: higher-intensity care may be harder to use when treatment schedules conflict with work.

---

## Business Problem

Behavioral health providers often monitor admission volume and treatment type, but those metrics do not fully explain whether patients can realistically access the level of care they may need.

For patients with co-occurring mental health needs, being routed to low-intensity outpatient care can signal a potential treatment mismatch. The key question is whether that mismatch is only driven by system capacity, or whether some patient groups face practical barriers to using higher-intensity treatment.

---

## Business Question

What may explain Treatment Mismatch Rate among admissions with co-occurring mental health needs, and does employment status reveal an access barrier?

---

## What This Dashboard Does

This Power BI dashboard examines treatment intensity among admissions with co-occurring mental health needs and compares mismatch patterns by employment status.

It focuses on three questions:

1. How many co-occurring mental health admissions are routed to low-, medium-, or high-intensity treatment?
2. Which employment groups have the highest Treatment Mismatch Rate?
3. Does the pattern suggest an access-design problem beyond total admission volume?

---

## Key Finding

Full-time and part-time employed admissions have the highest Treatment Mismatch Rates, even though they are not the largest admission-volume groups.

This makes employment status useful as an access-context variable. It helps identify whether treatment mismatch may be related to how care is scheduled and delivered, not only how much capacity exists.

---

## Why This Matters

The Treatment Mismatch Rate is highest among full-time (65.5%) and part-time (68.7%) employed admissions - higher than unemployed admissions (42.0%). This is the opposite of what a pure capacity-shortage explanation would predict.

This points to a potential accessibility problem rather than only a clinical-need problem. Employed individuals may be defaulting to low-intensity outpatient care not because it best matches their need, but because higher-intensity programs can be harder to fit around work schedules.

In practice, this means working patients may face a trade-off between keeping income stable and using higher-intensity services. The business opportunity is not necessarily only more beds - it is also reviewing whether care pathways are designed around work-schedule constraints.

---

## Dashboard Preview

### Treatment Access Friction by Employment Status

![Treatment Access Friction by Employment Status](images/employment-mismatch-by-status.png)

---

## How To Read The Visual

The stacked columns show the treatment intensity mix for admissions with co-occurring mental health needs.

- Orange: low-intensity care
- Grey: medium-intensity care
- Blue: high-intensity care
- Black line: Treatment Mismatch Rate

The key pattern is that full-time and part-time employed groups have the highest mismatch rates, meaning low-intensity placement is proportionally more common for working patients with co-occurring mental health needs.

---

## Recommended Business Actions

1. Track Treatment Mismatch Rate by employment status as an access-design KPI.
2. Review whether intake routing captures work-schedule constraints before assigning treatment pathway.
3. Test evening or weekend IOP slots if program schedule data becomes available for evaluation.
4. Evaluate telehealth or hybrid care options if service modality and follow-up data become available.
5. Use this dashboard as an operational monitoring tool, not as a clinical appropriateness decision rule.

---

## Metric Definitions

### Co-occurring Mental Health Admissions

Admissions where `PSYPROB = 1` in TEDS-A, meaning a co-occurring mental health / psychiatric problem was reported.

### Treatment Mismatch Rate

Co-occurring mental health admissions routed to low-intensity care divided by all co-occurring mental health admissions in the same employment group.

### Treatment Intensity Mix

The distribution of co-occurring mental health admissions across low-, medium-, and high-intensity treatment.

### Employment Status

Employment status is used as an access-context variable. It does not define clinical severity by itself, but it helps identify whether work-schedule constraints may be related to treatment pathway mismatch.

---

## Tools & Methods

| Tool | Purpose |
|---|---|
| SAMHSA TEDS-A 2023 | Public admissions dataset |
| Power Query | Data cleaning and feature preparation |
| Fabric Semantic Model | Expose Gold tables and reusable fields for reporting |
| Power BI Report | Build dashboard visuals using semantic model tables |

---

## Limitations

- TEDS-A is admission-based, not person-based. One person may appear more than once.
- The analysis does not prove that employment causes treatment mismatch.
- Treatment intensity is an operational grouping created for analysis, not a clinical appropriateness judgment.
- Sensitivity checks support the employment pattern across age, wait-time, and state views, but those checks describe association and do not establish causality.
- The current dataset does not include program schedule, appointment time, telehealth modality, or follow-up outcome fields, so proposed interventions require additional data before impact can be evaluated.
- Recommendations should be validated with clinical and operational stakeholders before use in a real care setting.

---

## Data Source

SAMHSA Treatment Episode Data Set - Admissions (TEDS-A) 2023  
Public Use File: https://www.samhsa.gov/data/data-we-collect/teds-treatment-episode-data-set/datafiles

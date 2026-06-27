# Statistical Validation and Sensitivity Analysis

This document provides the detailed validation behind the employment-based low-intensity placement finding summarized in the project README.

The broader project first identified a high-risk low-intensity placement signal: a substantial number of admissions classified as high risk were routed to low-intensity treatment. This validation examines whether employment status helps explain where that pattern is concentrated among admissions with co-occurring mental health needs.

The validation asks:

```text
Is employment status associated with low-intensity placement among admissions with co-occurring mental health needs, and does the pattern remain visible across available subgroups?
```

The analysis is descriptive, not causal.

---

## Analysis Sample

The validation sample was built from admissions with co-occurring mental health needs, defined as:

```text
PSYPROB = 1
```

EDA checks found that 538,172 of 686,928 co-occurring mental health admissions had usable employment values, or 78.3%. The remaining 148,756 admissions, or 21.7%, had unknown, not collected, or invalid employment values and were excluded from employment-segmented validation.

| Measure | Value |
|---|---:|
| Co-occurring mental health admissions | 686,928 |
| Usable employment records | 538,172 |
| Unknown / invalid employment records | 148,756 |
| Usable employment share | 78.3% |
| Excluded employment share | 21.7% |

---

## Metric Definition

This project defines employment-based low-intensity placement as an operational monitoring proxy, not a clinical judgment.

```text
Employment-Based Low-Intensity Placement Rate =
Co-occurring mental health admissions routed to low-intensity care
/ All co-occurring mental health admissions in the same group
```

Admissions involving co-occurring mental health needs that receive low-intensity outpatient services are flagged for monitoring because these cases may warrant additional operational review.

---

## Exploratory Analysis

Treatment intensity was concentrated but not fully dominated by one category.

| Treatment Intensity | Admissions | Share |
|---|---:|---:|
| Low Intensity | 329,884 | 48.0% |
| Medium Intensity | 182,890 | 26.6% |
| High Intensity | 174,154 | 25.4% |

Raw service codes were more unevenly distributed, with the largest raw service category accounting for 48.0% of co-occurring admissions. This supported grouping raw service codes into broader operational intensity categories for analysis.

---

## Analytical Design Decisions

### Why Employment Status?

Employment status was selected because it captures an operational context that may influence treatment accessibility. Unlike demographic characteristics that are largely descriptive, employment may affect a patient's ability to attend higher-intensity outpatient programs with fixed daytime schedules.

This project does not assume employment causes low-intensity placement. It uses employment as a practical segmentation variable for operational monitoring.

### Why Logistic Regression?

Logistic regression was selected because the goal was inference and interpretability rather than predictive performance. The model estimates whether employment status remains associated with low-intensity placement after adjusting for available administrative characteristics.

Covariates were selected based on data availability and their potential relationship with treatment access: age, sex, race, state, and wait-time category.

---

## Chi-Square Test

The chi-square test evaluated whether employment status and low-intensity placement were statistically independent.

| Employment Status | Not Low-Intensity | Low-Intensity | Low-Intensity Placement Rate |
|---|---:|---:|---:|
| Part-time employed | 10,640 | 23,360 | 68.7% |
| Full-time employed | 31,517 | 59,889 | 65.5% |
| Not in labor force | 100,368 | 95,283 | 48.7% |
| Unemployed | 126,013 | 91,102 | 42.0% |

| Test | Result |
|---|---:|
| Chi-square statistic | 19,308.84 |
| Degrees of freedom | 3 |
| P-value | < 0.001 |
| Cramer's V | 0.189 |

The result indicates a statistically significant association between employment status and low-intensity placement. Because the validation sample is large, Cramer's V is included as an effect-size check; the association is meaningful but should not be interpreted as causal proof.

---

## Logistic Regression

An adjusted logistic regression tested whether employment status remained associated with low-intensity placement after controlling for available covariates:

```text
Low_Intensity_Placement ~ Employment_Status + AGE + SEX + RACE + STFIPS + DAYWAIT
```

In the notebook implementation, this binary outcome is stored as `Treatment_Mismatch`; the field name is retained in code for continuity, but it represents low-intensity placement within the employment validation sample.

| Employment Status Term | Odds Ratio | Business Interpretation |
|---|---:|---|
| Part-time employed vs full-time employed | 1.066 | Slightly higher odds of low-intensity placement than full-time employed admissions |
| Not in labor force vs full-time employed | 0.411 | Lower odds of low-intensity placement than full-time employed admissions |
| Unemployed vs full-time employed | 0.403 | Lower odds of low-intensity placement than full-time employed admissions |

Employment status remained associated with low-intensity placement after adjustment, suggesting that the observed pattern was not fully explained by available demographic and administrative characteristics.

Unknown or not-collected wait-time codes were retained as categorical values in the regression control. Wait-time sensitivity checks separately excluded unknown wait-time groups to make the subgroup comparison easier to interpret.

---

## Sensitivity Analysis

Stratified sensitivity checks were added to evaluate whether the employment-based low-intensity placement pattern was isolated to a single subgroup.

| Sensitivity Check | Result |
|---|---|
| Age groups | Part-time employed admissions ranked highest in all 12 age groups |
| Wait-time groups | Employed groups ranked highest in all 5 wait-time groups: part-time in 3 and full-time in 2 |
| States with sufficient sample size | Employed groups ranked highest in 25 of 37 states, or 67.6% |

These checks suggest that the employment-based low-intensity placement pattern was not driven only by one age group, wait-time category, or small set of states. The pattern remained most consistent across age and wait-time segments and appeared in a majority of states with sufficient subgroup sample size.

---

## Operational Interpretation

The dashboard finding should be used as a monitoring signal, not as proof of root cause.

| Observation | What It Supports | What It Does Not Prove |
|---|---|---|
| Employed patients have higher low-intensity placement rates | Employment status is useful as an access-context segment | Employment causes low-intensity placement |
| Low-intensity placement is higher among working patients | The pattern may warrant routing or scheduling review | Low-intensity care is clinically inappropriate for every case |
| Statistical validation and sensitivity checks support the pattern | The association is robust across available controls and segments | Work schedule constraints are the confirmed mechanism |

Potential future evaluation candidates:

- Track low-intensity placement rate by employment status as a repeatable monitoring KPI.
- Review whether intake routing should capture work-schedule constraints before assigning a treatment pathway.
- Evaluate extended-hour, weekend, telehealth, or hybrid interventions only after program schedule, service modality, capacity, and follow-up data are available.

These interventions target operational barriers that are potentially modifiable by providers, unlike demographic characteristics.

A reduction in employment-based low-intensity placement over time could indicate that access to higher-intensity services is becoming more evenly distributed across employment groups, although additional outcome measures would be needed to evaluate patient benefit.

---

## Limitations

- The analysis is descriptive and does not establish causality.
- TEDS-A is admission-based, not person-based; one person may appear more than once.
- Treatment intensity is an operational grouping created for analysis, not a clinical appropriateness rule.
- Employment-based low-intensity placement is an operational monitoring proxy, not a clinical diagnosis.
- The employment analysis does not control for insurance coverage, income, geography, referral pathway, employer support, severity, state policy, or other potential confounders.
- The current data does not include program schedule, slot time, telehealth modality, staffing, utilization, or follow-up outcomes.
- The logistic regression adjusts for available administrative covariates only; unmeasured confounding may remain.
- Sensitivity checks evaluate consistency across observed segments but do not identify the causal mechanism behind low-intensity placement.

---

## Notebook

Notebook implementation:

```text
notebooks/03_statistical_validation_sensitivity_analysis.ipynb
notebooks/03_statistical_validation_sensitivity_analysis.py
```

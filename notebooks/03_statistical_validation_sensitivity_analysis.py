#!/usr/bin/env python
# coding: utf-8

# ## Statistical Validation
# 
# null

# # Statistical Validation and Sensitivity Analysis
# 
# ## 1. Purpose

# This notebook validates whether employment status is associated with Low-Intensity Placement among admissions with co-occurring mental health needs.
# It includes chi-square testing, adjusted logistic regression, and stratified sensitivity checks by age, wait time, and state.

# ## 2. Load Analysis Dataset from Fabric Lakehouse

# In[ ]:


df = spark.table("silver_tedsa_admissions_cleaned")

display(df.limit(10))


# ## 3. Create Analysis Sample

# In[ ]:


from pyspark.sql import functions as F

# Load source table from Fabric Lakehouse
df = spark.table("silver_tedsa_admissions_cleaned")

# Check source fields
print("Columns in silver_tedsa_admissions_cleaned:")
print(df.columns)

# Build analysis sample based on actual TEDS-A / Silver table fields
# Source-field mapping:
# PSYPROB = co-occurring mental health flag
# EMPLOY / EMPLOY_Label = employment status
# SEX = sex field, not GENDER
# STFIPS = state FIPS field, not STATE
# Treatment_Intensity = existing treatment intensity field in Silver table

analysis_df = (
    df
    .filter(F.col("PSYPROB") == 1)
    .filter(F.col("EMPLOY").isin(1, 2, 3, 4))
    .filter(F.col("Treatment_Intensity").isNotNull())
    .withColumn(
        "Employment_Status",
        F.when(F.col("EMPLOY") == 1, "Full-time employed")
         .when(F.col("EMPLOY") == 2, "Part-time employed")
         .when(F.col("EMPLOY") == 3, "Unemployed")
         .when(F.col("EMPLOY") == 4, "Not in labor force")
    )
    .withColumn(
        "Low_Intensity_Placement",
        F.when(F.lower(F.col("Treatment_Intensity")).contains("low"), F.lit(1))
         .otherwise(F.lit(0))
    )
    .select(
        "Low_Intensity_Placement",
        "Treatment_Intensity",
        "Employment_Status",
        "EMPLOY",
        "AGE",
        "SEX",
        "RACE",
        "STFIPS",
        "DAYWAIT"
    )
    .dropna()
)

display(analysis_df.limit(10))


# ## 4. Check Sample Size

# In[ ]:


analysis_df.count()


# ## 5. Convert Spark DataFrame to Pandas

# In[ ]:


pdf = analysis_df.toPandas()

pdf.head()


# ## 6. Chi-Square Test: Employment Status vs Low-Intensity Placement

# In[ ]:


import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency

chi_pdf = (
    analysis_df
    .groupBy("Employment_Status", "Low_Intensity_Placement")
    .count()
    .toPandas()
)

contingency_table = chi_pdf.pivot(
    index="Employment_Status",
    columns="Low_Intensity_Placement",
    values="count"
).fillna(0)

chi2, p_value, dof, expected = chi2_contingency(contingency_table)
n = contingency_table.to_numpy().sum()
min_dimension = min(contingency_table.shape) - 1
cramers_v = np.sqrt(chi2 / (n * min_dimension))

print("Contingency Table:")
print(contingency_table)

print("\nChi-square statistic:", chi2)
print("Degrees of freedom:", dof)
print("P-value:", p_value)
print("Cramer's V:", cramers_v)


# ## 7. Logistic Regression: Adjusted Association with Low-Intensity Placement

# In[ ]:


pdf = analysis_df.toPandas()

pdf.head()


# In[ ]:


import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

model = smf.logit(
    "Low_Intensity_Placement ~ C(Employment_Status) + C(AGE) + C(SEX) + C(RACE) + C(STFIPS) + C(DAYWAIT)",
    data=pdf
).fit()

print(model.summary())


# ## 8. Convert Logistic Regression Coefficients to Odds Ratios

# In[ ]:


odds_ratios = pd.DataFrame({
    "variable": model.params.index,
    "odds_ratio": np.exp(model.params.values),
    "coef": model.params.values,
    "p_value": model.pvalues.values
})

odds_ratios


# ## 9. Sensitivity Analysis by Age

# In[ ]:


from pyspark.sql import functions as F
from pyspark.sql.window import Window

# Calculate low-intensity placement rate by AGE and Employment_Status
age_sensitivity = (
    analysis_df
    .groupBy("AGE", "Employment_Status")
    .agg(
        F.count("*").alias("admissions"),
        F.sum("Low_Intensity_Placement").alias("low_intensity_admissions")
    )
    .withColumn(
        "low_intensity_placement_rate",
        F.col("low_intensity_admissions") / F.col("admissions")
    )
)

# Rank employment groups within each age group by low-intensity placement rate
age_window = Window.partitionBy("AGE").orderBy(F.col("low_intensity_placement_rate").desc())

age_sensitivity_ranked = (
    age_sensitivity
    .withColumn("rank_within_age", F.row_number().over(age_window))
    .orderBy("AGE", "rank_within_age")
)

display(age_sensitivity_ranked)


# ## 9.1 Age Sensitivity Summary

# In[ ]:


age_top_group_summary = (
    age_sensitivity_ranked
    .filter(F.col("rank_within_age") == 1)
    .groupBy("Employment_Status")
    .agg(
        F.count("*").alias("age_groups_ranked_highest")
    )
    .orderBy(F.col("age_groups_ranked_highest").desc())
)

display(age_top_group_summary)


# ## 10. Sensitivity Analysis by Wait Time

# In[ ]:


from pyspark.sql import functions as F
from pyspark.sql.window import Window

# Create a readable wait-time grouping.
# DAYWAIT is coded as admission wait time category in the source data.
wait_sensitivity_base = (
    analysis_df
    .withColumn(
        "Wait_Time_Group",
        F.when(F.col("DAYWAIT") == 0, "0 days")
         .when(F.col("DAYWAIT") == 1, "1-7 days")
         .when(F.col("DAYWAIT") == 2, "8-14 days")
         .when(F.col("DAYWAIT") == 3, "15-30 days")
         .when(F.col("DAYWAIT") == 4, "31+ days")
         .otherwise("Unknown / not collected")
    )
    .filter(F.col("Wait_Time_Group") != "Unknown / not collected")
)

# Calculate low-intensity placement rate by wait-time group and employment status
wait_time_sensitivity = (
    wait_sensitivity_base
    .groupBy("Wait_Time_Group", "Employment_Status")
    .agg(
        F.count("*").alias("admissions"),
        F.sum("Low_Intensity_Placement").alias("low_intensity_admissions")
    )
    .withColumn(
        "low_intensity_placement_rate",
        F.col("low_intensity_admissions") / F.col("admissions")
    )
)

# Rank employment groups within each wait-time group by low-intensity placement rate
wait_window = Window.partitionBy("Wait_Time_Group").orderBy(F.col("low_intensity_placement_rate").desc())

wait_time_sensitivity_ranked = (
    wait_time_sensitivity
    .withColumn("rank_within_wait_time", F.row_number().over(wait_window))
    .orderBy("Wait_Time_Group", "rank_within_wait_time")
)

display(wait_time_sensitivity_ranked)


# ## 10.1 Wait-Time Sensitivity Summary

# In[ ]:


wait_time_top_group_summary = (
    wait_time_sensitivity_ranked
    .filter(F.col("rank_within_wait_time") == 1)
    .groupBy("Employment_Status")
    .agg(
        F.count("*").alias("wait_time_groups_ranked_highest")
    )
    .orderBy(F.col("wait_time_groups_ranked_highest").desc())
)

display(wait_time_top_group_summary)


# ## 11. Sensitivity Analysis by State

# In[ ]:


from pyspark.sql import functions as F
from pyspark.sql.window import Window

# State-level sensitivity check
# Use a minimum sample threshold to avoid over-interpreting small state-employment cells.
MIN_STATE_EMPLOYMENT_ADMISSIONS = 500

state_sensitivity = (
    analysis_df
    .groupBy("STFIPS", "Employment_Status")
    .agg(
        F.count("*").alias("admissions"),
        F.sum("Low_Intensity_Placement").alias("low_intensity_admissions")
    )
    .withColumn(
        "low_intensity_placement_rate",
        F.col("low_intensity_admissions") / F.col("admissions")
    )
    .filter(F.col("admissions") >= MIN_STATE_EMPLOYMENT_ADMISSIONS)
)

# Rank employment groups within each state by low-intensity placement rate
state_window = Window.partitionBy("STFIPS").orderBy(F.col("low_intensity_placement_rate").desc())

state_sensitivity_ranked = (
    state_sensitivity
    .withColumn("rank_within_state", F.row_number().over(state_window))
    .orderBy("STFIPS", "rank_within_state")
)

display(state_sensitivity_ranked)


# ## 11.1 State Sensitivity Summary

# In[ ]:


state_top_group_summary = (
    state_sensitivity_ranked
    .filter(F.col("rank_within_state") == 1)
    .groupBy("Employment_Status")
    .agg(
        F.count("*").alias("states_ranked_highest")
    )
    .orderBy(F.col("states_ranked_highest").desc())
)

display(state_top_group_summary)


# ## 11.2 State Sensitivity Coverage

# In[ ]:


state_sensitivity_coverage = (
    state_sensitivity_ranked
    .select("STFIPS")
    .distinct()
    .agg(
        F.count("*").alias("states_included_after_min_sample_filter")
    )
)

display(state_sensitivity_coverage)


# ## 12. Interpretation Summary
# 
# The statistical validation supports employment status as a meaningful access-context variable for Low-Intensity Placement among admissions with co-occurring mental health needs.
# 
# The chi-square test found a statistically significant association between employment status and Low-Intensity Placement. Logistic regression showed that the association remained significant after adjusting for age, sex, race, state, and wait-time category.
# 
# Sensitivity checks showed that the employment-based low-intensity placement pattern was not isolated to a single subgroup. Part-time employed admissions ranked highest across all age groups; employed groups ranked highest across all wait-time groups; and employed groups ranked highest in 25 of 37 states with sufficient subgroup sample size.
# 
# These results should be interpreted as evidence of a robust descriptive pattern, not causal proof. Additional operational data, such as program schedule, service modality, intake routing rules, insurance coverage, and follow-up outcomes, would be needed to evaluate why this pattern occurs.
# 

# ## 13. EDA Check: Unknown Employment Values

# In[ ]:


from pyspark.sql import functions as F

# Reload source table in case the notebook session was restarted
df = spark.table("silver_tedsa_admissions_cleaned")

# Check unknown / invalid employment values in the co-occurring mental health sample
employment_eda = (
    df
    .filter(F.col("PSYPROB") == 1)
    .withColumn(
        "Employment_Value_Group",
        F.when(F.col("EMPLOY").isin(1, 2, 3, 4), "Usable employment value")
         .otherwise("Unknown / not collected / invalid")
    )
    .groupBy("Employment_Value_Group")
    .agg(
        F.count("*").alias("admissions")
    )
)

employment_total = employment_eda.agg(F.sum("admissions").alias("total_admissions"))

employment_eda_pct = (
    employment_eda
    .crossJoin(employment_total)
    .withColumn(
        "share_of_cooccurring_admissions",
        F.col("admissions") / F.col("total_admissions")
    )
    .orderBy(F.col("admissions").desc())
)

display(employment_eda_pct)


# ## 14. EDA Check: Treatment Intensity Distribution

# In[ ]:


from pyspark.sql import functions as F

# Reload source table in case the notebook session was restarted
df = spark.table("silver_tedsa_admissions_cleaned")

# Check whether treatment intensity groups are balanced or concentrated
treatment_intensity_eda = (
    df
    .filter(F.col("PSYPROB") == 1)
    .filter(F.col("Treatment_Intensity").isNotNull())
    .groupBy("Treatment_Intensity")
    .agg(
        F.count("*").alias("admissions")
    )
)

treatment_intensity_total = treatment_intensity_eda.agg(F.sum("admissions").alias("total_admissions"))

treatment_intensity_eda_pct = (
    treatment_intensity_eda
    .crossJoin(treatment_intensity_total)
    .withColumn(
        "share_of_cooccurring_admissions",
        F.col("admissions") / F.col("total_admissions")
    )
    .orderBy(F.col("admissions").desc())
)

display(treatment_intensity_eda_pct)


# ## 15. EDA Check: Raw Treatment Service Distribution

# In[ ]:


from pyspark.sql import functions as F

# Reload source table in case the notebook session was restarted
df = spark.table("silver_tedsa_admissions_cleaned")

# Raw SERVICES distribution before grouping into treatment intensity
services_eda = (
    df
    .filter(F.col("PSYPROB") == 1)
    .groupBy("SERVICES")
    .agg(
        F.count("*").alias("admissions")
    )
)

services_total = services_eda.agg(F.sum("admissions").alias("total_admissions"))

services_eda_pct = (
    services_eda
    .crossJoin(services_total)
    .withColumn(
        "share_of_cooccurring_admissions",
        F.col("admissions") / F.col("total_admissions")
    )
    .orderBy(F.col("admissions").desc())
)

display(services_eda_pct)

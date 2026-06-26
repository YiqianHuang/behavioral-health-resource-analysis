#!/usr/bin/env python
# coding: utf-8

# ## Transformation_nb
# 
# New notebook

# ## 3. Build Silver Cleaned Admissions Table
# 
# Create business-readable fields for mental health status, employment status, wait-time tier, operational risk profile, and treatment intensity.

# In[7]:


from pyspark.sql import functions as F

bronze_df = spark.table("bronze_tedsa_admissions_2023")

silver_df = (
    bronze_df
    .withColumn(
        "PSYPROB_Label",
        F.when(F.col("PSYPROB") == 1, "Co-occurring mental health problem")
         .when(F.col("PSYPROB") == 2, "No co-occurring mental health problem")
         .otherwise("Unknown")
    )
    .withColumn(
        "EMPLOY_Label",
        F.when(F.col("EMPLOY") == 1, "Full-time employment")
         .when(F.col("EMPLOY") == 2, "Part-time employment")
         .when(F.col("EMPLOY") == 3, "Unemployed")
         .when(F.col("EMPLOY") == 4, "Not in labor force")
         .otherwise("Unknown")
    )
    .withColumn(
        "Wait_Time_Tier",
        F.when(F.col("DAYWAIT") == 0, "Same day")
         .when(F.col("DAYWAIT") == 1, "Short wait (1-7 days)")
         .when(F.col("DAYWAIT") == 2, "Moderate wait (8-14 days)")
         .when(F.col("DAYWAIT") == 3, "Long wait (15-30 days)")
         .when(F.col("DAYWAIT") == 4, "Extended wait (31+ days)")
         .otherwise("Unknown")
    )
    .withColumn(
        "Risk_Profile",
        F.when(
            (F.col("PSYPROB") == 1) & (F.col("EMPLOY").isin(3, 4)),
            "High Risk"
        )
        .when(
            ((F.col("PSYPROB") == 1) & (F.col("EMPLOY") == 2)) |
            ((F.col("PSYPROB") == 2) & (F.col("EMPLOY") == 3)),
            "Medium Risk"
        )
        .when(
            F.col("EMPLOY") == 1,
            "Low Risk"
        )
        .otherwise("Unknown")
    )
    .withColumn(
        "Treatment_Intensity",
        F.when(F.col("SERVICES") == 7, "Low Intensity")
         .when(F.col("SERVICES").isin(1, 2, 6), "Medium Intensity")
         .when(F.col("SERVICES").isin(3, 4, 5, 8), "High Intensity")
         .otherwise("Unknown")
    )
)


# In[8]:


silver_df.write \
    .mode("overwrite") \
    .format("delta") \
    .saveAsTable("silver_tedsa_admissions_cleaned")


# In[ ]:


silver_check = spark.table("silver_tedsa_admissions_cleaned")


# ## 4. Build Gold KPI Summary Table
# 
# Calculate the core operational KPIs used in the dashboard, including high-risk rate, treatment mismatch rate, alignment rate, and delayed admission rate.

# In[10]:


from pyspark.sql import functions as F

silver_df = spark.table("silver_tedsa_admissions_cleaned")

total_admissions = silver_df.select("CASEID").distinct().count()

high_risk_admissions = (
    silver_df
    .filter(F.col("Risk_Profile") == "High Risk")
    .select("CASEID")
    .distinct()
    .count()
)

high_risk_low_intensity_admissions = (
    silver_df
    .filter(
        (F.col("Risk_Profile") == "High Risk") &
        (F.col("Treatment_Intensity") == "Low Intensity")
    )
    .select("CASEID")
    .distinct()
    .count()
)

aligned_high_risk_admissions = (
    silver_df
    .filter(
        (F.col("Risk_Profile") == "High Risk") &
        (F.col("Treatment_Intensity") != "Low Intensity")
    )
    .select("CASEID")
    .distinct()
    .count()
)

high_risk_delayed_admissions = (
    silver_df
    .filter(
        (F.col("Risk_Profile") == "High Risk") &
        (F.col("DAYWAIT").isin(2, 3, 4))
    )
    .select("CASEID")
    .distinct()
    .count()
)

gold_kpi_summary = spark.createDataFrame(
    [
        ("Total Admissions", total_admissions, None),
        ("High-Risk Admissions", high_risk_admissions, None),
        ("High Risk Rate", high_risk_admissions, high_risk_admissions / total_admissions),
        ("High-Risk Low-Intensity Admissions", high_risk_low_intensity_admissions, None),
        ("Treatment Mismatch Rate", high_risk_low_intensity_admissions, high_risk_low_intensity_admissions / high_risk_admissions),
        ("High-Risk Alignment Rate", aligned_high_risk_admissions, aligned_high_risk_admissions / high_risk_admissions),
        ("High-Risk Delayed Admission Rate", high_risk_delayed_admissions, high_risk_delayed_admissions / high_risk_admissions),
    ],
    ["Metric", "Value", "Rate"]
)

gold_kpi_summary.write \
    .mode("overwrite") \
    .format("delta") \
    .saveAsTable("gold_kpi_summary")


# ## 5. Build Gold Dashboard-Ready Aggregate Tables
# 
# Create aggregate tables that support dashboard visuals for risk-treatment alignment, wait-time monitoring, and treatment distribution.

# In[11]:


from pyspark.sql import functions as F

silver_df = spark.table("silver_tedsa_admissions_cleaned")

gold_risk_treatment_matrix = (
    silver_df
    .groupBy("Risk_Profile", "Treatment_Intensity")
    .agg(F.countDistinct("CASEID").alias("Admissions"))
    .orderBy("Risk_Profile", "Treatment_Intensity")
)

gold_wait_time_by_risk = (
    silver_df
    .filter(F.col("Wait_Time_Tier") != "Unknown")
    .groupBy("Risk_Profile", "Wait_Time_Tier", "DAYWAIT")
    .agg(F.countDistinct("CASEID").alias("Admissions"))
    .orderBy("Risk_Profile", "DAYWAIT")
)

gold_treatment_distribution = (
    silver_df
    .groupBy("SERVICES", "Treatment_Intensity")
    .agg(F.countDistinct("CASEID").alias("Admissions"))
    .orderBy("SERVICES")
)

gold_risk_treatment_matrix.write \
    .mode("overwrite") \
    .format("delta") \
    .saveAsTable("gold_risk_treatment_matrix")

gold_wait_time_by_risk.write \
    .mode("overwrite") \
    .format("delta") \
    .saveAsTable("gold_wait_time_by_risk")

gold_treatment_distribution.write \
    .mode("overwrite") \
    .format("delta") \
    .saveAsTable("gold_treatment_distribution")


# ## 6. Build Employment Access Friction Gold Table
# 
# Create an employment-by-treatment-intensity table to monitor whether patients with co-occurring mental health needs are routed into lower-intensity care differently by employment status.

# In[1]:


from pyspark.sql import functions as F

silver_df = spark.table("silver_tedsa_admissions_cleaned")

cooccurring_df = (
    silver_df
    .filter(F.col("PSYPROB") == 1)
    .filter(F.col("EMPLOY_Label") != "Unknown")
    .filter(F.col("Treatment_Intensity").isNotNull())
)

employment_totals = (
    cooccurring_df
    .groupBy("EMPLOY_Label")
    .agg(F.countDistinct("CASEID").alias("Employment_Total_Admissions"))
)

low_intensity_by_employment = (
    cooccurring_df
    .filter(F.col("Treatment_Intensity") == "Low Intensity")
    .groupBy("EMPLOY_Label")
    .agg(F.countDistinct("CASEID").alias("Low_Intensity_Admissions"))
)

gold_employment_treatment_mix = (
    cooccurring_df
    .groupBy("EMPLOY_Label", "Treatment_Intensity")
    .agg(F.countDistinct("CASEID").alias("Admissions"))
    .join(employment_totals, on="EMPLOY_Label", how="left")
    .join(low_intensity_by_employment, on="EMPLOY_Label", how="left")
    .withColumn(
        "Mismatch_Rate",
        F.col("Low_Intensity_Admissions") / F.col("Employment_Total_Admissions")
    )
    .withColumn(
        "Employment_Sort_Order",
        F.when(F.col("EMPLOY_Label") == "Part-time employment", 1)
         .when(F.col("EMPLOY_Label") == "Full-time employment", 2)
         .when(F.col("EMPLOY_Label") == "Not in labor force", 3)
         .when(F.col("EMPLOY_Label") == "Unemployed", 4)
         .otherwise(99)
    )
    .withColumn(
        "Treatment_Intensity_Sort_Order",
        F.when(F.col("Treatment_Intensity") == "Low Intensity", 1)
         .when(F.col("Treatment_Intensity") == "Medium Intensity", 2)
         .when(F.col("Treatment_Intensity") == "High Intensity", 3)
         .otherwise(99)
    )
)

(
    gold_employment_treatment_mix.write
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .format("delta")
    .saveAsTable("gold_employment_treatment_mix")
)


# ## 7. Validate KPI Outputs
# 
# Review the Gold KPI summary table to confirm that the pipeline outputs match the dashboard-level metrics.

# In[12]:


gold_kpi_summary = spark.table("gold_kpi_summary")

display(gold_kpi_summary)

expected_metrics = [
    "Total Admissions",
    "High-Risk Admissions",
    "High Risk Rate",
    "Treatment Mismatch Rate",
    "High-Risk Alignment Rate",
    "High-Risk Delayed Admission Rate"
]


# In[2]:


gold_employment_treatment_mix = spark.table("gold_employment_treatment_mix")


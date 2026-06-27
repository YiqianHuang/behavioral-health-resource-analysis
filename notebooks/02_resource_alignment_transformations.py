#!/usr/bin/env python
# coding: utf-8

# ## Resource_alignment_transformation_nb
# 
# New notebook

# ## 1. Load Bronze N-SUMHSS Facility Table
# 
# Read the raw N-SUMHSS facility-level Bronze table created by the ingestion notebook.

# In[1]:


from pyspark.sql import functions as F

bronze_nsumhss_df = spark.table("bronze_nsumhss_facilities_2023")


# ## 2. Create Helper Function for Numeric Fields
# 
# Convert numeric-looking string fields into integers while treating coded missing values such as `M`, `L`, or other non-numeric values as null.

# In[2]:


def numeric_col(col_name):
    return F.when(
        F.col(col_name).rlike("^[0-9]+$"),
        F.col(col_name).cast("int")
    ).otherwise(F.lit(None))


# ## 3. Build Silver N-SUMHSS Facility Table
# 
# Select the facility, state, treatment setting, service availability, client count, and bed count fields needed for state-level resource capacity analysis.
# 
# This Silver table translates selected coded facility fields into analysis-ready indicators.

# In[3]:


silver_nsumhss_df = (
    bronze_nsumhss_df
    .select(
        "MPRID",
        "LOCATIONSTATE",
        "TREATMT_SU",
        "TREATMT_MH",
        "DETOX",
        "SETTINGIP",
        "SETTINGRC",
        "SETTINGOP",
        "IPTOTAL",
        "RCTOTAL",
        "OPTOTAL",
        "IPBEDS",
        "RCBEDS"
    )
    .withColumnRenamed("LOCATIONSTATE", "State")
    .withColumn("Inpatient_Clients", numeric_col("IPTOTAL"))
    .withColumn("Residential_Clients", numeric_col("RCTOTAL"))
    .withColumn("Outpatient_Clients", numeric_col("OPTOTAL"))
    .withColumn("Inpatient_Beds", numeric_col("IPBEDS"))
    .withColumn("Residential_Beds", numeric_col("RCBEDS"))
    .withColumn("Offers_SU_Treatment", F.when(F.col("TREATMT_SU") == 1, 1).otherwise(0))
    .withColumn("Offers_MH_Treatment", F.when(F.col("TREATMT_MH") == 1, 1).otherwise(0))
    .withColumn("Offers_Detox", F.when(F.col("DETOX") == 1, 1).otherwise(0))
    .withColumn("Offers_Inpatient", F.when(F.col("SETTINGIP") == 1, 1).otherwise(0))
    .withColumn("Offers_Residential", F.when(F.col("SETTINGRC") == 1, 1).otherwise(0))
    .withColumn("Offers_Outpatient", F.when(F.col("SETTINGOP") == 1, 1).otherwise(0))
)


# ## 4. Write Silver N-SUMHSS Facility Table
# 
# Persist the cleaned facility-level data as a managed Silver Delta table for reuse in downstream state-level aggregation.

# In[4]:


silver_nsumhss_df.write \
    .mode("overwrite") \
    .format("delta") \
    .saveAsTable("silver_nsumhss_facilities_cleaned")


# ## 5. Build Gold State Resource Capacity Table
# 
# Aggregate facility-level service availability, client counts, and bed counts to the state level.
# 
# This Gold table represents the behavioral health service supply side of the analysis.

# In[5]:


silver_nsumhss_df = spark.table("silver_nsumhss_facilities_cleaned")

gold_state_resource_capacity = (
    silver_nsumhss_df
    .groupBy("State")
    .agg(
        F.countDistinct("MPRID").alias("Facility_Count"),
        F.sum("Offers_SU_Treatment").alias("SU_Treatment_Facility_Count"),
        F.sum("Offers_MH_Treatment").alias("MH_Treatment_Facility_Count"),
        F.sum("Offers_Detox").alias("Detox_Facility_Count"),
        F.sum("Offers_Inpatient").alias("Inpatient_Facility_Count"),
        F.sum("Offers_Residential").alias("Residential_Facility_Count"),
        F.sum("Offers_Outpatient").alias("Outpatient_Facility_Count"),
        F.sum("Inpatient_Clients").alias("Inpatient_Clients"),
        F.sum("Residential_Clients").alias("Residential_Clients"),
        F.sum("Outpatient_Clients").alias("Outpatient_Clients"),
        F.sum("Inpatient_Beds").alias("Inpatient_Beds"),
        F.sum("Residential_Beds").alias("Residential_Beds")
    )
)


# ## 6. Write Gold State Resource Capacity Table
# 
# Persist the state-level resource capacity table for semantic modeling and future integration with TEDS-A admission risk metrics.

# In[6]:


gold_state_resource_capacity.write \
    .mode("overwrite") \
    .format("delta") \
    .saveAsTable("gold_state_resource_capacity")


# ## 7. Validate Gold Resource Capacity Output
# 
# Preview the state-level Gold table to confirm that facility counts and service capacity metrics were generated successfully.

# In[7]:


display(gold_state_resource_capacity)


# ## 8. Build Gold State Admission Risk Table
# 
# Aggregate TEDS-A admissions to the state level and calculate high-risk admission burden, low-intensity placement, and delayed admission exposure.

# In[1]:


from pyspark.sql import functions as F

silver_teds_df = spark.table("silver_tedsa_admissions_cleaned")

state_map_data = [
    (1, "AL"), (2, "AK"), (4, "AZ"), (5, "AR"), (6, "CA"), (8, "CO"),
    (9, "CT"), (10, "DE"), (11, "DC"), (12, "FL"), (13, "GA"), (15, "HI"),
    (16, "ID"), (17, "IL"), (18, "IN"), (19, "IA"), (20, "KS"), (21, "KY"),
    (22, "LA"), (23, "ME"), (24, "MD"), (25, "MA"), (26, "MI"), (27, "MN"),
    (28, "MS"), (29, "MO"), (30, "MT"), (31, "NE"), (32, "NV"), (33, "NH"),
    (34, "NJ"), (35, "NM"), (36, "NY"), (37, "NC"), (38, "ND"), (39, "OH"),
    (40, "OK"), (41, "OR"), (42, "PA"), (44, "RI"), (45, "SC"), (46, "SD"),
    (47, "TN"), (48, "TX"), (49, "UT"), (50, "VT"), (51, "VA"), (53, "WA"),
    (54, "WV"), (55, "WI"), (56, "WY"), (72, "PR")
]

dim_state_df = spark.createDataFrame(state_map_data, ["STFIPS", "State"])

gold_state_admission_risk = (
    silver_teds_df
    .join(dim_state_df, on="STFIPS", how="left")
    .groupBy("State")
    .agg(
        F.countDistinct("CASEID").alias("Total_Admissions"),
        F.countDistinct(
            F.when(F.col("Risk_Profile") == "High Risk", F.col("CASEID"))
        ).alias("High_Risk_Admissions"),
        F.countDistinct(
            F.when(
                (F.col("Risk_Profile") == "High Risk") &
                (F.col("Treatment_Intensity") == "Low Intensity"),
                F.col("CASEID")
            )
        ).alias("High_Risk_Low_Intensity_Admissions"),
        F.countDistinct(
            F.when(
                (F.col("Risk_Profile") == "High Risk") &
                (F.col("DAYWAIT").isin(2, 3, 4)),
                F.col("CASEID")
            )
        ).alias("High_Risk_Delayed_Admissions")
    )
    .withColumn("High_Risk_Rate", F.col("High_Risk_Admissions") / F.col("Total_Admissions"))
    .withColumn("Treatment_Mismatch_Rate", F.col("High_Risk_Low_Intensity_Admissions") / F.col("High_Risk_Admissions"))
    .withColumn("High_Risk_Delayed_Admission_Rate", F.col("High_Risk_Delayed_Admissions") / F.col("High_Risk_Admissions"))
)


# ## 9. Write Gold State Admission Risk Table
# 
# Persist the state-level admission risk metrics as a Gold Delta table for downstream resource alignment analysis.

# In[2]:


gold_state_admission_risk.write \
    .mode("overwrite") \
    .format("delta") \
    .saveAsTable("gold_state_admission_risk")


# ## 10. Build Gold State Resource Alignment Table
# 
# Join state-level admission risk burden with state-level facility resource capacity to create the final multi-source analytical output.

# In[3]:


admission_risk_df = spark.table("gold_state_admission_risk")
resource_capacity_df = spark.table("gold_state_resource_capacity")

gold_state_resource_alignment = (
    admission_risk_df
    .join(resource_capacity_df, on="State", how="left")
    .withColumn(
        "High_Risk_Admissions_Per_Facility",
        F.col("High_Risk_Admissions") / F.when(F.col("Facility_Count") > 0, F.col("Facility_Count"))
    )
    .withColumn(
        "High_Risk_Admissions_Per_Residential_Facility",
        F.col("High_Risk_Admissions") / F.when(F.col("Residential_Facility_Count") > 0, F.col("Residential_Facility_Count"))
    )
    .withColumn(
        "High_Risk_Low_Intensity_Admissions_Per_Outpatient_Facility",
        F.col("High_Risk_Low_Intensity_Admissions") / F.when(F.col("Outpatient_Facility_Count") > 0, F.col("Outpatient_Facility_Count"))
    )
)


(
    gold_state_resource_alignment.write
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .format("delta")
    .saveAsTable("gold_state_resource_alignment")
)


# ## 11. Add Priority Quadrant Classification
# 
# Classify each state into a resource planning quadrant based on high-risk admission burden and facility capacity. This turns the state-level Gold table into a decision-ready prioritization layer.

# In[3]:


from pyspark.sql import functions as F

# Compute average high-risk admissions and facility count across all states
avg_admissions = gold_state_resource_alignment.select(
    F.avg("High_Risk_Admissions")
).collect()[0][0]

avg_facilities = gold_state_resource_alignment.select(
    F.avg("Facility_Count")
).collect()[0][0]

# Add the Priority_Quadrant classification based on those averages
gold_state_resource_priority = (
    gold_state_resource_alignment
    .withColumn(
        "Priority_Quadrant",
        F.when(
            (F.col("High_Risk_Admissions") >= avg_admissions) &
            (F.col("Facility_Count") < avg_facilities),
            "Expansion Priority"
        )
        .when(
            (F.col("High_Risk_Admissions") >= avg_admissions) &
            (F.col("Facility_Count") >= avg_facilities),
            "Optimization Zone"
        )
        .when(
            (F.col("High_Risk_Admissions") < avg_admissions) &
            (F.col("Facility_Count") < avg_facilities),
            "Low Priority"
        )
        .otherwise("Resource Rich")
    )
)


# ## 12. Write Gold State Resource Priority Table
# 
# Persist the final joined Gold table with resource pressure indicators and priority quadrant classification for semantic modeling, reporting, and portfolio documentation.

# In[2]:


(
    gold_state_resource_priority.write
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .format("delta")
    .saveAsTable("gold_state_resource_priority")
)


# ## 13. Validate Final Gold Output
# 
# Preview the final state-level resource alignment table to confirm that admission risk metrics and facility capacity metrics were successfully joined.

# In[3]:


display(spark.table("gold_state_resource_priority"))

#!/usr/bin/env python
# coding: utf-8

# # Bronze Ingestion
#
# This notebook loads the raw public-use CSV files from Fabric Lakehouse Files and writes them as managed Bronze Delta tables.
# Raw CSV files are not stored in GitHub; they should be uploaded to the Lakehouse Files area before running this notebook.

# ## 1. Configure Source Files and Bronze Table Names

# In[ ]:


TEDSA_SOURCE_PATH = "Files/tedsa_puf_2023.csv"
NSUMHSS_SOURCE_PATH = "Files/nsumhss_facilities_2023.csv"

TEDSA_BRONZE_TABLE = "bronze_tedsa_admissions_2023"
NSUMHSS_BRONZE_TABLE = "bronze_nsumhss_facilities_2023"


# ## 2. Define Reusable CSV Loader and Column Check

# In[ ]:


from pyspark.sql import functions as F


def read_public_use_csv(source_path):
    return (
        spark.read
        .format("csv")
        .option("header", "true")
        .option("inferSchema", "true")
        .option("quote", '"')
        .option("escape", '"')
        .load(source_path)
    )


def assert_required_columns(df, required_columns, dataset_name):
    missing_columns = [column for column in required_columns if column not in df.columns]
    if missing_columns:
        raise ValueError(
            f"{dataset_name} is missing required columns: {', '.join(missing_columns)}"
        )


# ## 3. Ingest TEDS-A Admissions to Bronze
#
# This step preserves the raw admissions file as a managed Bronze Delta table.

# In[ ]:


tedsa_required_columns = [
    "CASEID",
    "STFIPS",
    "SERVICES",
    "EMPLOY",
    "PSYPROB",
    "SEX",
    "DAYWAIT",
    "AGE",
    "RACE",
]

tedsa_bronze_df = read_public_use_csv(TEDSA_SOURCE_PATH)
assert_required_columns(tedsa_bronze_df, tedsa_required_columns, "TEDS-A admissions")

(
    tedsa_bronze_df.write
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .format("delta")
    .saveAsTable(TEDSA_BRONZE_TABLE)
)

tedsa_row_count = spark.table(TEDSA_BRONZE_TABLE).count()
print(f"{TEDSA_BRONZE_TABLE} row count: {tedsa_row_count:,}")

display(spark.table(TEDSA_BRONZE_TABLE).limit(10))


# ## 4. Ingest N-SUMHSS Facilities to Bronze
#
# This step preserves the raw facility file as a managed Bronze Delta table.

# In[ ]:


nsumhss_required_columns = [
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
    "RCBEDS",
]

nsumhss_bronze_df = read_public_use_csv(NSUMHSS_SOURCE_PATH)
assert_required_columns(nsumhss_bronze_df, nsumhss_required_columns, "N-SUMHSS facilities")

(
    nsumhss_bronze_df.write
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .format("delta")
    .saveAsTable(NSUMHSS_BRONZE_TABLE)
)

nsumhss_row_count = spark.table(NSUMHSS_BRONZE_TABLE).count()
print(f"{NSUMHSS_BRONZE_TABLE} row count: {nsumhss_row_count:,}")

display(spark.table(NSUMHSS_BRONZE_TABLE).limit(10))


# ## 5. Bronze Ingestion Summary

# In[ ]:


bronze_summary = spark.createDataFrame(
    [
        ("TEDS-A admissions", TEDSA_SOURCE_PATH, TEDSA_BRONZE_TABLE, tedsa_row_count),
        ("N-SUMHSS facilities", NSUMHSS_SOURCE_PATH, NSUMHSS_BRONZE_TABLE, nsumhss_row_count),
    ],
    ["Dataset", "Source_File", "Bronze_Table", "Row_Count"]
)

display(bronze_summary)

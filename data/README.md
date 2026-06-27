# Data

Raw data files are not stored in this repository due to file size and reproducibility considerations.

This project uses public-use datasets from the SAMHSA data portal:

- Treatment Episode Data Set - Admissions (TEDS-A) 2023
- National Substance Use and Mental Health Services Survey (N-SUMHSS) 2023

Download source:

https://www.samhsa.gov/data/data-we-collect

## Expected Raw Files

The Microsoft Fabric pipeline expects the raw files to be uploaded into the Lakehouse Files area before ingestion.

Example source files:

```text
tedsa_puf_2023.csv
nsumhss_facilities_2023.csv
```

## Why Raw Files Are Excluded

The raw CSV files are excluded from GitHub because they are large public-use files that can be downloaded directly from SAMHSA.

Keeping the repository focused on notebooks, documentation, screenshots, and pipeline logic makes the project easier to review and clone.

## Reproducibility Notes

To reproduce the analysis:

1. Download the 2023 TEDS-A and N-SUMHSS public-use files from SAMHSA.
2. Upload the source CSV files to the Fabric Lakehouse Files area.
3. Run `notebooks/00_bronze_ingestion.ipynb` to create Bronze Delta tables from the raw CSV files.
4. Run `notebooks/01_admission_transformations.ipynb` and `notebooks/02_resource_alignment_transformations.ipynb` to rebuild Silver and Gold tables.
5. Run `notebooks/03_statistical_validation_sensitivity_analysis.ipynb` after the Silver table has been created.

The analysis depends on public administrative data and should be interpreted as descriptive operational analytics, not clinical diagnosis or causal inference.

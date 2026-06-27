-- SQL Analytics Endpoint Views
-- Run these statements in the Fabric Lakehouse SQL Analytics Endpoint.

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


-- Validation query: employment access friction view
SELECT *
FROM dbo.vw_employment_access_friction
ORDER BY Employment_Sort_Order, Treatment_Intensity_Sort_Order;


-- Validation query: state resource priority view
SELECT *
FROM dbo.vw_state_resource_priority
WHERE Priority_Quadrant = 'Expansion Priority'
ORDER BY High_Risk_Admissions_Per_Facility DESC;

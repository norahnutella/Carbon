-- =========================================================
-- CARBON EMISSION TRACKING
-- REPORT QUERIES
-- =========================================================


-- =========================================================
-- REPORT 1: TOTAL INSTITUTIONAL EMISSIONS
-- =========================================================

SELECT
    NVL(SUM(Emission_CO2), 0) AS Total_CO2_Emission
FROM Emission_Record;


-- =========================================================
-- REPORT 2: DEPARTMENT-WISE EMISSIONS
-- =========================================================

SELECT
    d.Dept_ID,
    d.Dept_Name,
    SUM(e.Emission_CO2) AS Total_CO2_Emission
FROM Department d
JOIN Emission_Record e
    ON d.Dept_ID = e.Dept_ID
GROUP BY
    d.Dept_ID,
    d.Dept_Name
ORDER BY
    Total_CO2_Emission DESC;


-- =========================================================
-- REPORT 3: ENERGY VS TRANSPORT VS WASTE
-- =========================================================

SELECT
    Activity_Type,
    SUM(Emission_CO2) AS Total_CO2_Emission
FROM Emission_Record
GROUP BY Activity_Type
ORDER BY
    Total_CO2_Emission DESC;


-- =========================================================
-- REPORT 4: HIGHEST-EMISSION DEPARTMENT
-- =========================================================

SELECT
    d.Dept_ID,
    d.Dept_Name,
    SUM(e.Emission_CO2) AS Total_CO2_Emission
FROM Department d
JOIN Emission_Record e
    ON d.Dept_ID = e.Dept_ID
GROUP BY
    d.Dept_ID,
    d.Dept_Name
ORDER BY
    Total_CO2_Emission DESC
FETCH FIRST 1 ROW ONLY;


-- =========================================================
-- REPORT 5: TOP 3 HIGHEST-EMISSION DEPARTMENTS
-- =========================================================

SELECT
    d.Dept_ID,
    d.Dept_Name,
    SUM(e.Emission_CO2) AS Total_CO2_Emission
FROM Department d
JOIN Emission_Record e
    ON d.Dept_ID = e.Dept_ID
GROUP BY
    d.Dept_ID,
    d.Dept_Name
ORDER BY
    Total_CO2_Emission DESC
FETCH FIRST 3 ROWS ONLY;


-- =========================================================
-- REPORT 6: DETAILED EMISSION REPORT
-- =========================================================

SELECT
    e.Record_ID,
    d.Dept_Name,
    e.Activity_Type,
    e.Activity_ID,
    e.Quantity,
    f.Factor_Value,
    f.Unit AS Factor_Unit,
    e.Emission_CO2,
    e.Record_Date
FROM Emission_Record e
JOIN Department d
    ON e.Dept_ID = d.Dept_ID
JOIN Emission_Factor f
    ON e.Factor_ID = f.Factor_ID
ORDER BY
    e.Record_Date;


-- =========================================================
-- REPORT 7: INSTITUTION-WISE EMISSIONS
-- =========================================================

SELECT
    i.Institution_ID,
    i.Name AS Institution_Name,
    SUM(e.Emission_CO2) AS Total_CO2_Emission
FROM Institution i
JOIN Department d
    ON i.Institution_ID = d.Institution_ID
JOIN Emission_Record e
    ON d.Dept_ID = e.Dept_ID
GROUP BY
    i.Institution_ID,
    i.Name
ORDER BY
    Total_CO2_Emission DESC;
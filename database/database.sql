-- =========================================================
-- CARBON EMISSION TRACKING FOR INSTITUTIONS
-- DATABASE CREATION SCRIPT
-- =========================================================

-- =========================================================
-- 1. INSTITUTION TABLE
-- =========================================================

CREATE TABLE Institution (
    Institution_ID NUMBER PRIMARY KEY,
    Name VARCHAR2(100) NOT NULL,
    Type VARCHAR2(50),
    Address VARCHAR2(200),
    Contact_No VARCHAR2(20),
    Established_Year NUMBER(4)
);


-- =========================================================
-- 2. DEPARTMENT TABLE
-- =========================================================

CREATE TABLE Department (
    Dept_ID NUMBER PRIMARY KEY,
    Institution_ID NUMBER NOT NULL,
    Dept_Name VARCHAR2(100) NOT NULL,
    Location VARCHAR2(100),
    Head VARCHAR2(100),

    CONSTRAINT fk_dept_institution
        FOREIGN KEY (Institution_ID)
        REFERENCES Institution(Institution_ID)
);


-- =========================================================
-- 3. ENERGY CONSUMPTION TABLE
-- =========================================================

CREATE TABLE Energy_Consumption (
    Energy_ID NUMBER PRIMARY KEY,
    Dept_ID NUMBER NOT NULL,
    Date_Consumed DATE NOT NULL,
    Energy_Type VARCHAR2(50) NOT NULL,
    Quantity NUMBER(10,2) NOT NULL,
    Unit VARCHAR2(20),
    Emission_CO2 NUMBER(12,2),

    CONSTRAINT fk_energy_dept
        FOREIGN KEY (Dept_ID)
        REFERENCES Department(Dept_ID)
);


-- =========================================================
-- 4. TRANSPORT TABLE
-- =========================================================

CREATE TABLE Transport (
    Transport_ID NUMBER PRIMARY KEY,
    Dept_ID NUMBER NOT NULL,
    Date_Travelled DATE NOT NULL,
    Transport_Mode VARCHAR2(50),
    Distance_km NUMBER(10,2),
    Fuel_Type VARCHAR2(50),
    Fuel_Quantity NUMBER(10,2),
    Emission_CO2 NUMBER(12,2),

    CONSTRAINT fk_transport_dept
        FOREIGN KEY (Dept_ID)
        REFERENCES Department(Dept_ID)
);


-- =========================================================
-- 5. WASTE TABLE
-- =========================================================

CREATE TABLE Waste (
    Waste_ID NUMBER PRIMARY KEY,
    Dept_ID NUMBER NOT NULL,
    Date_Generated DATE NOT NULL,
    Waste_Type VARCHAR2(50),
    Quantity NUMBER(10,2),
    Unit VARCHAR2(20),
    Disposal_Method VARCHAR2(100),
    Emission_CO2 NUMBER(12,2),

    CONSTRAINT fk_waste_dept
        FOREIGN KEY (Dept_ID)
        REFERENCES Department(Dept_ID)
);


-- =========================================================
-- 6. EMISSION FACTOR TABLE
-- =========================================================

CREATE TABLE Emission_Factor (
    Factor_ID NUMBER PRIMARY KEY,
    Activity_Type VARCHAR2(30) NOT NULL,
    Factor_Value NUMBER(12,4) NOT NULL,
    Unit VARCHAR2(50),
    Description VARCHAR2(200)
);


-- =========================================================
-- 7. EMISSION RECORD TABLE
-- =========================================================

CREATE TABLE Emission_Record (
    Record_ID NUMBER PRIMARY KEY,
    Dept_ID NUMBER NOT NULL,
    Factor_ID NUMBER NOT NULL,
    Activity_Type VARCHAR2(30),
    Activity_ID NUMBER,
    Record_Date DATE,
    Quantity NUMBER(12,2),
    Emission_CO2 NUMBER(12,2),

    CONSTRAINT fk_record_dept
        FOREIGN KEY (Dept_ID)
        REFERENCES Department(Dept_ID),

    CONSTRAINT fk_record_factor
        FOREIGN KEY (Factor_ID)
        REFERENCES Emission_Factor(Factor_ID)
);


-- =========================================================
-- CHECK TABLES
-- =========================================================

SELECT TABLE_NAME
FROM USER_TABLES
ORDER BY TABLE_NAME;
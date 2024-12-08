select * from  Loan_Fact;
select * from   dim_bank_data;
select * from stg_loan_data;
select * from   dim_geography_data;
select * from   dim_LoanDetails_Dimension;
select * from   dim_borrower_data;








---
SELECT 
    LoanNr_ChkDgt, 
    COUNT(*) AS occurrence_count
FROM 
    dim_borrower_data
GROUP BY 
    LoanNr_ChkDgt
HAVING 
    COUNT(*) > 1;


	------


--1 .Total Loan Amount Disbursed by Geography


SELECT 
    g.City,
    g.State,
    SUM(CAST(REPLACE(REPLACE(f.DisbursementGross, '$', ''), ',', '') AS DECIMAL(18,2))) AS TotalLoanDisbursed
FROM 
    Loan_Fact f
JOIN 
    dim_geography_data g ON f.Geography_ID = g.Geography_ID
WHERE 
    ISNUMERIC(REPLACE(REPLACE(f.DisbursementGross, '$', ''), ',', '')) = 1
GROUP BY 
    g.City, g.State
ORDER BY 
    TotalLoanDisbursed DESC;

--2.Validation of Active Loans
SELECT 
    b.name,
    l.LoanNr_ChkDgt
    
FROM 
    Loan_Fact f
JOIN 
    dim_borrower_data b ON f.Borrower_ID = b.Borrower_ID
JOIN 
    dim_LoanDetails_Dimension l ON f.LoanDetails_ID = l.LoanDetails_ID
WHERE 
    f.ChgOffDate IS NULL AND b.active_Flag = 'Y';

--3.Number of Loans Approved by Year
SELECT 
    l.ApprovalFY AS ApprovalYear,
    COUNT(l.LoanNr_ChkDgt) AS LoanCount
FROM 
    dim_LoanDetails_Dimension l
GROUP BY 
    l.ApprovalFY
ORDER BY 
    ApprovalYear;

--4.Top Borrowers Based on Disbursed Loan Amount
SELECT TOP 10
    b.name,
    SUM(CAST(REPLACE(REPLACE(f.DisbursementGross, '$', ''), ',', '') AS DECIMAL(18,2))) AS TotalDisbursement
FROM 
    Loan_Fact f
JOIN 
    dim_borrower_data b ON f.Borrower_ID = b.Borrower_ID
GROUP BY 
    b.name
ORDER BY 
    TotalDisbursement DESC;


--5.Jobs Created or Retained per Business
SELECT 
    bb.Name,
    SUM(bb.CreateJob) AS TotalCreated,
    SUM(bb.RetainedJob) AS TotalRetained,
    SUM(bb.CreateJob + bb.RetainedJob) AS TotalJobs
FROM 
    dim_borrower_data bb
Group BY 
    bb.Name
ORDER BY 
    TotalJobs DESC;


--6.Loans by Urban vs. Rural Areas
SELECT 
    bb.UrbanRural,
    COUNT(f.ID) AS LoanCount, -- Updated column name from Fact_ID to ID
    SUM(CAST(REPLACE(REPLACE(f.DisbursementGross, '$', ''), ',', '') AS DECIMAL(18,2))) AS TotalLoanDisbursed
FROM 
    Loan_Fact f
JOIN 
    dim_borrower_data bb ON f.Borrower_ID = bb.Borrower_ID
GROUP BY 
    bb.UrbanRural
ORDER BY 
    TotalLoanDisbursed DESC;


--7.Loans by Bank and Geography
SELECT 
    bk.Bank,
    g.City,
    g.State,
    COUNT(f.ID) AS LoanCount, -- Renamed Fact_ID to ID
    SUM(CAST(REPLACE(REPLACE(f.DisbursementGross, '$', ''), ',', '') AS DECIMAL(18,2))) AS TotalLoanDisbursed
FROM 
    Loan_Fact f
JOIN 
    dim_bank_data bk ON f.Bank_ID = bk.Bank_ID
JOIN 
    dim_geography_data g ON f.Geography_ID = g.Geography_ID
GROUP BY 
    bk.Bank, g.City, g.State
ORDER BY 
    TotalLoanDisbursed DESC;


--8.Loan Disbursement Trends by Year
SELECT 
    YEAR(f.DisbursementDate) AS LoanYear,
    SUM(CAST(REPLACE(REPLACE(f.DisbursementGross, '$', ''), ',', '') AS DECIMAL(18,2))) AS TotalDisbursed
FROM 
    Loan_Fact f
WHERE 
    f.DisbursementDate IS NOT NULL
GROUP BY 
    YEAR(f.DisbursementDate)
ORDER BY 
    LoanYear;












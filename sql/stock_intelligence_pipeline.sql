USE DATABASE STOCK_INTELLIGENCE_DB;
USE SCHEMA PUBLIC;

/* RAW DATA */
CREATE OR REPLACE TABLE DAILY_STOCK (
    date DATE,
    location STRING,
    item STRING,
    opening_stock INT,
    received INT,
    issued INT,
    closing_stock INT,
    lead_time_days INT,
    criticality STRING
);

/* SAMPLE DATA */
INSERT INTO DAILY_STOCK VALUES
('2025-12-25','Delhi','Paracetamol',500,100,120,480,7,'HIGH'),
('2025-12-26','Delhi','Paracetamol',480,50,150,380,7,'HIGH'),
('2025-12-27','Delhi','Paracetamol',380,0,160,220,7,'HIGH'),
('2025-12-28','Delhi','Paracetamol',220,0,140,80,7,'HIGH'),
('2025-12-25','Mumbai','ORS',300,100,60,340,5,'HIGH'),
('2025-12-26','Mumbai','ORS',340,0,90,250,5,'HIGH'),
('2025-12-27','Mumbai','ORS',250,0,110,140,5,'HIGH'),
('2025-12-28','Mumbai','ORS',140,0,120,20,5,'HIGH');

/* CONSUMPTION TRENDS */
CREATE OR REPLACE VIEW STOCK_CONSUMPTION_TRENDS AS
SELECT
    location,
    item,
    date,
    issued,
    AVG(issued) OVER (
        PARTITION BY location, item
        ORDER BY date
        ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
    ) AS avg_daily_issue,
    closing_stock,
    lead_time_days,
    criticality
FROM DAILY_STOCK;

/* STOCK-OUT ESTIMATION */
CREATE OR REPLACE VIEW STOCK_OUT_ESTIMATION AS
SELECT
    *,
    ROUND(closing_stock / NULLIF(avg_daily_issue,0),1) AS days_of_stock_left
FROM STOCK_CONSUMPTION_TRENDS;

/* RISK CLASSIFICATION */
CREATE OR REPLACE VIEW STOCK_RISK_CLASSIFICATION AS
SELECT *,
    CASE
        WHEN days_of_stock_left < 3 THEN 'HIGH'
        WHEN days_of_stock_left BETWEEN 3 AND 7 THEN 'MEDIUM'
        ELSE 'LOW'
    END AS stock_risk_level
FROM STOCK_OUT_ESTIMATION;

/* REORDER RECOMMENDATION */
CREATE OR REPLACE VIEW STOCK_REORDER_RECOMMENDATIONS AS
SELECT *,
    ROUND(avg_daily_issue * (lead_time_days + 2),0) AS recommended_reorder_qty
FROM STOCK_RISK_CLASSIFICATION
WHERE stock_risk_level IN ('HIGH','MEDIUM');

/* DYNAMIC TABLE */
CREATE OR REPLACE DYNAMIC TABLE DT_STOCK_INTELLIGENCE
TARGET_LAG = '1 day'
WAREHOUSE = COMPUTE_WH
AS
SELECT * FROM STOCK_REORDER_RECOMMENDATIONS;

/* ALERT LOG */
CREATE OR REPLACE TABLE STOCK_ALERT_LOG (
    alert_date DATE,
    location STRING,
    item STRING,
    stock_risk_level STRING,
    days_of_stock_left NUMBER(5,1),
    recommended_reorder_qty NUMBER,
    alert_status STRING,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

/* ALERT TASK */
CREATE OR REPLACE TASK TASK_LOG_HIGH_RISK_ALERTS
WAREHOUSE = COMPUTE_WH
AS
INSERT INTO STOCK_ALERT_LOG
SELECT
    CURRENT_DATE,
    location,
    item,
    stock_risk_level,
    days_of_stock_left,
    recommended_reorder_qty,
    'NEW'
FROM DT_STOCK_INTELLIGENCE
WHERE stock_risk_level='HIGH';

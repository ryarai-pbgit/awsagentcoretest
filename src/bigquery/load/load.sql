-- データロード overdue.csv.gz
LOAD DATA OVERWRITE mydataset.OVERDUE_TABLE
(USERID STRING)
FROM FILES (
  format = 'CSV',
  uris = ['gs://mydata202510252051/overdue.csv.gz']);
-- ロード結果確認 overdue.csv.gz
SELECT * FROM `ryarai-mygcp.mydataset.OVERDUE_TABLE`;

-- ロード結果確認 customer.csv.gz
LOAD DATA OVERWRITE `mydataset.CUSTOMER_DATA`
(USERID STRING,
 AGE STRING,
 GENDER STRING,
 AREA STRING,
 JOB STRING,
 INCOME STRING,
 EDUCATION STRING,
 FAMILY STRING,
 INTEREST STRING,
 DEVICE STRING)
FROM FILES (
  format = 'CSV',
  uris = ['gs://mydata202510252051/customer.csv.gz']
);
-- ロード結果確認 customer.csv.gz
SELECT count(*) FROM `ryarai-mygcp.mydataset.TRANSACTION_DATA`;

-- データロード data_0_0_0 (2).csv.gz他
LOAD DATA OVERWRITE `mydataset.TRANSACTION_DATA`
(USERID STRING,
 DATE DATE,
 CATEGORY STRING,
 UNIT FLOAT64,
 QUANTITY INT64,
 AMOUNT FLOAT64,
 PAYMENT STRING,
 LOCATION STRING)
FROM FILES (
  format = 'CSV',
  uris = ['gs://mydata202510252051/data_0_0_0 (2).csv.gz', 
          'gs://mydata202510252051/data_0_1_0.csv.gz',
          'gs://mydata202510252051/data_0_2_0.csv.gz',
          'gs://mydata202510252051/data_0_3_0.csv.gz',
          'gs://mydata202510252051/data_0_4_0.csv.gz',
          'gs://mydata202510252051/data_0_5_0.csv.gz',
          'gs://mydata202510252051/data_0_6_0.csv.gz',
          'gs://mydata202510252051/data_0_7_0.csv.gz']
);

-- ロード結果確認 data_0_0_0 (2).csv.gz他
SELECT count(*) FROM `ryarai-mygcp.mydataset.TRANSACTION_DATA`;







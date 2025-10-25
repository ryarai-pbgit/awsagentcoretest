CREATE OR REPLACE TABLE `mydataset.CUSTOMER_DATA` (
  USERID STRING,
  AGE STRING,
  GENDER STRING,
  AREA STRING,
  JOB STRING,
  INCOME STRING,
  EDUCATION STRING,
  FAMILY STRING,
  INTEREST STRING,
  DEVICE STRING
)
OPTIONS(
  description="The table contains demographic data about customers. Each record represents a single customer and includes details about their personal characteristics, lifestyle, and interests."
);
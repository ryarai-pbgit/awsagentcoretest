CREATE OR REPLACE TABLE `mydataset.TRANSACTION_DATA` (
  USERID STRING,
  DATE DATE,
  CATEGORY STRING,
  UNIT FLOAT64,
  QUANTITY INT64,
  AMOUNT FLOAT64,
  PAYMENT STRING,
  LOCATION STRING
)
OPTIONS(
  description="The table contains records of financial transactions, specifically sales or purchases, with details about the user, date, category, and financial information. Each record represents a single transaction and includes details about the user, the item purchased or sold, and the location of the transaction."
);

CREATE OR REPLACE TABLE `mydataset.OVERDUE_TABLE` (
  USERID STRING
)
OPTIONS(
  description="The table contains records of overdue items. Each record represents a single item that is past its due date, including details about the user who borrowed it and the item itself."
);
-- データベース指定
USE DATABASE TESTDB;

-- ファイルフォーマット作成
CREATE OR REPLACE FILE FORMAT my_csv_unload_format
  TYPE = 'CSV';

-- ステージの作成
CREATE OR REPLACE STAGE my_unload_stage
  FILE_FORMAT = my_csv_unload_format;

-- unload
COPY INTO @my_unload_stage/transaction_data/ from TRANSACTION_DATA;
COPY INTO @my_unload_stage/customer_data/ from CUSTOMER_DATA;
COPY INTO @my_unload_stage/overdue_table/ from OVERDUE_TABLE;

-- ステージの内容を確認
LIST @my_unload_stage;

-- REMOVE @my_unload_stage/unload/;
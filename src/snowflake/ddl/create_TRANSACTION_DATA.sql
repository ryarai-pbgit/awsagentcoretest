create or replace TABLE TESTDB.PUBLIC.TRANSACTION_DATA (
	USERID VARCHAR(16777216),
	DATE DATE,
	CATEGORY VARCHAR(16777216),
	UNIT NUMBER(38,13),
	QUANTITY NUMBER(38,0),
	AMOUNT NUMBER(38,13),
	PAYMENT VARCHAR(16777216),
	LOCATION VARCHAR(16777216)
)COMMENT='The table contains records of financial transactions, specifically sales or purchases, with details about the user, date, category, and financial information. Each record represents a single transaction and includes details about the user, the item purchased or sold, and the location of the transaction.'
;
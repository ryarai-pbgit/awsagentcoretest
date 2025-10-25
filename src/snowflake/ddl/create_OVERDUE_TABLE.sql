create or replace TABLE TESTDB.PUBLIC.OVERDUE_TABLE (
	USERID VARCHAR(16777216)
)COMMENT='The table contains records of overdue items. Each record represents a single item that is past its due date, including details about the user who borrowed it and the item itself.'
;
## Super easy bot to pay for ztv.su hosting with undetected_chromedriver
Super simple tables for a database:

Storage of checks:
```SQL
CREATE TABLE "paid_checks" (
	"user_id"	INTEGER,
	"username"	TEXT,
	"date"	TEXT,
	"amount"	REAL
);
```
Users:
```SQL
CREATE TABLE "payments" (
	"user_id"	INTEGER UNIQUE
);
```
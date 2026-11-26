-- Optional: create a NEW dedicated database, never overwrite an existing one.
USE master;
GO
IF DB_ID(N'TicketingDB') IS NOT NULL
 THROW 50000, 'TicketingDB already exists. Review it before proceeding.', 1;
CREATE DATABASE TicketingDB;
GO

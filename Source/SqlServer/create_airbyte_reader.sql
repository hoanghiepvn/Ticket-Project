-- Run intentionally in SSMS as an authorized administrator.
-- Replace password locally; this file is NOT executed by Docker or scripts.
USE [master];
GO
-- Example only; uncomment after choosing a strong password.
-- CREATE LOGIN [ticketing_airbyte] WITH PASSWORD = 'REPLACE_LOCALLY';
-- GO
-- USE [TicketingDB];
-- CREATE USER [ticketing_airbyte] FOR LOGIN [ticketing_airbyte];
-- GRANT SELECT ON OBJECT::dbo.events TO [ticketing_airbyte];
-- GRANT SELECT ON OBJECT::dbo.ticket_types TO [ticketing_airbyte];
-- GRANT SELECT ON OBJECT::dbo.orders TO [ticketing_airbyte];
-- GRANT SELECT ON OBJECT::dbo.order_items TO [ticketing_airbyte];
-- GRANT SELECT ON OBJECT::dbo.payments TO [ticketing_airbyte];
-- No CDC, db_owner, server settings, or firewall changes.

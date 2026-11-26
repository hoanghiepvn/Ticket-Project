-- Replaces the five source tables. Back up TicketingDB before any subsequent use.
-- Run with sqlcmd from this directory after generating all five files in generated.
:ON ERROR EXIT
USE [TicketingDB];
SET XACT_ABORT ON;
SET QUOTED_IDENTIFIER ON;
SET ANSI_NULLS ON;
SET ANSI_PADDING ON;
SET ANSI_WARNINGS ON;
SET ARITHABORT ON;
SET CONCAT_NULL_YIELDS_NULL ON;
SET NUMERIC_ROUNDABORT OFF;
BEGIN TRANSACTION;
DELETE FROM dbo.payments;
DELETE FROM dbo.order_items;
DELETE FROM dbo.orders;
DELETE FROM dbo.ticket_types;
DELETE FROM dbo.events;
GO
:r generated/01_events.sql
:r generated/02_ticket_types.sql
:r generated/03_orders.sql
:r generated/04_order_items.sql
:r generated/05_payments.sql
-- Business verification is user-managed; no automatic test script is invoked.
GO
COMMIT TRANSACTION;
GO

-- SQL Server 2016+; run in the intended EMPTY database. No DROP/DELETE.
SET XACT_ABORT ON;
SET QUOTED_IDENTIFIER ON;
SET ANSI_NULLS ON;
SET ANSI_PADDING ON;
SET ANSI_WARNINGS ON;
SET ARITHABORT ON;
SET CONCAT_NULL_YIELDS_NULL ON;
SET NUMERIC_ROUNDABORT OFF;
BEGIN TRANSACTION;
IF OBJECT_ID('dbo.events') IS NOT NULL OR OBJECT_ID('dbo.ticket_types') IS NOT NULL
 OR OBJECT_ID('dbo.orders') IS NOT NULL OR OBJECT_ID('dbo.order_items') IS NOT NULL
 OR OBJECT_ID('dbo.payments') IS NOT NULL
 THROW 50001, 'Target tables already exist. Use a new empty database.', 1;

CREATE TABLE dbo.events (
 event_id int NOT NULL PRIMARY KEY,
 event_code varchar(30) NOT NULL UNIQUE,
 event_name nvarchar(200) NOT NULL,
 category varchar(30) NOT NULL,
 organizer_name nvarchar(150) NOT NULL,
 venue_name nvarchar(150) NOT NULL,
 province nvarchar(60) NOT NULL,
 capacity int NOT NULL CHECK(capacity > 0),
 starts_at datetime2(0) NOT NULL,
 ends_at datetime2(0) NOT NULL,
 sales_start_at datetime2(0) NOT NULL,
 sales_end_at datetime2(0) NOT NULL,
 event_status varchar(20) NOT NULL CHECK(event_status IN ('ON_SALE','COMPLETED')),
 created_at datetime2(0) NOT NULL,
 updated_at datetime2(0) NOT NULL,
 CHECK(sales_start_at < sales_end_at AND sales_end_at <= starts_at AND starts_at < ends_at),
 CHECK(created_at <= updated_at)
);
CREATE TABLE dbo.ticket_types (
 ticket_type_id int NOT NULL PRIMARY KEY,
 event_id int NOT NULL REFERENCES dbo.events(event_id),
 ticket_type_code varchar(30) NOT NULL,
 ticket_type_name nvarchar(80) NOT NULL,
 list_price decimal(18,0) NOT NULL CHECK(list_price > 0),
 sale_quota int NOT NULL CHECK(sale_quota > 0),
 created_at datetime2(0) NOT NULL,
 updated_at datetime2(0) NOT NULL,
 UNIQUE(event_id,ticket_type_code),
 UNIQUE(ticket_type_id,event_id),
 CHECK(created_at <= updated_at)
);
CREATE TABLE dbo.orders (
 order_id bigint NOT NULL PRIMARY KEY,
 event_id int NOT NULL REFERENCES dbo.events(event_id),
 order_code varchar(30) NOT NULL UNIQUE,
 ordered_at datetime2(0) NOT NULL,
 expires_at datetime2(0) NOT NULL,
 sales_channel varchar(20) NOT NULL CHECK(sales_channel IN ('WEB','APP')),
 order_status varchar(20) NOT NULL CHECK(order_status IN ('PAID','EXPIRED','CANCELLED','PENDING')),
 subtotal_amount decimal(18,0) NOT NULL CHECK(subtotal_amount > 0),
 discount_amount decimal(18,0) NOT NULL CHECK(discount_amount >= 0),
 total_amount decimal(18,0) NOT NULL CHECK(total_amount > 0),
 currency char(3) NOT NULL CHECK(currency = 'VND'),
 created_at datetime2(0) NOT NULL,
 updated_at datetime2(0) NOT NULL,
 UNIQUE(order_id,event_id),
 CHECK(total_amount = subtotal_amount - discount_amount),
 CHECK(ordered_at < expires_at AND created_at <= updated_at)
);
CREATE TABLE dbo.order_items (
 order_item_id bigint NOT NULL PRIMARY KEY,
 order_id bigint NOT NULL,
 event_id int NOT NULL,
 ticket_type_id int NOT NULL,
 quantity int NOT NULL CHECK(quantity BETWEEN 1 AND 6),
 unit_price decimal(18,0) NOT NULL CHECK(unit_price > 0),
 discount_amount decimal(18,0) NOT NULL CHECK(discount_amount >= 0),
 line_amount decimal(18,0) NOT NULL CHECK(line_amount > 0),
 created_at datetime2(0) NOT NULL,
 updated_at datetime2(0) NOT NULL,
 UNIQUE(order_id,ticket_type_id),
 FOREIGN KEY(order_id,event_id) REFERENCES dbo.orders(order_id,event_id),
 FOREIGN KEY(ticket_type_id,event_id) REFERENCES dbo.ticket_types(ticket_type_id,event_id),
 CHECK(line_amount = quantity * unit_price - discount_amount),
 CHECK(created_at <= updated_at)
);
CREATE TABLE dbo.payments (
 payment_id bigint NOT NULL PRIMARY KEY,
 order_id bigint NOT NULL REFERENCES dbo.orders(order_id),
 merchant_transaction_id varchar(40) NOT NULL UNIQUE,
 partner_transaction_id varchar(40) NULL,
 payment_partner varchar(30) NOT NULL,
 payment_method varchar(30) NOT NULL CHECK(payment_method IN ('WALLET','DOMESTIC_CARD','QR_BANK')),
 payment_amount decimal(18,0) NOT NULL CHECK(payment_amount > 0),
 currency char(3) NOT NULL CHECK(currency = 'VND'),
 payment_status varchar(20) NOT NULL CHECK(payment_status IN ('SUCCESS','FAILED','PENDING')),
 failure_reason varchar(40) NULL,
 initiated_at datetime2(0) NOT NULL,
 completed_at datetime2(0) NULL,
 paid_at datetime2(0) NULL,
 created_at datetime2(0) NOT NULL,
 updated_at datetime2(0) NOT NULL,
 CHECK((payment_status = 'SUCCESS' AND paid_at IS NOT NULL AND failure_reason IS NULL)
 OR (payment_status <> 'SUCCESS' AND paid_at IS NULL)),
 CHECK((payment_status = 'PENDING' AND completed_at IS NULL)
 OR (payment_status <> 'PENDING' AND completed_at IS NOT NULL)),
 CHECK(completed_at IS NULL OR completed_at >= initiated_at),
 CHECK(paid_at IS NULL OR paid_at = completed_at),
 CHECK(created_at <= updated_at)
);
CREATE UNIQUE INDEX ux_payment_success ON dbo.payments(order_id) WHERE payment_status='SUCCESS';
CREATE UNIQUE INDEX ux_partner_reference ON dbo.payments(payment_partner,partner_transaction_id)
 WHERE partner_transaction_id IS NOT NULL;
CREATE INDEX ix_events_updated ON dbo.events(updated_at,event_id);
CREATE INDEX ix_types_updated ON dbo.ticket_types(updated_at,ticket_type_id);
CREATE INDEX ix_orders_updated ON dbo.orders(updated_at,order_id);
CREATE INDEX ix_items_updated ON dbo.order_items(updated_at,order_item_id);
CREATE INDEX ix_payments_updated ON dbo.payments(updated_at,payment_id);
CREATE INDEX ix_items_ticket ON dbo.order_items(ticket_type_id);
CREATE INDEX ix_payments_reconcile ON dbo.payments(payment_partner,paid_at) INCLUDE(merchant_transaction_id,payment_amount,payment_status);
COMMIT;

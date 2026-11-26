-- PostgreSQL published Gold; use the read-only powerbi_reader account.
SET search_path TO gold;
SELECT SUM(sales_amount) AS paid_ticket_value_vnd,
       SUM(sold_quantity) AS sold_tickets,
       COUNT(DISTINCT CASE WHEN status_key=1 THEN order_id END) AS paid_orders
FROM fact_ticket_sales;

SELECT e.event_name, SUM(f.sales_amount) AS sales_amount,
       SUM(f.sold_quantity) AS sold_quantity
FROM fact_ticket_sales f JOIN dim_event e ON e.event_id=f.event_id
GROUP BY e.event_name ORDER BY sales_amount DESC;

-- Never SUM(orders.total_amount) after joining orders -> order_items -> payments.
-- Never SUM(dim_event.capacity) across fact rows.

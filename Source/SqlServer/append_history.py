"""Append reproducible historical batches to TicketingDB; existing rows are preserved.

Generate only by default. --load writes all five related tables atomically per year.
Requires pyodbc and Microsoft ODBC Driver 17/18 for SQL Server.
"""
import argparse
from collections import Counter
from datetime import datetime
import json
from pathlib import Path
import re

from events import TABLES, build_dataset

KEYS = dict(events="event_id", ticket_types="ticket_type_id", orders="order_id",
            order_items="order_item_id", payments="payment_id")
REFERENCES = dict(event_id="events", ticket_type_id="ticket_types", order_id="orders",
                  order_item_id="order_items", payment_id="payments")
DEFAULT_COUNTS = {2020: 40000, 2021: 20000, 2022: 30000, 2023: 40000, 2024: 55000, 2025: 70000}


def load_batch(data, year, seed, server, database):
    import pyodbc
    driver = next((d for d in reversed(pyodbc.drivers())
                   if d in ("ODBC Driver 18 for SQL Server", "ODBC Driver 17 for SQL Server")), None)
    if not driver:
        raise RuntimeError("Microsoft ODBC Driver 17/18 is required.")
    prefix = f"H{year}S{seed}"
    connection = pyodbc.connect(
        f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};"
        "Trusted_Connection=yes;Encrypt=yes;TrustServerCertificate=yes",
        autocommit=False, timeout=15,
    )
    try:
        cursor = connection.cursor()
        cursor.execute("SET XACT_ABORT ON; SET LOCK_TIMEOUT 60000;")
        cursor.execute("""
            DECLARE @result int;
            EXEC @result = sys.sp_getapplock @Resource='ticketing_history_append',
                @LockMode='Exclusive', @LockOwner='Transaction', @LockTimeout=60000;
            IF @result < 0 THROW 51000, 'Could not lock history import.', 1;
        """)
        # Lock targets until commit: no concurrent importer can allocate the same keys.
        offsets = {}
        for table in TABLES:
            cursor.execute(f"SELECT COALESCE(MAX([{KEYS[table]}]),0) "
                           f"FROM dbo.[{table}] WITH (TABLOCKX,HOLDLOCK)")
            offsets[table] = int(cursor.fetchone()[0])
        cursor.execute("SELECT COUNT(*) FROM dbo.events WHERE event_code LIKE ?", prefix+"E%")
        existing = cursor.fetchone()[0]
        if existing:
            cursor.execute("SELECT COUNT_BIG(*) FROM dbo.orders WHERE order_code LIKE ?", prefix+"O%")
            count = cursor.fetchone()[0]
            if existing != len(data["events"]) or count != len(data["orders"]):
                raise RuntimeError("Batch exists with different counts; do not reuse this seed/config.")
            connection.rollback()
            return {"status": "already_loaded", "year": year, "orders": count}

        for table in TABLES:
            columns = list(data[table][0])
            insert = (f"INSERT INTO dbo.[{table}] (" +
                      ",".join(f"[{c}]" for c in columns) + ") VALUES (" +
                      ",".join("?" for _ in columns) + ")")
            cursor.fast_executemany = True
            for start in range(0, len(data[table]), 2000):
                batch = []
                for original in data[table][start:start+2000]:
                    row = dict(original)
                    for field, target in REFERENCES.items():
                        if field in row:
                            row[field] += offsets[target]
                    if table == "events":
                        row["event_code"] = prefix + "E" + str(original["event_id"])
                    elif table == "orders":
                        row["order_code"] = prefix + "O" + str(original["order_id"])
                    elif table == "payments":
                        row["merchant_transaction_id"] = prefix + "T" + str(original["payment_id"])
                        if row["partner_transaction_id"] is not None:
                            row["partner_transaction_id"] = prefix + "P" + str(original["payment_id"])
                    batch.append(tuple(row[c] for c in columns))
                cursor.executemany(insert, batch)
        connection.commit()
        return {"status": "loaded", "year": year, "offsets": offsets,
                "rows": {t: len(data[t]) for t in TABLES}}
    except BaseException:
        connection.rollback()
        raise
    finally:
        connection.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start-year", type=int, default=2020)
    parser.add_argument("--end-year", type=int, default=2025)
    parser.add_argument("--orders-per-year", type=int,
                        help="Override each year's order count; default 40k/20k/30k/40k/55k/70k.")
    parser.add_argument("--seed", type=int, default=20221004)
    parser.add_argument("--server", default="localhost")
    parser.add_argument("--database", default="TicketingDB")
    parser.add_argument("--load", action="store_true")
    parser.add_argument("--output", type=Path, default=Path(__file__).parent/"history_batches")
    args = parser.parse_args()
    if not 2020 <= args.start_year <= args.end_year <= 2025:
        parser.error("Supported completed historical years: 2020 through 2025.")
    if not 0 <= args.seed <= 99999999:
        parser.error("Seed must be between 0 and 99999999.")
    if args.orders_per_year is not None and not 1 <= args.orders_per_year <= 1000000:
        parser.error("orders-per-year must be between 1 and 1000000.")
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", args.database):
        parser.error("Use a simple database name.")
    if any(c in args.server for c in ";{}"):
        parser.error("Invalid server name.")
    args.output.mkdir(parents=True, exist_ok=True)
    for year in range(args.start_year, args.end_year+1):
        count = args.orders_per_year or DEFAULT_COUNTS[year]
        print(f"Generating {year}: {count:,} orders...", flush=True)
        data = build_dataset(count, args.seed+year, year=year)
        summary = {
            "generator": "history-1.0", "synthetic": True,
            "year": year, "seed": args.seed, "orders_requested": count,
            "timezone": "Asia/Ho_Chi_Minh",
            "rows": {t: len(data[t]) for t in TABLES},
            "order_status": dict(Counter(o["order_status"] for o in data["orders"])),
            "orders_by_month": dict(sorted(Counter(o["ordered_at"].strftime("%Y-%m")
                                                   for o in data["orders"]).items())),
            "paid_value_vnd": sum(o["total_amount"] for o in data["orders"] if o["order_status"]=="PAID"),
        }
        summary["load"] = (load_batch(data, year, args.seed, args.server, args.database)
                           if args.load else {"status": "generated_only"})
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        path = args.output / f"{year}_seed{args.seed}_{stamp}.json"
        path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(summary["load"]), flush=True)
        print(f"Manifest: {path}", flush=True)


if __name__ == "__main__":
    main()

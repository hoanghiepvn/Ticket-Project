"""dbt execution for Dataset DAGs. No Airbyte credentials or legacy audit hand-off."""
import hashlib
import logging
from contextlib import closing

from airflow.operators.python import get_current_context

from ticketing.dbt_runner import invoke
from ticketing.model_catalog import MODEL_GROUPS
from ticketing.warehouse import connect

log = logging.getLogger(__name__)


def run_dbt(stage, model=None, execute=None):
    """Publish the task's Dataset outlets only after dbt (and opt-in tests) succeeds."""
    if stage not in MODEL_GROUPS or (model and model not in MODEL_GROUPS[stage]):
        raise ValueError("Unknown dbt stage/model")
    context = get_current_context()
    params = context["params"]
    models = [model] if model else list(MODEL_GROUPS[stage])
    identity = context["dag"].dag_id + ":" + context["run_id"]
    run_id = hashlib.sha256(identity.encode()).hexdigest()[:32]
    full_refresh = params.get("full_refresh", False)
    # Airbyte is Full Refresh Overwrite; old manual configs cannot override this.
    bronze_mode = "full_snapshot"

    # Serialize competing writes to the same model (individual DAG vs manual all).
    # Session locks survive dbt subprocess commits and are released when this closes.
    with closing(connect()) as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("SET statement_timeout = '300s'")
            for name in sorted(models):
                key = int.from_bytes(hashlib.sha256(("dbt:"+name).encode()).digest()[:8],
                                     byteorder="big", signed=True)
                cur.execute("SELECT pg_advisory_lock(%s)", (key,))

            for name in models:
                table = name.removeprefix("silver_") if stage == "silver" else name
                cur.execute(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_schema=%s AND table_name=%s", (stage,table))
                columns = {row[0] for row in cur.fetchall()}
                incremental = stage == "silver" or name == "fact_ticket_sales"
                required = {"_record_hash","_is_deleted","_loaded_at"}
                if incremental and columns and not required.issubset(columns) and not full_refresh:
                    raise RuntimeError(
                        f"{stage}.{table} has the old layout. For first initialization, "
                        "run silver_ticket_all / gold_ticket_all with full_refresh=true "
                        "while individual Dataset DAGs remain paused.")

        log.info("dbt stage=%s model=%s full_refresh=%s", stage, model or "all", full_refresh)
        artifacts = execute() if execute else invoke("run",run_id,stage,full_refresh,bronze_mode,model=model)
        if params.get("run_tests", False):
            invoke("test",run_id,stage,bronze_mode=bronze_mode,model=model)
        else:
            log.info("Data tests disabled by configuration.")
    log.info("dbt completed; Airflow can now emit Dataset updates. Artifacts: %s", artifacts)
    return artifacts

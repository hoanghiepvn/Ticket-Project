"""Shared submission; no standalone connection-check task."""
import hashlib

from airflow.models import DagRun
from airflow.operators.python import get_current_context
from airflow.utils.session import create_session

from ticketing.airbyte_client import submit


def trigger_sync(connection_id):
    """Submit once and return its Job ID. Authentication happens during submission."""
    # Keep the concurrency guard inside the trigger, not as a separate task.
    with create_session() as session:
        busy = session.query(DagRun).filter(
            DagRun.dag_id.in_(["silver_ticket_all", "gold_ticket_sales"]),
            DagRun.state == "running",
        ).first()
        if busy:
            raise RuntimeError("Silver/Gold is running; do not replace its Bronze input")

    context = get_current_context()
    identity = context["dag"].dag_id + ":" + context["run_id"]
    pipeline_id = hashlib.sha256(identity.encode()).hexdigest()[:32]
    return submit(pipeline_id, connection_id=connection_id)

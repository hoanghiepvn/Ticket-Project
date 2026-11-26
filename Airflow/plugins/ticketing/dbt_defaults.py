"""Shared operational defaults; business schedules stay in individual DAG files."""
from datetime import timedelta

import pendulum
from airflow.models.param import Param


def dag_options():
    return {
        "start_date": pendulum.datetime(2026, 9, 24, tz="Asia/Ho_Chi_Minh"),
        "catchup": False,
        "max_active_runs": 1,
        "max_active_tasks": 1,
        "is_paused_upon_creation": True,
        "dagrun_timeout": timedelta(hours=3),
        "params": {
            "full_refresh": Param(False, type="boolean"),
        },
    }

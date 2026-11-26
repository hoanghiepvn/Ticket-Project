"""BashOperator with the existing same-model lock and initial-layout guard."""
import json
import os
import shlex
import tempfile
from datetime import timedelta
from pathlib import Path

from airflow.operators.bash import BashOperator

from ticketing.dataset_dbt import run_dbt


class DbtBashOperator(BashOperator):
    def __init__(self, *, stage, model=None, **kwargs):
        kwargs.setdefault("cwd", "/opt/project/dbt")
        kwargs.setdefault("do_xcom_push", False)
        kwargs.setdefault("skip_on_exit_code", None)
        kwargs.setdefault("execution_timeout", timedelta(hours=2, minutes=15))
        super().__init__(**kwargs)
        self.stage = stage
        self.model = model

    def execute(self, context):
        # One visible command is the source of truth for both selection and locking.
        args = shlex.split(self.bash_command)
        if len(args) != 4 or args[:3] != ["dbt", "run", "--select"]:
            raise ValueError("Use: dbt run --select path:models/...sql (or tag:silver/gold)")
        selector = args[3]
        project = Path(self.cwd)
        if selector == "tag:" + self.stage:
            self.model = None
        elif selector.startswith("path:models/" + self.stage + "/") and selector.endswith(".sql"):
            source = (project / selector[5:]).resolve()
            if not source.is_relative_to(project.resolve()) or not source.is_file():
                raise ValueError("SQL file not found inside dbt project: " + selector)
            self.model = source.stem
        else:
            raise ValueError("Selector must match the DAG's stage")

        artifacts_root = Path(os.environ.get("DATA_DIR", "/opt/project/data")) / "dbt_runs"
        artifacts_root.mkdir(parents=True, exist_ok=True)
        artifacts = Path(tempfile.mkdtemp(prefix=self.dag_id + "-", dir=artifacts_root))
        args[0] = os.environ.get("DBT_BIN", "/opt/dbt/bin/dbt")
        args += [
            "--project-dir", str(project), "--profiles-dir", str(project),
            "--target-path", str(artifacts / "target"), "--log-path", str(artifacts / "logs"),
            "--vars", json.dumps({"bronze_mode": "full_snapshot"}),
        ]
        if context["params"]["full_refresh"]:
            args.append("--full-refresh")
        original = self.bash_command
        self.bash_command = shlex.join(args)
        self.log.info("SQL selector: %s; artifacts: %s", selector, artifacts)
        self.log.info("Command: %s", self.bash_command)
        try:
            return self._execute_guarded(context)
        finally:
            self.bash_command = original

    def _execute_guarded(self, context):
        return run_dbt(
            self.stage,
            self.model,
            execute=lambda: super(DbtBashOperator, self).execute(context),
        )

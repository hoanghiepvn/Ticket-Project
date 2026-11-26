FROM apache/airflow:2.10.5-python3.11
USER root
RUN python -m venv /opt/dbt && chown -R airflow:root /opt/dbt
USER airflow
COPY Dbt/Dbt-Postgres/requirements.txt /tmp/requirements-dbt.txt
RUN /opt/dbt/bin/pip install --no-cache-dir -r /tmp/requirements-dbt.txt && /opt/dbt/bin/python -m pip check
COPY Airflow/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir "apache-airflow==2.10.5" -r /tmp/requirements.txt && python -m pip check
WORKDIR /opt/project
COPY --chown=airflow:root Airflow/plugins /opt/airflow/plugins
COPY --chown=airflow:root Airflow/dags /opt/project/ticketing_workflows
COPY --chown=airflow:root Dbt/Dbt-Postgres /opt/project/dbt
ENV PYTHONPATH=/opt/project:/opt/airflow/plugins PYTHONUNBUFFERED=1 DBT_BIN=/opt/dbt/bin/dbt DBT_SEND_ANONYMOUS_USAGE_STATS=false

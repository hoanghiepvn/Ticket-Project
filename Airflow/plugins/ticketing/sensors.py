"""Reschedule between polls so the Airbyte wait does not occupy a worker."""
from airflow.sensors.base import BaseSensorOperator
from airflow.exceptions import AirflowException
from ticketing.airbyte_client import AirbyteClient

class AirbyteJobSensor(BaseSensorOperator):
    template_fields = ('job_id',)

    def __init__(self, *, job_id, **kwargs):
        super().__init__(**kwargs)
        self.job_id = job_id
        # Dataset outlets are explicitly declared by the calling DAG.

    def poke(self, context):
        job = AirbyteClient().request('GET',f'/jobs/{int(self.job_id)}')
        status = job.get('status')
        self.log.info('Airbyte job %s: %s', self.job_id, status)
        if status == 'succeeded':
            if 'outlet_events' in context:
                for asset in self.outlets:
                    context['outlet_events'][asset].extra = {
                        'airbyte_job_id': int(self.job_id),
                        'producer_dag': self.dag_id,
                    }
            return True
        if status not in ('pending','running','queued'):
            raise AirflowException(f'Airbyte job {self.job_id}: {status}; inspect Airbyte UI')
        return False

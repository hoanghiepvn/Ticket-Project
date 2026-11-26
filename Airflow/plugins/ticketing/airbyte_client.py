"""Airbyte API; checkpoint submitted jobs, never blindly retry a POST."""
import logging
import os
import time
import uuid
import requests
from ticketing.common import DATA, read, save
from ticketing.schema import require

log = logging.getLogger(__name__)

class AirbyteClient:
    def __init__(self):
        self.base = os.environ['AIRBYTE_API_URL'].rstrip('/')
        self.client_id = os.environ.get('AIRBYTE_CLIENT_ID','')
        self.secret = os.environ.get('AIRBYTE_CLIENT_SECRET','')
        require(bool(self.client_id and self.secret), 'Configure Airbyte credentials in .env')
        self.token = None
        self.expires = 0

    def headers(self):
        if time.monotonic() >= self.expires:
            response = requests.post(self.base+'/applications/token',
                json={'client_id':self.client_id,'client_secret':self.secret},timeout=30)
            require(response.ok, f'Airbyte authentication failed: HTTP {response.status_code}')
            body = response.json()
            self.token = body['access_token']
            self.expires = time.monotonic()+max(1,int(body.get('expires_in',180))-30)
        return {'Authorization':'Bearer '+self.token}

    def request(self,method,path,**kwargs):
        response = requests.request(method,self.base+path,headers=self.headers(),timeout=30,**kwargs)
        log.info('Airbyte %s %s -> HTTP %s', method, path, response.status_code)
        require(response.ok, f'Airbyte {method} failed: HTTP {response.status_code}')
        return response.json()

def submit(run_id, connection_id=None):
    client = AirbyteClient()
    connection = str(uuid.UUID(connection_id or os.environ.get('AIRBYTE_CONNECTION_ID','')))
    folder = DATA/'elt'/run_id/'airbyte'/connection
    path = folder/'airbyte.json'
    marker = folder/'sync_intent.json'
    if path.exists():
        previous = read(path)
        require(previous['connection_id'] == connection, 'Checkpoint belongs to another connection')
        return str(previous['job_id'])
    require(not marker.exists(), 'Previous POST outcome unknown; inspect Airbyte UI before retrying')
    save(marker, {'connection_id':connection,'status':'requesting'})
    result = client.request('POST','/jobs',json={'connectionId':connection,'jobType':'sync'})
    job_id = int(result['jobId'])
    save(path, {'job_id':job_id,'connection_id':connection})
    return str(job_id)

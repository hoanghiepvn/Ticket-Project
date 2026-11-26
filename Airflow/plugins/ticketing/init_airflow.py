"""Explicit bootstrap only. Importing this module must never spawn commands."""
import json
import os
import subprocess

def main():
    users = json.loads(subprocess.check_output(
        ['airflow','users','list','--output','json'], text=True, timeout=120))
    if not any(user['username'] == 'admin' for user in users):
        subprocess.run([
            'airflow','users','create','--username','admin',
            '--password',os.environ['AIRFLOW_ADMIN_PASSWORD'],
            '--firstname','Ticketing','--lastname','Admin','--role','Admin',
            '--email','admin@localhost.invalid',
        ], check=True, timeout=120)

if __name__ == '__main__':
    main()

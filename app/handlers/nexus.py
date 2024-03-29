
import os
import json
import requests


class NexusRESTClient:
    token = os.environ.get("NEXUS_AI_TOKEN")
    base_url = os.environ.get("NEXUS_AI_URL")

    def __init__(self) -> None:
        self.headers = {
            'Authorization': self.token,
            'Content-Type': "application/json"
        }

    def index_succedded(self, task_succeded: bool, nexus_task_uuid: str, file_type: str) -> None:
        endpoint = f'{self.base_url}/api/v1/content-base-file'
        data = { 
            "status": int(task_succeded),
            "task_uuid": nexus_task_uuid,
            "file_type": "text" if file_type == "txt" else "file",
        }
        response = requests.patch(url=endpoint, data=json.dumps(data), headers=self.headers)
        response.raise_for_status()

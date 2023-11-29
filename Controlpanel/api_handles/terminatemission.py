import requests
from dotenv import load_dotenv
import os

load_dotenv()

def terminate(end_time):
    url = "http://129.80.123.18/api/control-panel/end_mission.php"
    payload = {"end_time": end_time}
    files = []
    headers = {"API_KEY": os.getenv("API_KEY")}
    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    return response.status_code

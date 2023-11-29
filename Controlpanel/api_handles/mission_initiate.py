import requests
from dotenv import load_dotenv
import os

load_dotenv()


def initiate(name, objective, location, time):
    url = "http://129.80.123.18/api/control-panel/create_mission.php"
    payload = {
        "mission_name": name,
        "mission_objective": objective,
        "mission_location": location,
        "start_time": time,
    }
    files = []
    headers = {"API_KEY": os.getenv("API_KEY")}
    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    return response.status_code

import requests
from dotenv import load_dotenv
import os

load_dotenv()


def upload(temp, pressure, ph, time, image):
    url = "http://129.80.123.18/api/control-panel/upload_data.php"

    payload = {"temp": temp, "pressure": pressure, "ph": ph, "time": time}
    files = [("image", ("capture.jpg", image, "image/jpeg"))]

    headers = {"API_KEY": os.getenv("API_KEY")}
    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    return response.status_code

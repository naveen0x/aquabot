import requests
from dotenv import load_dotenv
import os

load_dotenv()

url = "http://129.80.123.18/api/dashboard/mission_data.php"
payload = {}
files = {}
headers = {"API_KEY": os.getenv("API_KEY")}


def mission():
       
    try:
        response = requests.request("POST", url, headers=headers, data=payload, files=files)
        if response.status_code == 200:
            json_data = response.json()
            return json_data
        else:
            print("Failed to retrieve data. Status code:", response.status_code)
            return "error"

    except requests.exceptions.ConnectionError as e:
        print(f"Error: Could not connect to {url}. Please check your internet connection.")
        return "int-error"

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

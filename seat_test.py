
import requests
from dotenv import load_dotenv
import os
import json

load_dotenv()

url = "https://apis.cineplex.com/prod/ticketing/api/v1/theatre/7420/showtime/385223/seat-availability"

headers = {
    "Ocp-Apim-Subscription-Key": os.getenv("CINEPLEX_KEY")
}

response = requests.get(url, headers=headers)

data = response.json()

print(json.dumps(data, indent=2)[:5000])
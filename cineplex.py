import os
from datetime import datetime, timedelta
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv

load_dotenv()

session = requests.Session()
session.headers.update({
    "Ocp-Apim-Subscription-Key": os.getenv("CINEPLEX_KEY", "")
})

THEATRES = [
    {"id": 7420, "name": "Cineplex Cinemas Mississauga Square One"},
    {"id": 7408, "name": "Cineplex Cinemas Vaughan"},
]


def normalize_ticket_url(ticket_url, theatre_id, showtime_id):
    if not ticket_url:
        return f"https://www.cineplex.com/Showtimes/{theatre_id}/{showtime_id}"

    parsed = urlparse(ticket_url)
    if parsed.scheme in {"http", "https"} and parsed.netloc:
        return ticket_url

    return f"https://www.cineplex.com/Showtimes/{theatre_id}/{showtime_id}"


def get_json(url):
    response = session.get(url)

    if response.status_code != 200:
        print("API ERROR:", response.status_code)
        print(response.text[:200])
        return []

    try:
        return response.json()
    except Exception:
        print("BAD JSON:")
        print(response.text[:200])
        return []


def find_imax_70mm_showtimes():
    today = datetime.today()
    shows = []

    for day_offset in range(20):
        date = (today + timedelta(days=day_offset)).strftime("%m/%d/%Y")

        for theatre in THEATRES:
            url = (
                "https://apis.cineplex.com/prod/cpx/theatrical/api/v1/showtimes"
                f"?language=en&locationId={theatre['id']}&date={date}&filmId=37617"
            )

            data = get_json(url)
            if not isinstance(data, list):
                continue

            for theatre_data in data:
                if not isinstance(theatre_data, dict):
                    continue

                for day in theatre_data.get("dates", []):
                    for movie in day.get("movies", []):
                        if movie.get("name") != "The Odyssey":
                            continue

                        for experience in movie.get("experiences", []):
                            experience_types = experience.get("experienceTypes", [])
                            if "IMAX" not in experience_types or "70mm" not in experience_types:
                                continue

                            for session in experience.get("sessions", []):
                                show_time = datetime.fromisoformat(session["showStartDateTime"])
                                if show_time.hour < 17:
                                    continue

                                showtime_id = session["vistaSessionId"]
                                ticket_url = normalize_ticket_url(
                                    session.get("ticketingUrl"),
                                    theatre_data["theatreId"],
                                    showtime_id,
                                )

                                shows.append({
                                    "theatre_id": theatre_data["theatreId"],
                                    "theatre": theatre_data["theatre"],
                                    "showtime_id": showtime_id,
                                    "time": session["showStartDateTime"],
                                    "ticket_url": ticket_url,
                                })

    return shows
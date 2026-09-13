import os

import requests
from dotenv import load_dotenv

load_dotenv()

session = requests.Session()
session.headers.update({
    "Ocp-Apim-Subscription-Key": os.getenv("CINEPLEX_KEY", "")
})

layout_cache = {}
row_scores = {
    "H": 100,
    "G": 90,
    "I": 90,
    "F": 80,
    "J": 70,
}
PREFERRED_ROWS = ["F", "G", "H", "I", "J"]
PAIR_ROWS = ["F", "G", "H", "I"]


def seat_score(row, seat):
    row_score = row_scores.get(row, 0)
    centre_distance = abs(seat - 15)
    return row_score - centre_distance


def find_good_seats(theatre_id, showtime_id):
    def get_json(url):
        response = session.get(url)
        response.raise_for_status()
        return response.json()

    availability_url = (
        f"https://apis.cineplex.com/prod/ticketing/api/v1/"
        f"theatre/{theatre_id}/showtime/{showtime_id}/seat-availability"
    )
    availability = get_json(availability_url)["seatAvailabilities"]
    available_count = sum(1 for seat in availability.values() if seat == "Available")

    if available_count < 1:
        return []

    cache_key = f"{theatre_id}_{showtime_id}"
    if cache_key not in layout_cache:
        layout_url = (
            f"https://apis.cineplex.com/prod/ticketing/api/v1/"
            f"theatre/{theatre_id}/showtime/{showtime_id}/seat-layout"
        )
        layout_cache[cache_key] = get_json(layout_url)

    layout = layout_cache[cache_key]
    available_seats = []

    for row in layout["standardSeats"]["rows"]:
        row_label = row["label"]
        if row_label not in PREFERRED_ROWS:
            continue

        for seat in row["seats"]:
            seat_id = seat["id"]
            if availability.get(seat_id) == "Available":
                available_seats.append({
                    "id": seat_id,
                    "label": seat["label"],
                    "row": row_label,
                })

    available_by_row = {}
    for seat in available_seats:
        row = seat["row"]
        if row not in PAIR_ROWS:
            continue

        available_by_row.setdefault(row, []).append(int(seat["label"][1:]))

    good_pairs = []
    for row, seats in available_by_row.items():
        seats.sort()

        for i in range(len(seats) - 1):
            if seats[i + 1] == seats[i] + 1:
                seat1 = seats[i]
                seat2 = seats[i + 1]
                score = seat_score(row, seat1) + seat_score(row, seat2)
                good_pairs.append({
                    "row": row,
                    "seat1": seat1,
                    "seat2": seat2,
                    "score": score,
                })

    if good_pairs:
        good_pairs.sort(key=lambda x: x["score"], reverse=True)
        return good_pairs

    single_seats = [
        {
            "row": seat["row"],
            "seat1": int(seat["label"][1:]),
            "seat2": None,
            "score": seat_score(seat["row"], int(seat["label"][1:])),
        }
        for seat in available_seats
        if seat["row"] in PAIR_ROWS
    ]

    single_seats.sort(key=lambda x: x["score"], reverse=True)
    return single_seats[:3]
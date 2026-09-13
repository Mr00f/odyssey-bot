from concurrent.futures import ThreadPoolExecutor

from alert_tracker import filter_new_alerts
from cineplex import find_imax_70mm_showtimes
from discord_alert import send_alert
from seat_finder import find_good_seats


def check_show(show):
    seats = find_good_seats(show["theatre_id"], show["showtime_id"])
    if not seats:
        return None

    return {"show": show, "seats": seats[:3]}


def check_for_seats():
    shows = find_imax_70mm_showtimes()

    with ThreadPoolExecutor(max_workers=min(10, max(1, len(shows)))) as executor:
        results = executor.map(check_show, shows)

    return [result for result in results if result]


if __name__ == "__main__":
    alerts = check_for_seats()
    if alerts:
        new_alerts = filter_new_alerts(alerts)
        if new_alerts:
            send_alert(new_alerts)
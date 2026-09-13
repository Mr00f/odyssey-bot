import json
import os

FILE_NAME = "seen_alerts.json"


def load_seen_alerts():
    if not os.path.exists(FILE_NAME):
        return set()

    with open(FILE_NAME, "r", encoding="utf-8") as file:
        data = json.load(file)

    return set(data)


def save_seen_alerts(seen):
    with open(FILE_NAME, "w", encoding="utf-8") as file:
        json.dump(list(seen), file, indent=2)


def create_alert_key(alert):
    show = alert["show"]
    seats = alert["seats"]
    seat_string = ",".join(f"{s['row']}{s['seat1']}-{s['seat2']}" for s in seats)
    return f"{show['theatre']}|{show['time']}|{seat_string}"


def filter_new_alerts(alerts):
    seen = load_seen_alerts()
    new_alerts = []

    for alert in alerts:
        key = create_alert_key(alert)
        if key not in seen:
            new_alerts.append(alert)
            seen.add(key)

    save_seen_alerts(seen)
    return new_alerts
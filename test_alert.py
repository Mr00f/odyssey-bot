from discord_alert import send_alert

test_alerts = [
    {
        "show": {
            "theatre": "Cineplex Cinemas Vaughan",
            "time": "2026-07-29T18:00:00",
            "ticket_url": "https://example.com"
        },
        "seats": [
            {
                "row": "G",
                "seat1": 14,
                "seat2": 15
            },
            {
                "row": "G",
                "seat1": 16,
                "seat2": 17
            }
        ]
    }
]

send_alert(test_alerts)
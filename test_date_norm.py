from utils import format_date_colombian

dates_to_test = [
    "2026-02-11",
    "2026-02-11T00:00:00",
    "2026-02-11T00:00:00-05:00",
    " 2026-02-11 ",
    "11/02/2026",
    "2026/02/11",
    None,
    ""
]

print("Testing format_date_colombian:")
for d in dates_to_test:
    res = format_date_colombian(d)
    print(f"'{d}' -> '{res}'")

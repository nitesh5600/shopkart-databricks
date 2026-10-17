"""Generate ShopKart clickstream events (nested JSON lines) linked to the existing ShopKart dataset."""
import csv, json, os, random, uuid
from datetime import datetime, timedelta

random.seed(7)
RAW = "shopkart_data/raw"
OUT = "shopkart_data/events"
os.makedirs(OUT, exist_ok=True)

def hid():
    return uuid.UUID(int=random.getrandbits(128)).hex

people = {}
with open(f"{RAW}/olist_customers_dataset.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        people[r["customer_unique_id"]] = (r["customer_state"], r["customer_city"])
people = list(people.items())

products = []
with open(f"{RAW}/olist_products_dataset.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        products.append((r["product_id"], r["product_category_name"] or None))
prices = {}
with open(f"{RAW}/olist_order_items_dataset.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        prices[r["product_id"]] = float(r["price"])
products = [p for p in products if p[0] in prices]

DEVICES = [("mobile", "android", 45), ("mobile", "ios", 20), ("desktop", "windows", 22),
           ("desktop", "macos", 8), ("tablet", "android", 3), ("tablet", "ios", 2)]
REFS = ["google", "instagram", "facebook", "direct", "email_campaign", "youtube"]

def ts(d):
    return d.strftime("%Y-%m-%dT%H:%M:%S.") + f"{d.microsecond // 1000:03d}Z"

def session(start, version=None):
    """One browsing session: page views, cart changes, maybe checkout + purchase."""
    uid, (state, city) = random.choice(people)
    logged_in = random.random() < 0.8
    dtype, os_, _ = random.choices(DEVICES, [d[2] for d in DEVICES])[0]
    sid = hid()
    t = start
    cart = []
    events = []

    def ev(etype, page, extra=None):
        nonlocal t
        t += timedelta(seconds=random.randint(3, 120), milliseconds=random.randint(0, 999))
        e = {
            "event_id": hid(),
            "event_type": etype,
            "event_ts": ts(t),
            "session_id": sid,
            "user": {
                "customer_unique_id": uid if logged_in else None,
                "is_logged_in": logged_in,
                "geo": {"state": state, "city": city},
            },
            "device": {"type": dtype, "os": os_},
            "page": {"url": page, "referrer": random.choice(REFS) if not events else None},
            "cart": {"items": [dict(i) for i in cart],
                     "cart_value": round(sum(i["price"] * i["qty"] for i in cart), 2)},
            "properties": extra or {},
        }
        if version:
            e["app_version"] = version  # new field that only appears in later batches
        events.append(e)

    ev("page_view", "/home")
    for _ in range(random.randint(1, 6)):
        pid, cat = random.choice(products)
        ev("page_view", f"/product/{pid}", {"category": cat} if cat else {})
        if random.random() < 0.35:
            cart.append({"product_id": pid, "qty": random.choices([1, 2, 3], [85, 12, 3])[0],
                         "price": prices[pid]})
            ev("add_to_cart", f"/product/{pid}", {"product_id": pid})
    if cart and random.random() < 0.15:
        removed = cart.pop(random.randrange(len(cart)))
        ev("remove_from_cart", "/cart", {"product_id": removed["product_id"]})
    if cart and random.random() < 0.45:
        ev("checkout", "/checkout", {"payment_type": random.choice(["credit_card", "boleto", "voucher"])})
        if random.random() < 0.7:
            ev("purchase", "/checkout/success", {"order_ref": hid()[:12]})
    return events

def batch(name, day, n_sessions, version=None, late_from=None, n_late=0, corrupt=0):
    rows = []
    for _ in range(n_sessions):
        start = day + timedelta(seconds=random.randint(0, 86399))
        rows += session(start, version)
    if late_from:  # sessions that happened on an earlier day but arrive only now
        for _ in range(n_late):
            start = late_from + timedelta(seconds=random.randint(0, 86399))
            rows += session(start, version)
    lines = [json.dumps(r, ensure_ascii=False) for r in rows]
    for _ in range(corrupt):
        bad = random.choice(lines)
        lines.insert(random.randrange(len(lines)), bad[: random.randint(20, len(bad) - 10)])  # truncated JSON
    with open(f"{OUT}/{name}", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return len(rows), len(lines)

d = datetime(2018, 8, 20)
stats = {
    "events_2018-08-20.json": batch("events_2018-08-20.json", d, 3000, corrupt=5),
    "events_2018-08-21.json": batch("events_2018-08-21.json", d + timedelta(days=1), 3000, corrupt=3),
    # app release: new field app_version appears
    "events_2018-08-22.json": batch("events_2018-08-22.json", d + timedelta(days=2), 3000, version="5.2.0"),
    # mobile devices that were offline sync late: 2-day-old sessions arrive with this batch
    "events_2018-08-23.json": batch("events_2018-08-23.json", d + timedelta(days=3), 3000, version="5.2.0",
                                    late_from=d + timedelta(days=1), n_late=250),
}
for k, v in stats.items():
    print(k, "events", v[0], "lines", v[1])

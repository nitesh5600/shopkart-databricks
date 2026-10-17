"""Generate a synthetic ShopKart dataset that mirrors the Olist Brazilian e-commerce schema."""
import csv, os, random, uuid
from datetime import datetime, timedelta

random.seed(42)
OUT = "shopkart_data/raw"
INC = "shopkart_data/incremental"
os.makedirs(OUT, exist_ok=True)
os.makedirs(INC, exist_ok=True)

def hid():
    return uuid.UUID(int=random.getrandbits(128)).hex

def ts(d):
    return d.strftime("%Y-%m-%d %H:%M:%S") if d else ""

def write(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)

# ---------- geography ----------
STATES = {
    "SP": (0.42, ["sao paulo", "campinas", "guarulhos", "santos", "sorocaba", "ribeirao preto", "osasco", "sao jose dos campos"], (1000, 19999)),
    "RJ": (0.13, ["rio de janeiro", "niteroi", "duque de caxias", "nova iguacu", "petropolis"], (20000, 28999)),
    "MG": (0.12, ["belo horizonte", "uberlandia", "contagem", "juiz de fora", "betim"], (30000, 39999)),
    "RS": (0.055, ["porto alegre", "caxias do sul", "pelotas", "canoas"], (90000, 99999)),
    "PR": (0.05, ["curitiba", "londrina", "maringa", "ponta grossa"], (80000, 87999)),
    "SC": (0.037, ["florianopolis", "joinville", "blumenau", "itajai"], (88000, 89999)),
    "BA": (0.034, ["salvador", "feira de santana", "vitoria da conquista"], (40000, 48999)),
    "DF": (0.022, ["brasilia"], (70000, 73699)),
    "ES": (0.02, ["vitoria", "vila velha", "serra"], (29000, 29999)),
    "GO": (0.02, ["goiania", "anapolis", "aparecida de goiania"], (72800, 76799)),
    "PE": (0.017, ["recife", "jaboatao dos guararapes", "olinda"], (50000, 56999)),
    "CE": (0.013, ["fortaleza", "caucaia", "juazeiro do norte"], (60000, 63999)),
    "PA": (0.01, ["belem", "ananindeua", "santarem"], (66000, 68899)),
    "MT": (0.009, ["cuiaba", "varzea grande"], (78000, 78899)),
    "MA": (0.007, ["sao luis", "imperatriz"], (65000, 65999)),
    "MS": (0.007, ["campo grande", "dourados"], (79000, 79999)),
    "PB": (0.005, ["joao pessoa", "campina grande"], (58000, 58999)),
    "PI": (0.005, ["teresina"], (64000, 64999)),
    "RN": (0.005, ["natal", "mossoro"], (59000, 59999)),
    "AL": (0.004, ["maceio"], (57000, 57999)),
    "SE": (0.003, ["aracaju"], (49000, 49999)),
    "TO": (0.003, ["palmas"], (77000, 77999)),
    "RO": (0.003, ["porto velho"], (76800, 76999)),
    "AM": (0.002, ["manaus"], (69000, 69299)),
    "AC": (0.001, ["rio branco"], (69900, 69999)),
    "AP": (0.001, ["macapa"], (68900, 68999)),
    "RR": (0.001, ["boa vista"], (69300, 69399)),
}
STATE_KEYS = list(STATES)
STATE_W = [STATES[s][0] for s in STATE_KEYS]

def location(state=None):
    s = state or random.choices(STATE_KEYS, STATE_W)[0]
    _, cities, (lo, hi) = STATES[s]
    return f"{random.randint(lo, hi):05d}", random.choice(cities), s

# ---------- categories ----------
CATS = [  # pt name, english, weight, price range
    ("cama_mesa_banho", "bed_bath_table", 10, (20, 180)),
    ("beleza_saude", "health_beauty", 9, (15, 250)),
    ("esporte_lazer", "sports_leisure", 8, (20, 300)),
    ("moveis_decoracao", "furniture_decor", 7, (30, 400)),
    ("informatica_acessorios", "computers_accessories", 7, (25, 600)),
    ("utilidades_domesticas", "housewares", 6, (15, 200)),
    ("relogios_presentes", "watches_gifts", 5, (60, 900)),
    ("telefonia", "telephony", 4, (15, 700)),
    ("ferramentas_jardim", "garden_tools", 4, (20, 300)),
    ("automotivo", "auto", 4, (20, 400)),
    ("brinquedos", "toys", 4, (15, 250)),
    ("cool_stuff", "cool_stuff", 3, (40, 500)),
    ("perfumaria", "perfumery", 3, (30, 350)),
    ("bebes", "baby", 3, (20, 300)),
    ("eletronicos", "electronics", 2, (20, 500)),
    ("papelaria", "stationery", 2, (8, 120)),
    ("fashion_bolsas_e_acessorios", "fashion_bags_accessories", 2, (20, 200)),
    ("pet_shop", "pet_shop", 2, (15, 200)),
    ("moveis_escritorio", "office_furniture", 1.5, (100, 800)),
    ("consoles_games", "consoles_games", 1.2, (40, 1500)),
    ("malas_acessorios", "luggage_accessories", 1, (60, 600)),
    ("construcao_ferramentas_construcao", "construction_tools_construction", 1, (25, 400)),
    ("eletrodomesticos", "home_appliances", 1, (40, 900)),
    ("instrumentos_musicais", "musical_instruments", 0.8, (30, 1200)),
    ("livros_interesse_geral", "books_general_interest", 0.6, (15, 120)),
    ("alimentos", "food", 0.5, (10, 120)),
    # present in products but intentionally MISSING from the translation file (real Olist quirk)
    ("pc_gamer", None, 0.15, (300, 3000)),
    ("portateis_cozinha_e_preparadores_de_alimentos", None, 0.15, (50, 600)),
]

write(f"{OUT}/product_category_name_translation.csv",
      ["product_category_name", "product_category_name_english"],
      [(pt, en) for pt, en, _, _ in CATS if en])

# ---------- sellers ----------
sellers = []
for _ in range(450):
    z, c, s = location()
    sellers.append((hid(), z, c, s))
write(f"{OUT}/olist_sellers_dataset.csv",
      ["seller_id", "seller_zip_code_prefix", "seller_city", "seller_state"], sellers)
seller_w = [random.paretovariate(1.2) for _ in sellers]  # a few big sellers

# ---------- products ----------
products = []
prod_meta = {}
for _ in range(2800):
    pt, en, w, (lo, hi) = random.choices(CATS, [c[2] for c in CATS])[0]
    pid = hid()
    null_cat = random.random() < 0.015  # ~1.5% products with no category
    weight = random.randint(100, 15000)
    products.append((pid, "" if null_cat else pt,
                     "" if null_cat else random.randint(20, 76),
                     "" if null_cat else random.randint(100, 3000),
                     "" if null_cat else random.randint(1, 8),
                     weight, random.randint(15, 100), random.randint(2, 80), random.randint(10, 80)))
    prod_meta[pid] = (round(random.uniform(lo, hi), 2), weight)
write(f"{OUT}/olist_products_dataset.csv",
      ["product_id", "product_category_name", "product_name_lenght", "product_description_lenght",
       "product_photos_qty", "product_weight_g", "product_length_cm", "product_height_cm", "product_width_cm"],
      products)
prod_ids = [p[0] for p in products]
prod_w = [random.paretovariate(1.1) for _ in products]  # best-sellers

# ---------- customers & orders ----------
N_ORDERS = 20000
START, END = datetime(2017, 1, 5), datetime(2018, 8, 29)
span = (END - START).total_seconds()

persons = []  # (unique_id, zip, city, state)
customers, orders, items, payments, reviews = [], [], [], [], []
order_rows = {}

STATUS = ["delivered"] * 970 + ["shipped"] * 11 + ["canceled"] * 6 + ["unavailable"] * 6 + ["invoiced"] * 3 + ["processing"] * 3 + ["approved"] * 1

for i in range(N_ORDERS):
    # growth over time: more orders later
    frac = random.random() ** 0.7
    purchase = START + timedelta(seconds=frac * span)
    purchase = purchase.replace(microsecond=0)

    if persons and random.random() < 0.03:
        person = random.choice(persons)  # repeat customer
    else:
        z, c, s = location()
        person = (hid(), z, c, s)
        persons.append(person)
    cust_id = hid()  # Olist: new customer_id per order
    customers.append((cust_id, person[0], person[1], person[2], person[3]))

    status = random.choice(STATUS)
    approved = purchase + timedelta(minutes=random.randint(5, 2880))
    if random.random() < 0.002:
        approved = None
    est = (purchase + timedelta(days=random.randint(15, 45))).replace(hour=0, minute=0, second=0)
    carrier = delivered = None
    if status in ("shipped", "delivered"):
        carrier = (approved or purchase) + timedelta(hours=random.randint(10, 150))
    if status == "delivered":
        far = STATES[person[3]][0] < 0.02
        delivered = carrier + timedelta(days=random.randint(1, 8) + (random.randint(5, 20) if far else 0),
                                        hours=random.randint(0, 23))
        if random.random() < 0.0004:  # rare source-system glitch: delivered before purchase
            delivered = purchase - timedelta(days=random.randint(1, 5))
        if random.random() < 0.001:
            delivered = None  # delivered but missing date
    oid = hid()
    row = [oid, cust_id, status, ts(purchase), ts(approved), ts(carrier), ts(delivered), ts(est)]
    orders.append(row)
    order_rows[oid] = row

    # items
    n_items = random.choices([1, 2, 3, 4, 6], [88, 8, 2.5, 1, 0.5])[0]
    if status in ("canceled", "unavailable") and random.random() < 0.5:
        n_items = 0
    total = 0.0
    pid = random.choices(prod_ids, prod_w)[0]
    sid = random.choices(sellers, seller_w)[0][0]
    for k in range(1, n_items + 1):
        if random.random() < 0.3:  # different product in same order
            pid = random.choices(prod_ids, prod_w)[0]
            sid = random.choices(sellers, seller_w)[0][0]
        price, weight = prod_meta[pid]
        freight = round(max(5.0, weight / 1000 * random.uniform(1.5, 3.5) + random.uniform(5, 15)), 2)
        items.append((oid, k, pid, sid, ts(purchase + timedelta(days=random.randint(2, 7))), price, freight))
        total += price + freight

    # payments
    if n_items:
        total = round(total, 2)
        ptype = random.choices(["credit_card", "boleto", "voucher", "debit_card"], [74, 19, 5, 2])[0]
        if ptype == "credit_card" and random.random() < 0.03:  # split with voucher
            v = round(min(total - 1, random.uniform(10, 60)), 2)
            payments.append((oid, 1, "credit_card", random.randint(1, 10), round(total - v, 2)))
            payments.append((oid, 2, "voucher", 1, v))
        else:
            inst = random.randint(1, 10) if ptype == "credit_card" else 1
            payments.append((oid, 1, ptype, inst, total))

    # reviews (most delivered orders)
    if status == "delivered" and delivered and random.random() < 0.9:
        late = delivered > est
        score = random.choices([1, 2, 3, 4, 5], [40, 12, 15, 15, 18] if late else [7, 3, 8, 20, 62])[0]
        msgs = {1: ["produto nao chegou", "pessimo atendimento", "veio errado"],
                2: ["demorou muito", "qualidade ruim"],
                3: ["ok", "produto razoavel"],
                4: ["bom produto", "chegou no prazo"],
                5: ["excelente", "recomendo", "otimo produto, chegou antes do prazo"]}
        has_msg = random.random() < 0.4
        created = (delivered + timedelta(days=1)).replace(hour=0, minute=0, second=0)
        reviews.append((hid(), oid, score, "",
                        random.choice(msgs[score]) if has_msg else "",
                        ts(created), ts(created + timedelta(hours=random.randint(5, 96)))))

write(f"{OUT}/olist_customers_dataset.csv",
      ["customer_id", "customer_unique_id", "customer_zip_code_prefix", "customer_city", "customer_state"], customers)
ORDER_HDR = ["order_id", "customer_id", "order_status", "order_purchase_timestamp", "order_approved_at",
             "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date"]
write(f"{OUT}/olist_orders_dataset.csv", ORDER_HDR, orders)
write(f"{OUT}/olist_order_items_dataset.csv",
      ["order_id", "order_item_id", "product_id", "seller_id", "shipping_limit_date", "price", "freight_value"], items)
write(f"{OUT}/olist_order_payments_dataset.csv",
      ["order_id", "payment_sequential", "payment_type", "payment_installments", "payment_value"], payments)
write(f"{OUT}/olist_order_reviews_dataset.csv",
      ["review_id", "order_id", "review_score", "review_comment_title", "review_comment_message",
       "review_creation_date", "review_answer_timestamp"], reviews)

# ---------- SK-10: incremental daily order feeds ----------
def month(r):
    return r[3][:7]
day1 = [r for r in orders if month(r) <= "2017-12"]
day2 = [r for r in orders if "2018-01" <= month(r) <= "2018-04"]
day3 = [r for r in orders if month(r) >= "2018-05"]

# 100 delivered orders from day_2 first arrive as 'shipped', then get updated in day_3
cands = [r for r in day2 if r[2] == "delivered" and r[6]]
updated = random.sample(cands, 100)
upd_ids = {r[0] for r in updated}
day2_out = []
for r in day2:
    if r[0] in upd_ids:
        r2 = list(r); r2[2] = "shipped"; r2[6] = ""
        day2_out.append(r2)
    else:
        day2_out.append(r)
day3_out = day3 + [list(r) for r in updated]
random.shuffle(day3_out)

write(f"{INC}/orders_day_1.csv", ORDER_HDR, day1)
write(f"{INC}/orders_day_2.csv", ORDER_HDR, day2_out)
write(f"{INC}/orders_day_3.csv", ORDER_HDR, day3_out)

# ---------- SK-11: customer address change file ----------
movers = random.sample(persons, 50)
changes = []
for p in movers:
    new_state = random.choices([s for s in STATE_KEYS if s != p[3]],
                               [STATES[s][0] for s in STATE_KEYS if s != p[3]])[0]
    z, c, s = location(new_state)
    changes.append((p[0], z, c, s, "2018-09-01"))
# 5 rows that look like changes but are identical to current data (should NOT create new versions)
for p in random.sample([q for q in persons if q not in movers], 5):
    changes.append((p[0], p[1], p[2], p[3], "2018-09-01"))
random.shuffle(changes)
write(f"{INC}/customer_address_changes.csv",
      ["customer_unique_id", "customer_zip_code_prefix", "customer_city", "customer_state", "change_date"], changes)

print("orders", len(orders), "items", len(items), "customers", len(customers), "persons", len(persons),
      "products", len(products), "sellers", len(sellers), "payments", len(payments), "reviews", len(reviews))
print("day1/2/3", len(day1), len(day2_out), len(day3_out), "changes", len(changes))

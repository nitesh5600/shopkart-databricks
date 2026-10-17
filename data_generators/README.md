# ShopKart dataset

Synthetic e-commerce data for the ShopKart learning project. It uses the **same file names, columns and quirks as the public Olist Brazilian E-Commerce dataset**, so any Olist tutorial or Kaggle notebook applies. The data is generated (no real people or orders) and sized to run comfortably within the Databricks Free Edition quota.

## raw/ (used from SK-01 onwards)

| File | Rows | Key | Notes |
|---|---|---|---|
| olist_orders_dataset.csv | 20,000 | order_id | Jan 2017 – Aug 2018, 7 statuses |
| olist_customers_dataset.csv | 20,000 | customer_id | One `customer_id` per order. The real person is `customer_unique_id` (19,412 people, ~3% repeat buyers) |
| olist_order_items_dataset.csv | 23,650 | order_id + order_item_id | price and freight per item |
| olist_products_dataset.csv | 2,800 | product_id | Category name in Portuguese; column names keep Olist's typo `lenght` |
| product_category_name_translation.csv | 26 | product_category_name | Portuguese → English |
| olist_sellers_dataset.csv | 450 | seller_id | |
| olist_order_payments_dataset.csv | 20,314 | order_id + payment_sequential | Some orders are paid in 2 parts (card + voucher) |
| olist_order_reviews_dataset.csv | 17,481 | review_id | Scores 1–5, short Portuguese comments |

## incremental/ (used in SK-10 and SK-11)

| File | Rows | Purpose |
|---|---|---|
| orders_day_1.csv | 9,681 | Orders purchased in 2017 |
| orders_day_2.csv | 4,871 | Orders purchased Jan–Apr 2018 |
| orders_day_3.csv | 5,548 | Orders purchased May–Aug 2018, plus updates to existing orders |
| customer_address_changes.csv | 55 | Customers who moved, effective 2018-09-01 |

## Real-world quirks you will meet (do not "fix" the source files)

These are deliberate, and several tickets depend on them:

- Some products have **no category** (blank). Items for these products still exist.
- Two categories (`pc_gamer`, `portateis_cozinha_e_preparadores_de_alimentos`) are **missing from the translation file**.
- A handful of orders were **delivered before they were purchased** (a source-system bug).
- A few `delivered` orders have **no delivery date**, and a few orders have no approval date.
- Some canceled/unavailable orders have **no items and no payments**.
- `orders_day_3.csv` contains **100 orders that already arrived in day 2** with status `shipped`; in day 3 they are `delivered` with a delivery date. Your MERGE must update them, not duplicate them.
- `customer_address_changes.csv` has 50 real moves and **5 rows identical to the current address**. Those 5 must not create new SCD2 versions.

The full `raw/olist_orders_dataset.csv` is the final state of all orders (the same as day_1 + day_2 + day_3 after the updates are applied), so you can use it to check your incremental pipeline.

## ShopKart clickstream events

Website and app events from ShopKart, as JSON Lines (one JSON object per line). They are linked to the main dataset: `user.customer_unique_id` matches `olist_customers_dataset.csv`, and product ids match `olist_products_dataset.csv`.

| File | Events | Notes |
|---|---|---|
| events_2018-08-20.json | 18,938 | Includes **5 corrupt (truncated) lines** |
| events_2018-08-21.json | 18,944 | Includes **3 corrupt lines** |
| events_2018-08-22.json | 18,841 | New app release: a new top-level field **`app_version`** appears |
| events_2018-08-23.json | 20,588 | Includes **~1,550 late events** from 2018-08-21 (phones that synced late) |

## Shape of one event

```
event_id, event_type, event_ts (ISO string, UTC), session_id
user:       { customer_unique_id (null if not logged in), is_logged_in, geo: { state, city } }
device:     { type, os }
page:       { url, referrer (only on the first event of a session) }
cart:       { items: [ { product_id, qty, price } ], cart_value }
properties: { varies by event_type: category / product_id / payment_type / order_ref }
app_version (only from 2018-08-22 onwards)
```

Event types: `page_view`, `add_to_cart`, `remove_from_cart`, `checkout`, `purchase`.

Deliberate quirks: corrupt lines, a field that appears halfway through, late-arriving data, null user ids for anonymous visitors, an array that is empty for most events, and `properties` whose keys change per event type.

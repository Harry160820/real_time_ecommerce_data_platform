# historical_data_loader.py
import json, random, uuid, os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from faker import Faker
from azure.storage.filedatalake import DataLakeServiceClient

fake = Faker()
load_dotenv()
# ---------- CONFIGURATION ----------
AZURE_STORAGE_ACCOUNT_NAME = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")   # your storage account name
AZURE_STORAGE_ACCOUNT_KEY = os.getenv("AZURE_STORAGE_ACCOUNT_KEY")    # from portal
CONTAINER = "bronze"
HISTORICAL_DIR = "historical"
# -----------------------------------

service_client = DataLakeServiceClient(
    account_url=f"https://{AZURE_STORAGE_ACCOUNT_NAME}.dfs.core.windows.net",
    credential=AZURE_STORAGE_ACCOUNT_KEY
)
file_system = service_client.get_file_system_client(CONTAINER)

# Create directory if not exist (creates virtual folder)
file_system.create_directory(HISTORICAL_DIR)

def upload_json(data, file_name):
    file_client = file_system.get_file_client(f"{HISTORICAL_DIR}/{file_name}")
    file_client.upload_data(json.dumps(data, default=str).encode('utf-8'), overwrite=True)
    print(f"Uploaded {file_name}")

# 1. Customers
customers = []
for _ in range(500):
    customers.append({
        "customer_id": str(uuid.uuid4()),
        "name": fake.name(),
        "email": fake.email(),
        "city": fake.city(),
        "state": fake.state(),
        "signup_date": fake.date_between(start_date='-2y', end_date='today').isoformat()
    })
upload_json(customers, "customers.json")

# 2. Products
categories = ["Electronics", "Clothing", "Books", "Home & Kitchen", "Sports"]
products = []
for _ in range(200):
    products.append({
        "product_id": f"PROD-{uuid.uuid4().hex[:8]}",
        "name": fake.catch_phrase(),
        "category": random.choice(categories),
        "price": round(random.uniform(5, 500), 2),
        "cost": round(random.uniform(2, 200), 2)
    })
upload_json(products, "products.json")

# 3. Orders (historical)
orders = []
for _ in range(2000):
    cust = random.choice(customers)
    prod = random.choice(products)
    order_date = fake.date_time_between(start_date='-6m', end_date='now')
    orders.append({
        "order_id": f"ORD-{uuid.uuid4().hex[:8]}",
        "customer_id": cust["customer_id"],
        "product_id": prod["product_id"],
        "quantity": random.randint(1, 4),
        "price": prod["price"],
        "order_date": order_date.isoformat(),
        "status": random.choice(["Completed", "Cancelled", "Returned"])
    })
upload_json(orders, "orders.json")

# 4. Payments (1:1 with orders)
payments = []
for ord in orders:
    payments.append({
        "payment_id": f"PAY-{uuid.uuid4().hex[:8]}",
        "order_id": ord["order_id"],
        "amount": ord["quantity"] * ord["price"],
        "payment_method": random.choice(["Credit Card", "UPI", "Net Banking", "COD"]),
        "payment_date": (datetime.fromisoformat(ord["order_date"]) + timedelta(minutes=random.randint(1,60))).isoformat()
    })
upload_json(payments, "payments.json")

# 5. Reviews
reviews = []
for _ in range(1000):
    ord = random.choice(orders)
    reviews.append({
        "review_id": f"REV-{uuid.uuid4().hex[:8]}",
        "order_id": ord["order_id"],
        "customer_id": ord["customer_id"],
        "product_id": ord["product_id"],
        "rating": random.randint(1,5),
        "review_text": fake.sentence(),
        "review_date": (datetime.fromisoformat(ord["order_date"]) + timedelta(days=random.randint(1,30))).isoformat()
    })
upload_json(reviews, "reviews.json")

print("Historical data loaded successfully.")
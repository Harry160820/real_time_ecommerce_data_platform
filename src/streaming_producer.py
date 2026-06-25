import json, random, os, uuid, time
from datetime import datetime
from faker import Faker
from azure.storage.filedatalake import DataLakeServiceClient
from dotenv import load_dotenv

load_dotenv()
fake = Faker()

# ---------- CONFIGURATION ----------
AZURE_STORAGE_ACCOUNT_NAME = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")   # your storage account name
AZURE_STORAGE_ACCOUNT_KEY = os.getenv("AZURE_STORAGE_ACCOUNT_KEY")    # from portal
CONTAINER = "bronze"
STREAMING_DIR = "streaming"
# -----------------------------------

# We need a list of known product IDs and customer IDs for realism.
# For simplicity, we’ll generate some fixed IDs. In a real scenario, you'd read these from your master tables.

customer_ids = [str(uuid.uuid4()) for _ in range(100)]  # 100 unique customer IDs
product_ids = [f"PROD-{uuid.uuid4().hex[:8]}" for _ in range(50)]  # 50 unique product IDs

service_client = DataLakeServiceClient(
    account_url=f"https://{AZURE_STORAGE_ACCOUNT_NAME}.dfs.core.windows.net",
    credential=AZURE_STORAGE_ACCOUNT_KEY
)

file_system = service_client.get_file_system_client(CONTAINER)

# Ensure streaming directory exists

try:
    file_system.create_directory(STREAMING_DIR)
except Exception as e:
    print(f"Directory {STREAMING_DIR} may already exist: {e}")

event_types = ["page_view", "add_to_cart", "remove_from_cart", "checkout", "purchase"]

while True:
    for _ in range(random.randint(1, 5)):
        event = {
            "event_id": str(uuid.uuid4()),
            "session_id": f"SESS-{uuid.uuid4().hex[:6]}",
            "customer_id": None if random.random() < 0.4 else random.choice(customer_ids),
            "product_id": random.choice(product_ids),
            "event_type": random.choice(event_types),
            "timestamp": datetime.utcnow().isoformat()
        }
        file_name = f"{STREAMING_DIR}/event_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}.json"
        try:
            file_system.get_file_client(file_name).upload_data(json.dumps(event, default=str), overwrite=True)
            print(f"Uploaded {file_name}")
        except Exception as e:
            print(f"Failed to upload: {e}")
    time.sleep(15)

    
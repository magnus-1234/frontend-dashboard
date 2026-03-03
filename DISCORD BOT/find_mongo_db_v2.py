import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Try to load .env from the root directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

uri = os.getenv('MONGO_URI')
if not uri:
    # Try current directory .env just in case
    load_dotenv()
    uri = os.getenv('MONGO_URI')

if not uri:
    print("Error: MONGO_URI not found in environment or .env file")
    exit(1)

client = MongoClient(uri, serverSelectionTimeoutMS=10000)

try:
    print("Databases available:")
    for db_name in client.list_database_names():
        db = client[db_name]
        has_coll = 'auto_redeem_members' in db.list_collection_names()
        count = db['auto_redeem_members'].count_documents({}) if has_coll else 0
        print(f"- {db_name} (auto_redeem_members: {count if has_coll else 'NOT FOUND'})")
except Exception as e:
    print(f"Error: {e}")

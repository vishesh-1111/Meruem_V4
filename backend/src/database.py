import motor.motor_asyncio
import os
from dotenv import load_dotenv
load_dotenv()
remote_url = os.getenv("MONGODB_URL")
# print(remote_url)
client = motor.motor_asyncio.AsyncIOMotorClient(remote_url)
db = client["Meruem_v4"]



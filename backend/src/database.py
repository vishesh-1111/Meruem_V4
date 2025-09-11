import motor.motor_asyncio
remote_url = "mongodb://localhost:27017"
client = motor.motor_asyncio.AsyncIOMotorClient(remote_url)
db = client["Meruem_v4"]



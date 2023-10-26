import os
from dotenv import load_dotenv

load_dotenv()
print(os.getenv("JWT_SECRET"))
print(os.getenv("DATABASE_URL"))
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN        = os.getenv("TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))
PORT         = 5000

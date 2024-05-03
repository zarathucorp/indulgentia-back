from dotenv import load_dotenv
import os

load_dotenv()

current_mode = os.getenv("RUNNING_MODE")

if current_mode == "prod":
    pass
elif current_mode == "dev":
    pass

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

from env import SUPABASE_URL, SUPABASE_ANON_KEY
from supabase import create_client, Client

url: str = SUPABASE_URL
key: str = SUPABASE_ANON_KEY
supabase: Client = create_client(url, key)

supabase.auth.sign_out

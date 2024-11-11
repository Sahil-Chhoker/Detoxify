import os
from dotenv import load_dotenv
from supabase import create_client, Client
from core.config import settings
load_dotenv()


def get_supabase_config():
    url = settings.SUPABASE_URL
    key = settings.SUPABASE_KEY

    if not url or not key:
        raise ValueError(
            "Missing Supabase configuration. "
            "Please ensure SUPABASE_URL and SUPABASE_KEY are set in your .env file"
        )
    return url, key


try:
    supabase_url, supabase_key = get_supabase_config()
    print(f"Successfully loaded Supabase configuration")
except ValueError as e:
    print(f"Error: {e}")


try:
    SUPABASE: Client = create_client(supabase_url, supabase_key)
    print(f"Successfully connected to Supabase")
except Exception as e:
    print(f"Error: {e}")

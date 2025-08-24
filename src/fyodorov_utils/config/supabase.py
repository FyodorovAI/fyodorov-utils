from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions
from .config import Settings

settings = Settings()


def get_supabase(jwt: str = None) -> Client:
    print("Getting supabase client")
    if jwt and jwt != "" and len(jwt.split(".")) == 3:
        return create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY,
            options=ClientOptions(headers={"Authorization": f"Bearer {jwt}"}),
        )
    else:
        return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

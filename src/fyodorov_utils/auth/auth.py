from fastapi import Depends, HTTPException, Security, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from starlette.status import HTTP_403_FORBIDDEN
from datetime import datetime, timedelta
from fyodorov_utils.decorators.logging import error_handler
from fyodorov_utils.config.config import Settings
from fyodorov_llm_agents.db import get_db_client

settings = Settings()
security = HTTPBearer()

# Supabase authentication client is removed. A new authentication system is required.
# For now, direct Supabase auth calls will be commented out or raise errors.



async def authenticate(credentials: HTTPAuthorizationCredentials = Security(security)):
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated",
        )
        # Perform additional validation checks as needed (e.g., expiration, issuer, audience)
        print(f"Decoded JWT payload: {payload}")
        return payload  # Or a user object based on the payload
    except jwt.PyJWTError as e:
        print(f"JWT error: {str(e)}")
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
        ) from e


# User auth functions
@error_handler
async def sign_up(
    email: str = Body(...), password: str = Body(...), invite_code: str = Body(...)
):
    # Check if invite code exists
    async with get_db_client() as db:
        invite_code_data = await db.fetch_one(
            "SELECT nr_uses, max_uses FROM public.invite_codes WHERE code = $1", invite_code
        )
    
    if not invite_code_data:
        raise HTTPException(status_code=401, detail="Invalid invite code")

    nr_uses = invite_code_data["nr_uses"]
    max_uses = invite_code_data["max_uses"]

    if max_uses != 0 and nr_uses >= max_uses: # 0 means unlimited uses
        raise HTTPException(
            status_code=401, detail="Invite code has reached maximum usage"
        )

    # --- Supabase authentication removed ---
    # user = supabase.auth.sign_up(
    #     {
    #         "email": email,
    #         "password": password,
    #         "options": {
    #             "data": {
    #                 "invite_code": invite_code,
    #             }
    #         },
    #     }
    # )
    # Placeholder for generic user creation/authentication
    print(f"User sign-up attempted for {email} with invite code {invite_code}. Supabase auth is currently disabled.")
    # You would integrate your new user authentication system here.
    # For now, we'll simulate success for invite code logic.
    
    # Increment nr_uses in invite_codes table
    nr_uses += 1
    async with get_db_client() as db:
        res = await db.update(
            "invite_codes",
            {"nr_uses": nr_uses},
            {"code": invite_code}
        )
    print(f"response when updating invite code nr uses: {res}")

    # Return a dummy JWT for now, as actual user creation is disabled
    dummy_user_payload = {"sub": email, "session_id": "dummy_session_id", "email": email}
    dummy_jwt = generate_jwt(dummy_user_payload)
    return {"message": "User created successfully (auth disabled)", "jwt": dummy_jwt}


@error_handler
async def sign_in(email: str = Body(...), password: str = Body(...)):
    try:
        # --- Supabase authentication removed ---
        # user = supabase.auth.sign_in_with_password(
        #     {
        #         "email": email,
        #         "password": password,
        #     }
        # )
        # Placeholder for generic user authentication
        print(f"User sign-in attempted for {email}. Supabase auth is currently disabled.")
        # You would integrate your new user authentication system here.
        # For now, we'll simulate success with a dummy JWT.
        
        # Simulate successful authentication for JWT generation
        dummy_user_payload = {"sub": email, "session_id": "dummy_session_id", "email": email}
        dummy_jwt = generate_jwt(dummy_user_payload)
        
    except Exception as e: # Catch all exceptions for now, as gotrue.errors.AuthApiError is gone
        print(f"Error signing in: {type(e)} {str(e)}")
        raise HTTPException(status_code=401, detail="Error signing in (auth disabled)")
    return {"message": "User signed in successfully (auth disabled)", "jwt": dummy_jwt}


@error_handler
async def create_api_key(expiration: int = 15, user=Depends(authenticate)):
    print(f"[create_api_key] expiration: {expiration}")
    api_key = generate_jwt(user, expiration)
    return {"message": "API key created successfully", "api_key": api_key}


def generate_jwt(user, days_to_expiry: int = 30) -> str:
    if days_to_expiry > 90 or days_to_expiry < 1:
        days_to_expiry = 30
    user["iat"] = datetime.utcnow()
    expiry = datetime.utcnow() + timedelta(days=days_to_expiry)
    print(f"Expiry: {expiry} \nNow: {datetime.utcnow()}")
    user["exp"] = expiry
    token = jwt.encode(user, settings.JWT_SECRET, algorithm="HS256")
    return token

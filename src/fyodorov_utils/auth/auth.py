from fastapi import Depends, HTTPException, Security, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from starlette.status import HTTP_403_FORBIDDEN
import gotrue
from datetime import datetime, timedelta
from fyodorov_utils.decorators.logging import error_handler
from fyodorov_utils.config.config import Settings
from fyodorov_utils.config.supabase import get_supabase

settings = Settings()
security = HTTPBearer()
supabase = get_supabase()


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
    invite_code_check = (
        supabase.from_("invite_codes")
        .select("nr_uses, max_uses")
        .eq("code", invite_code)
        .execute()
    )
    if not invite_code_check.data:
        raise HTTPException(status_code=401, detail="Invalid invite code")

    invite_code_data = invite_code_check.data[0]
    nr_uses = invite_code_data["nr_uses"]
    max_uses = invite_code_data["max_uses"]

    if nr_uses >= max_uses:
        raise HTTPException(
            status_code=401, detail="Invite code has reached maximum usage"
        )

    user = supabase.auth.sign_up(
        {
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "invite_code": invite_code,
                }
            },
        }
    )
    # Increment nr_uses in invite_codes table
    nr_uses += 1
    res = (
        supabase.from_("invite_codes")
        .update({"nr_uses": nr_uses})
        .eq("code", invite_code)
        .execute()
    )
    print(f"response when updating invite code nr uses: {res}")

    return {"message": "User created successfully", "jwt": user.session.access_token}


@error_handler
async def sign_in(email: str = Body(...), password: str = Body(...)):
    try:
        user = supabase.auth.sign_in_with_password(
            {
                "email": email,
                "password": password,
            }
        )
    except gotrue.errors.AuthApiError as e:
        print(f"Error signing in - invalid credentials: {str(e)} - {type(e)}")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    except Exception as e:
        print(f"Error signing in: {str(e)} - {type(e)}")
        raise HTTPException(status_code=401, detail="Error signing in")
    return {"message": "User signed in successfully", "jwt": user.session.access_token}


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

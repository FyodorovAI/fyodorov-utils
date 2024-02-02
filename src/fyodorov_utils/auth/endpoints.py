from fastapi import FastAPI, Body, Depends
from .auth import sign_up, sign_in, create_api_key, authenticate

users_app = FastAPI(title="Fyodorov-Auth", description="Common auth endpoints for Fyodorov services", version="0.0.1")

@users_app.get('/')
async def root(user = Depends(authenticate)):
    print(f"Logged in as: {user}")
    return {"message": "logged in as: " + user.email}

@users_app.post('/sign_up')
async def sign_up_endpoint(email: str = Body(...), password: str = Body(...), invite_code: str = Body(...), user = Depends(authenticate)):
    return await sign_up(email, password, invite_code, user)

@users_app.post('/sign_in')
async def sign_in_endpoint(email: str = Body(...), password: str = Body(...), user = Depends(authenticate)):
    return await sign_in(email, password, user)

@users_app.post('/create_api_key')
async def create_api_key_endpoint(expiration: int = 15, user = Depends(authenticate)):
    return await create_api_key(expiration, user)

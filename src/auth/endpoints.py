from fastapi import FastAPI
from .auth import sign_up, sign_in, create_api_key

users_app = FastAPI()

@app.post('/sign_up')
def sign_up_endpoint(*args, **kwargs):
    return sign_up(*args, **kwargs)

@app.post('/sign_in')
def sign_in_endpoint(*args, **kwargs):
    return sign_in(*args, **kwargs)

@app.post('/create_api_key')
def create_api_key_endpoint(*args, **kwargs):
    return create_api_key(*args, **kwargs)

from pwdlib import PasswordHash
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from pwdlib.exceptions import UnknownHashError
import jwt
from jwt.exceptions import InvalidTokenError
import datetime
from dotenv import load_dotenv
import os

load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
refresh_scheme=APIKeyHeader(name="X-Refresh-Token", description="Insert your refresh token", auto_error=True)
SECRET_KEY = os.getenv("SECRET_KEY")
REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY")

password_hasher = PasswordHash.recommended()

def hashing_password(password: str) -> str:
    return password_hasher.hash(password)

def verify_password_hash(password: str, hashed_password: str) -> bool:
    try:
        return password_hasher.verify(password, hashed_password)
    except UnknownHashError:
        return False

def create_tokens(user_id, username):
    access_payload={
        "user_id": user_id,
        "username": username,
        "type": "access",
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=15)
    }

    refresh_payload={
        "user_id": user_id,
        "type": "refresh",
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7)
    }
    access_token = jwt.encode(access_payload, SECRET_KEY, algorithm="HS256")
    refresh_token = jwt.encode(refresh_payload, REFRESH_SECRET_KEY, algorithm="HS256")

    return access_token, refresh_token

def check_access_token(access_token: str = Depends(oauth2_scheme)) -> int:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=["HS256"])

        if payload.get("type") != "access":
            raise credentials_exception
        return payload.get("user_id")
         
    except InvalidTokenError:
        raise credentials_exception
        
def check_refresh_token(refresh_token: str = Depends(refresh_scheme)) -> int:

    refresh_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Refresh Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(refresh_token, REFRESH_SECRET_KEY, algorithms=["HS256"])
        if payload.get("type") != "refresh":
            raise refresh_exception
        return payload.get("user_id")
    
    except InvalidTokenError:
        raise refresh_exception
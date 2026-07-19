from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from models import User
from pydantic_models import UserCreate, UserResponse, TokenResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_session
from credentials import hashing_password, verify_password_hash, create_tokens, check_refresh_token

app = FastAPI()

origins = [
    "http://127.0.0.1:5500"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       
    allow_credentials=True,          
    allow_headers=["*"],   
    allow_methods=["*"]         
)

@app.post('/register', response_model=UserResponse)
async def register_user(user_data: UserCreate, session: AsyncSession=Depends(get_session)):
    
    result = await session.execute(
        select(User).where(User.username == user_data.username)
    )
    
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=409, detail='Username already exists')
    
    password_hashed = hashing_password(user_data.password)

    user_created = User(
        name=user_data.name,
        username=user_data.username,
        password_hash=password_hashed
    )

    session.add(user_created)

    await session.commit()
    await session.refresh(user_created)

    return UserResponse(
        name=user_created.name,
        username=user_created.username,
        active=user_created.active
    )

@app.post('/login', response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm=Depends(),
      session: AsyncSession=Depends(get_session)
      ):
    error_credentials=HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Invalid username or password',
        headers={"WWW-Authenticate": "Bearer"}
        )
    
    result = await session.execute(
        select(User).where(User.username == form_data.username)
    )
    extrated_user = result.scalar_one_or_none()
    if not extrated_user:
        raise error_credentials
    
    password_hash = extrated_user.password_hash
    is_valid = verify_password_hash(form_data.password, password_hash)

    if not is_valid:
        raise error_credentials
    
    access_token, refresh_token = create_tokens(extrated_user.id, extrated_user.username)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )

@app.post('/refresh', response_model=TokenResponse)
async def refresh(
    user_id = Depends(check_refresh_token),
    session: AsyncSession = Depends(get_session)
    ):
    
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    extracted_user = result.scalar_one_or_none()

    if not extracted_user:
        raise HTTPException(status_code=401, detail='Invalid user')
    access_token, refresh_token = create_tokens(user_id, extracted_user.username)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )
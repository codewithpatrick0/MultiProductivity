from fastapi import FastAPI, Depends, HTTPException, status, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from models import User, Task
from pydantic_models import UserCreate, UserResponse, TokenResponse, TaskResponse, TaskCreate, TaskEdit
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_session
from credentials import hashing_password, verify_password_hash, create_tokens, check_access_token, check_refresh_token

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

@app.post('/register', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
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

@app.post('/tasks', response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def define_task(
    task: TaskCreate,
    user_id: int = Depends(check_access_token),
    session: AsyncSession = Depends(get_session)
):
    new_task = Task(id_user=user_id, title=task.title, info=task.info)

    try:
        session.add(new_task)
        await session.commit()
        await session.refresh(new_task)

        return TaskResponse(
            id=new_task.id,
            id_user=user_id,
            title=new_task.title,
            info=new_task.info
        )
    except Exception as e:
        await session.rollback()
        print(f'Error interno: {e}')

        raise HTTPException(status_code=400, detail='It could not be saved to the database.')

@app.get('/tasks', response_model=list[TaskResponse])
async def obtain_tasks(
    user_id: int = Depends(check_access_token),
    session: AsyncSession = Depends(get_session)
):
    try:
        results = await session.execute(
            select(Task).where(Task.id_user == user_id)
        )
        
        extracted_tasks = results.scalars().all()
        return extracted_tasks
    
    except Exception as e:
        print(f'Error interno: {e}')
        raise HTTPException(status_code=500, detail='The tasks could not be retrieved.')
    
@app.patch('/tasks/{task_id}', response_model=TaskResponse)
async def edit_task(
    task_id: int,
    task: TaskEdit,
    user_id: int = Depends(check_access_token),
    session: AsyncSession = Depends(get_session)
):
    query = await session.execute(
        select(Task).where(
            Task.id==task_id,
            Task.id_user==user_id
            )
    )
    extracted_task = query.scalar_one_or_none()

    if not extracted_task:
        raise HTTPException(status_code=404, detail='The ID does not exist or the task does not belong to you.')
    
    if task.title :
        extracted_task.title = task.title
    if task.info:
        extracted_task.info = task.info
    if task.status:
        extracted_task.status = task.status

    await session.commit()
    await session.refresh(extracted_task)

    return TaskResponse(
        id=extracted_task.id,
        id_user=user_id,
        title=extracted_task.title,
        info=extracted_task.info,
        status=extracted_task.status
    )

@app.delete('/tasks/{task_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    user_id: int = Depends(check_access_token),
    session: AsyncSession = Depends(get_session)
):
    query = await session.execute(
        select(Task).where(
            Task.id==task_id,
            Task.id_user==user_id
            )
    )
    extracted_task = query.scalar_one_or_none()

    if not extracted_task:
        raise HTTPException(status_code=404, detail='Task not found.')
    
    await session.delete(extracted_task)
    await session.commit()

    return Response()
    
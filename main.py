from fastapi import FastAPI, Depends, HTTPException, status, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from models import User, Task, Category
from pydantic_models import UserCreate, UserResponse, TokenResponse, TaskResponse, TaskCreate, TaskEdit, CategoryCreate, CategoryResponse, CategoryEdit
from sqlalchemy import select, or_
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
    if not task.id_category:
        query_others = await session.execute(
            select(Category).where(
                Category.name=="Others", Category.id_user.is_(None))
        )

        others_category = query_others.scalar_one_or_none()
        if not others_category:
            raise HTTPException(status_code=500, detail="Default 'Others' category was not found.")

        new_task = Task(id_user=user_id, id_category=others_category.id, title=task.title, info=task.info)
    else:
        new_task = Task(id_user=user_id, id_category=task.id_category, title=task.title, info=task.info)

    try:
        session.add(new_task)
        await session.commit()
        await session.refresh(new_task)

        return TaskResponse(
            id=new_task.id,
            id_user=user_id,
            id_category=new_task.id_category,
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
    if task.id_category:
        extracted_task.id_category = task.id_category

    await session.commit()
    await session.refresh(extracted_task)

    return TaskResponse(
        id=extracted_task.id,
        id_user=user_id,
        id_category=extracted_task.id_category,
        title=extracted_task.title,
        info=extracted_task.info,
        status=extracted_task.status
    )

@app.delete('/tasks/{task_id}')
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

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.post('/categories', response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def define_category(
    category: CategoryCreate,
    user_id: int = Depends(check_access_token),
    session: AsyncSession = Depends(get_session)
):
    new_category = Category(id_user=user_id, name=category.name, color=category.color)

    try:
        session.add(new_category)
        await session.commit()
        await session.refresh(new_category)

        return CategoryResponse(
            id=new_category.id,
            id_user=user_id,
            name=new_category.name,
            color=new_category.color
        )
    except Exception as e:
        await session.rollback()
        print(f'Error interno: {e}')

        raise HTTPException(status_code=400, detail='It could not be saved to the database.')

@app.get('/categories', response_model=list[CategoryResponse])
async def obtain_categories(
    user_id: int = Depends(check_access_token),
    session: AsyncSession = Depends(get_session)
):
    try:
        results = await session.execute(
            select(Category).where(
                or_(Category.id_user == user_id, Category.id_user.is_(None))
            )
        )

        extracted_categories = results.scalars().all()
        return extracted_categories

    except Exception as e:
        print(f'Error interno: {e}')
        raise HTTPException(status_code=500, detail='The categories could not be retrieved.')

@app.patch('/categories/{category_id}', response_model=CategoryResponse)
async def edit_category(
    category_id: int,
    category: CategoryEdit,
    user_id: int = Depends(check_access_token),
    session: AsyncSession = Depends(get_session)
):
    query = await session.execute(
        select(Category).where(
            Category.id == category_id,
            Category.id_user == user_id
            )
    )
    extracted_category = query.scalar_one_or_none()

    if not extracted_category:
        raise HTTPException(status_code=404, detail='The ID does not exist or the category does not belong to you.')

    if category.name:
        extracted_category.name = category.name
    if category.color:
        extracted_category.color = category.color

    await session.commit()
    await session.refresh(extracted_category)

    return CategoryResponse(
        id=extracted_category.id,
        id_user=user_id,
        name=extracted_category.name,
        color=extracted_category.color
    )

@app.delete('/categories/{category_id}')
async def delete_category(
    category_id: int,
    user_id: int = Depends(check_access_token),
    session: AsyncSession = Depends(get_session)
):
    query = await session.execute(
        select(Category).where(
            Category.id == category_id,
            Category.id_user == user_id
            )
    )
    extracted_category = query.scalar_one_or_none()

    if not extracted_category:
        raise HTTPException(status_code=404, detail='Category not found or does not belong to you.')

    others_query = await session.execute(
        select(Category).where(
            Category.name == 'Others',
            Category.id_user.is_(None)
            )
    )
    others_category = others_query.scalar_one_or_none()

    if not others_category:
        raise HTTPException(status_code=500, detail="Default 'Others' category was not found.")

    tasks_query = await session.execute(
        select(Task).where(
            Task.id_category == category_id,
            Task.id_user == user_id
            )
    )
    tasks_to_reassign = tasks_query.scalars().all()

    for task in tasks_to_reassign:
        task.id_category = others_category.id

    await session.delete(extracted_category)
    await session.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)

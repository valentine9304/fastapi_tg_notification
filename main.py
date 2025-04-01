from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas import TaskPost, TaskPatch, TaskGet, MessageGet, MessagePost, TokenRequest, TokenResponse
from api.crud import create_task, create_message, get_task, update_task, get_all_tasks, get_all_messages, get_token
from api.auth import get_current_user
from api.db import Base, async_session, engine


app = FastAPI(title="To Do", openapi_url="/openapi.json")


@app.on_event("startup")
async def startup():
    await init_db()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    async with async_session() as session:
        yield session


@app.post("/tasks/create", response_model=TaskGet, status_code=201,
          summary="Создать новую задачу",
          description="Добавляет новую задачу в список с указанием времени выполнения и описанием.")
async def create_new_task(task: TaskPost, db: AsyncSession = Depends(get_db), user_id: str = Depends(get_current_user)):
    return await create_task(db, task)


@app.get("/tasks/{task_id}", response_model=TaskGet,
         summary="Получить задачу по ID",
         description="Возвращает данные о задаче по её идентификатору.")
async def read_task(task_id: int, db: AsyncSession = Depends(get_db), user_id: str = Depends(get_current_user)):
    task = await get_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.patch("/tasks/{task_id}/update", response_model=TaskGet,
           summary="Обновить задачу",
           description="Обновляет время выполнения и описание существующей задачи.")
async def update_existing_task(task_id: int, task: TaskPatch, db: AsyncSession = Depends(get_db), user_id: str = Depends(get_current_user)):
    updated_task = await update_task(db, task_id, task)
    if updated_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated_task


@app.get("/tasks", response_model=list[TaskGet],
         summary="Получить список задач",
         description="Возвращает список всех задач с их временем выполнения и описанием.")
async def read_all_tasks(db: AsyncSession = Depends(get_db), user_id: str = Depends(get_current_user)):
    return await get_all_tasks(db)


@app.post("/messages/create", response_model=MessageGet, status_code=201,
          summary="Создать новое сообщение",
          description="Добавляет сообщение и отправить его через ТГ по telegram_user_id.")
async def create_new_message(message: MessagePost, db: AsyncSession = Depends(get_db), user_id: str = Depends(get_current_user)):
    return await create_message(db, message)


@app.get("/messages", response_model=list[MessageGet],
         summary="Получить список всех сообщений",
         description="Возвращает список всех сообщений с их статусами и данными.")
async def read_all_messages(db: AsyncSession = Depends(get_db), user_id: str = Depends(get_current_user)):
    return await get_all_messages(db)


@app.post("/token", response_model=TokenResponse,
          summary="Получить JWT-токен",
          description="Выдаёт JWT-токен для пользователя 'admin'.")
async def token_endpoint(request: TokenRequest):
    return await get_token(request)

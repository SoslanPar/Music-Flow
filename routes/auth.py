import json
import os
import secrets
import httpx
from fastapi import APIRouter, HTTPException, Request, Response, Depends, Cookie
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field
from services.users_services import UserServices
from db.base import Database
from models.Users import Users
from dotenv import load_dotenv

load_dotenv()
DOMAIN = os.getenv("DOMAIN")
CLIENT_ID = os.getenv("YANDEX_CLIENT_ID")
CLIENT_SECRET = os.getenv("YANDEX_CLIENT_SECRET")

db = Database()

router = APIRouter(prefix="/auth")


# ============ Pydantic Models ============

class SignInRequest(BaseModel):
    """Модель запроса на вход"""
    nickname: str = Field(..., min_length=1, max_length=100, description="Email или username")
    password: str = Field(..., min_length=4, max_length=100, description="Пароль")


class SignUpRequest(BaseModel):
    """Модель запроса на регистрацию"""
    email: EmailStr = Field(..., description="Email пользователя")
    username: str = Field(..., min_length=3, max_length=50, description="Имя пользователя")
    password: str = Field(..., min_length=6, max_length=100, description="Пароль (минимум 6 символов)")
    birthday: str | None = Field(default=None, description="Дата рождения")


class AuthResponse(BaseModel):
    """Модель ответа авторизации"""
    status: str
    user_id: str
    username: str
    action: str
    success: bool


async def get_access_token(code: str) -> str:
    """
    Обмен кода авторизации на токен доступа (асинхронно через httpx).
    """
    token_url = "https://oauth.yandex.ru/token"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=data)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Ошибка при получении токена Яндекса")
        return response.json().get("access_token")


@router.get("/get_cookie")
async def get_cookie(request: Request):
    try:
        cookies = request.cookies
        return Response(content=json.dumps(cookies), status_code=200)
    except Exception as e:
        return Response(content=json.dumps({"error": str(e)}), status_code=500)


@router.get("/current-user")
async def get_current_user(user_id: str = Cookie(None)):
    """Получить текущего авторизованного пользователя"""
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    async with db.session_factory() as session:
        user = await session.get(Users, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return {"id": str(user.id), "username": user.username}
    

@router.post("/sign-in", response_model=AuthResponse)
async def auth_login(credentials: SignInRequest):
    """
    Вход в систему по email/username и паролю.
    Пароль хешируется на сервере с использованием bcrypt.
    """
    try:
        user_services = UserServices(db)
        user = await user_services.login(credentials.nickname, credentials.password)

        if user:
            return AuthResponse(
                status="authenticated",
                user_id=str(user.id),
                username=user.username,
                action="login",
                success=True
            )
        
        raise HTTPException(status_code=401, detail="Неправильный логин или пароль")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка авторизации: {str(e)}")


@router.post("/sign-up", response_model=AuthResponse)
async def auth_register(credentials: SignUpRequest):
    """
    Регистрация нового пользователя.
    Пароль хешируется на сервере с использованием bcrypt.
    """
    try:
        user_services = UserServices(db)
        
        result = await user_services.create_new_user(
            email=credentials.email,
            password=credentials.password,
            username=credentials.username,
            birthday=credentials.birthday,
            rooms_list=[],
            yandex_token=None
        )
        
        return AuthResponse(
            status="registered",
            user_id=result["user_id"],
            username=result["username"],
            action="register",
            success=True
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка регистрации: {str(e)}")
    

@router.get("/check_token")
async def check_token(code: str):
    """
    Авторизация через Яндекс OAuth.
    Если пользователь существует - логиним, иначе создаём нового.
    """
    try:
        user_services = UserServices(db)
        token = await get_access_token(code)
        
        # Проверяем, есть ли пользователь с таким токеном
        existing_user = await user_services.check_yandex_token(token)
        
        if existing_user:
            return AuthResponse(
                status="authenticated",
                user_id=str(existing_user.id),
                username=existing_user.username,
                action="login",
                success=True
            )

        # Получаем профиль из Яндекса и создаём нового пользователя
        profile = await user_services.get_yandex_profile(token)
        login = profile.get("login")
        email = profile.get("default_email")
        birthday = profile.get("birthday")
        
        if not login:
            raise HTTPException(status_code=400, detail="Не удалось получить логин Яндекса")
        
        if not email:
            # Генерируем уникальный email если его нет
            email = f"{login}@yandex.ru"

        # Генерируем безопасный случайный пароль для Яндекс-пользователей
        random_password = secrets.token_urlsafe(32)

        new_user = await user_services.create_new_user(
            email=email,
            password=random_password,  # Безопасный случайный пароль
            username=login,
            birthday=birthday,
            yandex_token=token,
            rooms_list=[],
        )

        return AuthResponse(
            status="registered",
            user_id=new_user["user_id"],
            username=new_user["username"],
            action="register",
            success=True
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")
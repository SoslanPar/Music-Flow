import asyncio

import sqlalchemy
from sqlalchemy import select, or_, and_

from models.Users import Users  # Импорт всех моделей
from models.Tokens import Tokens

from db.base import Database
# from db.base import engine, Base, AsyncSession

from pydantic import EmailStr

import jwt
import secrets
import httpx

from passlib.hash import bcrypt
from fastapi import HTTPException


class UserServices:
    def __init__(self, db: Database):
        self.db = db


    async def create_token(self, obj):
        secret_key = secrets.token_urlsafe(20)

        token = jwt.encode(obj, secret_key, algorithm='HS256')
        return token    


    def hash_password(self, password: str) -> str:
        """Хеширует пароль с использованием bcrypt"""
        return bcrypt.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Проверяет пароль против хеша bcrypt"""
        try:
            return bcrypt.verify(plain_password, hashed_password)
        except Exception:
            return False

    async def get_all(self):
        async with self.db.session_factory() as session:
            result = await session.execute(select(Users))
            result = result.scalars().all()
            result = [{'id': str(i.id), 
                     'email': i.email, 
                     'hashed_password': i.hashed_password, 
                     'username': i.username,
                     'birthday': i.birthday,
                     'rooms_list': list(i.rooms_list),
                     'yandex_token': i.yandex_token
                    }
                    for i in result]
            print(result)
            return result
        
    async def create_new_user(self, email: str, password: str, username: str, birthday: str = None, rooms_list: list = None, yandex_token: str = None):
        """Создаёт нового пользователя с безопасным хешированием пароля"""
        async with self.db.session_factory() as session:
            # Проверяем, существует ли пользователь с таким email или username
            existing = await session.execute(
                select(Users).where(
                    or_(Users.email == email, Users.username == username)
                )
            )
            if existing.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="Пользователь с таким email или username уже существует")
            
            hashed_password = self.hash_password(password)
            new_user = Users(
                email=email,
                hashed_password=hashed_password,
                username=username,
                birthday=birthday or "",
                rooms_list=rooms_list or [],
                yandex_token=yandex_token
            )
            
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)  # Обновляем объект для получения ID
            
            return {'status': 'success', 'user_id': str(new_user.id), 'username': new_user.username}
    
    async def login(self, nickname: str, password: str):
        """Авторизация пользователя с проверкой bcrypt хеша"""
        async with self.db.session_factory() as session:
            # Ищем пользователя по email или username
            result = await session.execute(
                select(Users).where(
                    or_(Users.email == nickname, Users.username == nickname)
                )
            )
            user = result.scalar_one_or_none()
            
            if user and self.verify_password(password, user.hashed_password):
                return user
            return None
    
    async def login_by_yandex_token(self, yandex_token: str):
        """Авторизация по Яндекс токену"""
        async with self.db.session_factory() as session:
            result = await session.execute(
                select(Users).where(Users.yandex_token == yandex_token)
            )
            return result.scalar_one_or_none()
        
    async def add_room(self, room_id: str, user_id: str):
        async with self.db.session_factory() as session:
            result = await session.execute(select(Users).where(Users.id == user_id))
            user = result.scalar_one_or_none()
            if user:
                rooms = list(user.rooms_list) if user.rooms_list else []
                if room_id not in rooms:
                    rooms.append(room_id)
                    user.rooms_list = rooms
                    await session.commit()
            return user
    
    async def remove_room(self, room_id: str, user_id: str):
        """Удалить комнату из списка пользователя"""
        async with self.db.session_factory() as session:
            result = await session.execute(select(Users).where(Users.id == user_id))
            user = result.scalar_one_or_none()
            if user:
                rooms = list(user.rooms_list) if user.rooms_list else []
                if room_id in rooms:
                    rooms.remove(room_id)
                    user.rooms_list = rooms
                    await session.commit()
                    return True
            return False
    
    async def get_user_rooms(self, user_id: str) -> list:
        """Получить список комнат пользователя"""
        async with self.db.session_factory() as session:
            result = await session.execute(select(Users).where(Users.id == user_id))
            user = result.scalar_one_or_none()
            if user and user.rooms_list:
                return list(user.rooms_list)
            return []
    
    async def get_yandex_token_by_user_id(self, user_id: str):
        async with self.db.session_factory() as session:
            result = await session.execute(
                select(Users).where(Users.id == user_id)
            )
            token = result.scalar_one_or_none()
            # print(f'toks = {token}')
            return token.yandex_token
        

    async def check_yandex_token(self, yandex_token: str):
        """Проверяет наличие Яндекс токена в БД"""
        async with self.db.session_factory() as session:
            print('222')
            result = await session.execute(
                select(Users).where(Users.yandex_token == yandex_token)
            )
            x = result.scalar_one_or_none()
            return x
        
    async def get_yandex_profile(self, token: str) -> dict:
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"OAuth {token}"}
            response = await client.get("https://login.yandex.ru/info", headers=headers)
            if response.status_code != 200:
                raise HTTPException(
                    status_code=401, detail="Не удалось получить данные профиля Яндекса"
                )
            return response.json()
        
    async def get_users_from_room(self, list_id: list) -> dict:
        users = {}
        async with self.db.session_factory() as session:
            print('222')
            for user_id in list_id:
                result = await session.execute(
                    select(Users).where(Users.id == user_id)
                )
                user = result.scalar_one_or_none()
                users[user_id] = user.username
            return users

        
if __name__ == '__main__':
    d = Database()
    b = UserServices(d)
    
    # asyncio.run(b.create_new_user(email="artem.com", password="1234567", birthday="12.06.2005", username="1neplay"))
    asyncio.run(b.get_yandex_token_by_user_id('d63709db-3ec0-433c-b549-a49e771778f1'))
    # b.create_database()
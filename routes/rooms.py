import json
import os
import asyncio
import sqlalchemy
from yandex_music import Client
from fastapi import APIRouter, HTTPException, Request, Response, Depends
from fastapi.responses import (HTMLResponse, RedirectResponse, JSONResponse)
from fastapi.templating import Jinja2Templates
from aiocache import cached, Cache
from aiocache.serializers import JsonSerializer
from services.rooms_services import Rooms, RoomsServices
from services.users_services import UserServices
from db.base import Database
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor


db = Database()
load_dotenv()
templates = Jinja2Templates(directory="templates")


DOMAIN = os.getenv("DOMAIN")
OAUTH_TOKEN = os.getenv("OAUTH_TOKEN")

# Пул потоков для синхронных операций Yandex Music API
executor = ThreadPoolExecutor(max_workers=10)

# Кэш для информации о треках (TTL 5 минут)
track_info_cache = Cache(Cache.MEMORY, serializer=JsonSerializer())


def _get_track_info_sync(track_id: str, client: Client) -> dict:
    """Синхронное получение информации о треке"""
    track = client.tracks(track_id)[0]
    return {
        "title": track.title,
        "artist": ", ".join(artist.name for artist in track.artists),
        "cover": f"https://{track.cover_uri.replace('%%', '50x50')}",
        "duration": track.duration_ms / 1000 if track.duration_ms else None
    }


async def get_track_info_cached(track_id: str) -> dict:
    """Получение информации о треке с кэшированием"""
    cache_key = f"track_info:{track_id}"
    
    # Проверяем кэш
    cached_info = await track_info_cache.get(cache_key)
    if cached_info:
        return cached_info
    
    # Если нет в кэше - получаем из API в отдельном потоке
    loop = asyncio.get_event_loop()
    client = Client(OAUTH_TOKEN).init()
    track_info = await loop.run_in_executor(executor, _get_track_info_sync, track_id, client)
    
    # Сохраняем в кэш на 5 минут
    await track_info_cache.set(cache_key, track_info, ttl=300)
    
    return track_info



router = APIRouter(prefix="/rooms")


@router.get("/{room_id}", response_class=HTMLResponse)
async def get_room_page(request: Request, room_id: str):
    # Проверяем существование комнаты
    async with db.session_factory() as session:

        room = await session.get(Rooms, room_id)
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")
    cookies = request.cookies
    # print(f'Cookie in room: {cookies}')
    return templates.TemplateResponse(
        "room.html", {"request": request, "room_id": room_id}
    )

@router.post("/create")
async def create_room(
    request: Request, name_rooms: str = None, db: Database = Depends(Database)
):
    if not (name_rooms):
        return Response(
            content=json.dumps(
                {"Status": "Error", "Message": "Введите название комнаты"}
            ),
            status_code=500,
        )
    cookies = request.cookies
    # print(cookies)
    if "user_id" not in cookies and not (cookies["user_id"]):
        # print(1)
        return Response(
            content=json.dumps({"Status": "Error", "Message": "Авторизуйтесь"}),
            status_code=500,
        )
    resp = RoomsServices(db)
    user_model = UserServices(db)
    # print(name_rooms)
    try:
        done = await resp.create_room(name_rooms, cookies["user_id"])
        op = await user_model.add_room(str(done["id"]), cookies["user_id"])
        # print(type(done))
    except sqlalchemy.exc.IntegrityError as e:
        return Response(
            content=json.dumps({"Status": "Error", "Message": str(e)}), status_code=500
        )
    done = await resp.get_all()
    # print(done)
    return Response(content=json.dumps(done), status_code=200)

@router.get("/{room_id}/join")
async def join_room(room_id: str, request: Request):
    return RedirectResponse(f"/room/{room_id}")


@router.get("/{room_id}/queue")
async def get_queue_tracks(room_id: str, track_id: str = ""):
    room_model = RoomsServices(db)
    info = await room_model.get_tracks_from_room(room_id)
    print(f"Queue request for room {room_id}, track_id: {track_id}")
    
    try:
        # Если запрашивается информация об одном треке
        if track_id:
            track_info = await get_track_info_cached(track_id)
            return JSONResponse(
                content={'new_track': track_info},
                headers={
                    "Access-Control-Allow-Origin": DOMAIN,
                    "Access-Control-Allow-Credentials": "true",
                }
            )
        
        # Получаем информацию о всех треках параллельно
        track_urls = info.get('list_track', [])
        if not track_urls:
            return JSONResponse(
                content={'list_track': [], 'index': 0},
                headers={
                    "Access-Control-Allow-Origin": DOMAIN,
                    "Access-Control-Allow-Credentials": "true",
                }
            )
        
        # Извлекаем track_id из URL и получаем информацию параллельно
        async def get_track_from_url(url: str) -> dict:
            clean_url = url.split("?")[0]
            tid = clean_url.split("track/")[1].split("/")[0]
            return await get_track_info_cached(tid)
        
        # Параллельное получение всех треков
        tracks = await asyncio.gather(*[get_track_from_url(url) for url in track_urls])

        return JSONResponse(
            content={'list_track': list(tracks), 'index': info.get('index', 0)},
            headers={
                "Access-Control-Allow-Origin": DOMAIN,
                "Access-Control-Allow-Credentials": "true",
            }
        )
    except Exception as e:
        print(f"Error in get_queue_tracks: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/user/{user_id}/rooms")
async def get_user_rooms(user_id: str):
    """Получить список комнат пользователя"""
    try:
        user_model = UserServices(db)
        room_model = RoomsServices(db)
        
        # Получаем ID комнат пользователя
        room_ids = await user_model.get_user_rooms(user_id)
        
        if not room_ids:
            return JSONResponse(content={'rooms': []})
        
        # Получаем информацию о каждой комнате
        rooms = []
        for room_id in room_ids:
            try:
                async with db.session_factory() as session:
                    room = await session.get(Rooms, room_id)
                    if room:
                        rooms.append({
                            'id': str(room.id),
                            'name': room.name_room,
                            'participants_count': len(room.list_of_participants) if room.list_of_participants else 0
                        })
            except Exception as e:
                print(f"Error getting room {room_id}: {e}")
                continue
        
        return JSONResponse(content={'rooms': rooms})
    except Exception as e:
        print(f"Error in get_user_rooms: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
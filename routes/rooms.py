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

# Кэш для информации о треках (TTL 10 минут) - увеличен для производительности
track_info_cache = Cache(Cache.MEMORY, serializer=JsonSerializer())

# Глобальный клиент Yandex Music (переиспользуется)
_yandex_client = None

def get_yandex_client():
    """Получить или создать клиент Yandex Music"""
    global _yandex_client
    if _yandex_client is None:
        _yandex_client = Client(OAUTH_TOKEN).init()
    return _yandex_client


def _get_tracks_batch_sync(track_ids: list, client: Client) -> list:
    """Батчевое получение информации о треках (один запрос к API)"""
    if not track_ids:
        return []
    
    tracks = client.tracks(track_ids)
    return [
        {
            "id": str(track.id),
            "title": track.title,
            "artist": ", ".join(artist.name for artist in track.artists),
            "cover": f"https://{track.cover_uri.replace('%%', '100x100')}" if track.cover_uri else None,
            "duration": track.duration_ms / 1000 if track.duration_ms else None
        }
        for track in tracks
    ]


def _get_track_info_sync(track_id: str, client: Client) -> dict:
    """Синхронное получение информации о треке"""
    track = client.tracks(track_id)[0]
    return {
        "id": track.id,
        "title": track.title,
        "artist": ", ".join(artist.name for artist in track.artists),
        "cover": f"https://{track.cover_uri.replace('%%', '100x100')}" if track.cover_uri else None,
        "duration": track.duration_ms / 1000 if track.duration_ms else None
    }


async def get_tracks_batch_cached(track_ids: list) -> list:
    """Батчевое получение треков с кэшированием"""
    if not track_ids:
        return []
    
    results = []
    uncached_ids = []
    uncached_indices = []
    
    # Проверяем кэш для каждого трека
    for i, track_id in enumerate(track_ids):
        cache_key = f"track_info:{track_id}"
        cached_info = await track_info_cache.get(cache_key)
        if cached_info:
            results.append((i, cached_info))
        else:
            uncached_ids.append(track_id)
            uncached_indices.append(i)
    
    # Батчевый запрос для некэшированных треков
    if uncached_ids:
        loop = asyncio.get_event_loop()
        client = get_yandex_client()
        new_tracks = await loop.run_in_executor(executor, _get_tracks_batch_sync, uncached_ids, client)
        
        # Кэшируем и добавляем результаты
        for idx, track_info in zip(uncached_indices, new_tracks):
            cache_key = f"track_info:{track_info['id']}"
            await track_info_cache.set(cache_key, track_info, ttl=600)  # 10 минут
            results.append((idx, track_info))
    
    # Сортируем по оригинальному порядку
    results.sort(key=lambda x: x[0])
    return [r[1] for r in results]


async def get_track_info_cached(track_id: str) -> dict:
    """Получение информации о треке с кэшированием"""
    cache_key = f"track_info:{track_id}"
    
    # Проверяем кэш
    cached_info = await track_info_cache.get(cache_key)
    if cached_info:
        return cached_info
    
    # Если нет в кэше - получаем из API в отдельном потоке
    loop = asyncio.get_event_loop()
    client = get_yandex_client()
    track_info = await loop.run_in_executor(executor, _get_track_info_sync, track_id, client)
    
    # Сохраняем в кэш на 10 минут
    await track_info_cache.set(cache_key, track_info, ttl=600)
    
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
async def get_queue_tracks(room_id: str, track_id: str = "", track_url: str = ""):
    room_model = RoomsServices(db)
    info = await room_model.get_tracks_from_room(room_id)
    
    try:
        # Если запрашивается информация об одном треке
        if track_id:
            track_info = await get_track_info_cached(track_id)
            # Добавляем URL если передан
            if track_url:
                track_info = {**track_info, 'url': track_url}
            elif 'id' in track_info:
                # Формируем URL из track_id если не передан
                track_info = {**track_info, 'url': f"https://music.yandex.ru/track/{track_info['id']}"}
            return JSONResponse(
                content={'new_track': track_info},
                headers={
                    "Access-Control-Allow-Origin": DOMAIN,
                    "Access-Control-Allow-Credentials": "true",
                }
            )
        
        # Получаем информацию о всех треках БАТЧЕМ (один запрос к API)
        track_urls = info.get('list_track', [])
        if not track_urls:
            return JSONResponse(
                content={'list_track': [], 'index': 0},
                headers={
                    "Access-Control-Allow-Origin": DOMAIN,
                    "Access-Control-Allow-Credentials": "true",
                }
            )
        
        # Извлекаем track_id из URL и сохраняем URL
        track_ids = []
        url_map = {}  # track_id -> url
        for url in track_urls:
            clean_url = url.split("?")[0]
            tid = clean_url.split("track/")[1].split("/")[0]
            track_ids.append(tid)
            url_map[tid] = url
        
        # Батчевое получение всех треков (быстрее чем по одному)
        tracks = await get_tracks_batch_cached(track_ids)
        
        # Добавляем URL к каждому треку
        for track in tracks:
            track['url'] = url_map.get(track['id'], '')

        return JSONResponse(
            content={'list_track': tracks, 'index': info.get('index', 0)},
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
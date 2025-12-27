import json
import os
import asyncio
import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import (JSONResponse, StreamingResponse)
from yandex_music import Client
from aiocache import cached, Cache
from aiocache.serializers import JsonSerializer
from services.users_services import UserServices
from db.base import Database
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor


db = Database()
load_dotenv()
OAUTH_TOKEN = os.getenv("OAUTH_TOKEN")

router = APIRouter(prefix="/tracks")

# Пул потоков для синхронных операций
executor = ThreadPoolExecutor(max_workers=10)

# Кэш для метаданных треков
track_cache = Cache(Cache.MEMORY, serializer=JsonSerializer())


def _get_track_sync(track_id: str, token: str) -> tuple:
    """Синхронное получение трека"""
    client = Client(token).init()
    track = client.tracks(track_id)[0]
    return track


async def get_track_cached(track_id: str, token: str):
    """Получение трека с кэшированием"""
    cache_key = f"track:{track_id}"
    
    # Кэшируем только метаданные, не объект
    cached_meta = await track_cache.get(cache_key)
    
    loop = asyncio.get_event_loop()
    track = await loop.run_in_executor(executor, _get_track_sync, track_id, token)
    
    return track


@router.get("/track_info")
async def get_track_info(url: str, user_id: str, request: Request):
    try:
        user_model = UserServices(db)
        yan_tok = await user_model.get_yandex_token_by_user_id(user_id=user_id)
        
        track_id = url.split('track/')[1].split('/')[0] if 'track/' in url else url
        track = await get_track_cached(track_id, yan_tok or OAUTH_TOKEN)

        return {
            "title": track.title,
            "artist": ", ".join(artist.name for artist in track.artists),
            "cover": f"https://{track.cover_uri.replace('%%', '400x400')}",
        }
    except Exception as e:
        print(f"Error in get_track_info: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    

@router.get("/track_and_stream")
async def track_and_stream(url: str, user_id: str):
    try:
        clean_url = url.split("?")[0]
        track_id = clean_url.split("track/")[1].split("/")[0]
        
        # Проверяем кэш метаданных
        cache_key = f"track_meta:{track_id}"
        cached_info = await track_cache.get(cache_key)
        
        if cached_info:
            return JSONResponse(cached_info)

        track = await get_track_cached(track_id, OAUTH_TOKEN)
        
        # Получаем прямую ссылку в отдельном потоке
        loop = asyncio.get_event_loop()
        download_info = await loop.run_in_executor(
            executor, 
            lambda: track.get_download_info(get_direct_links=True)[0]
        )

        duration_sec = track.duration_ms / 1000 if track.duration_ms else None
        track_info = {
            "title": track.title,
            "artist": ", ".join(artist.name for artist in track.artists),
            "cover": f"https://{track.cover_uri.replace('%%', '400x400')}",
            "stream_url": f"/stream?url={url}&user_id={user_id}",
            "duration": duration_sec,
        }
        
        # Кэшируем на 2 минуты
        await track_cache.set(cache_key, track_info, ttl=120)

        return JSONResponse(track_info)
    except Exception as e:
        print(f"Error in track_and_stream: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    

@router.get("/stream")
async def stream_audio(url: str, request: Request, user_id: str):
    try:
        if "music.yandex.ru" not in url or "track/" not in url:
            raise HTTPException(status_code=400, detail="Invalid track URL. Must be a Yandex Music track URL")

        clean_url = url.split("?")[0]
        track_id = clean_url.split("track/")[1].split("/")[0]

        # Получаем трек
        track = await get_track_cached(track_id, OAUTH_TOKEN)
        
        # Получаем прямую ссылку в отдельном потоке
        loop = asyncio.get_event_loop()
        download_info = await loop.run_in_executor(
            executor, 
            lambda: track.get_download_info(get_direct_links=True)[0]
        )
        stream_url = await loop.run_in_executor(executor, download_info.get_direct_link)

        # Определяем MIME-тип по кодеку
        mime_type = {
            "mp3": "audio/mpeg",
            "aac": "audio/aac",
            "flac": "audio/flac",
        }.get(download_info.codec, "audio/mpeg")

        # Получаем длительность трека в секундах
        duration_sec = track.duration_ms / 1000 if track.duration_ms else None

        # Получаем Content-Length
        content_length = None
        async with httpx.AsyncClient() as client:
            try:
                head_response = await client.head(stream_url, follow_redirects=True, timeout=5.0)
                content_length = head_response.headers.get("content-length")
            except Exception as e:
                print(f"Error getting content length: {e}")

        # Если не удалось получить Content-Length, используем примерный расчет
        if not content_length and duration_sec:
            content_length = str(int(duration_sec * 16000))

        track_info = {
            "title": track.title,
            "artist": ", ".join(artist.name for artist in track.artists),
            "cover": f"https://{track.cover_uri.replace('%%', '400x400')}",
            "duration": duration_sec,
        }

        response_headers = {
            "Content-Type": mime_type,
            "Content-Disposition": "inline",
            "X-Content-Type-Options": "nosniff",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Expose-Headers": "Track-Info, Content-Duration",
            "Track-Info": json.dumps(track_info),
            "Content-Duration": str(duration_sec) if duration_sec else "0",
            "Cache-Control": "public, max-age=3600",  # Кэширование на 1 час
            "Accept-Ranges": "bytes",
        }

        if content_length:
            response_headers["Content-Length"] = content_length

        # Асинхронный генератор с увеличенным буфером
        async def generate():
            async with httpx.AsyncClient(timeout=None, follow_redirects=True) as client:
                async with client.stream("GET", stream_url) as response:
                    if response.status_code != 200:
                        raise HTTPException(
                            status_code=502,
                            detail=f"Upstream error: {response.status_code}"
                        )
                    
                    # Увеличенный размер чанка для лучшей производительности
                    async for chunk in response.aiter_bytes(chunk_size=512 * 1024):
                        if await request.is_disconnected():
                            break
                        yield chunk

        return StreamingResponse(
            generate(),
            media_type=mime_type,
            headers=response_headers
        )

    except Exception as e:
        print(f"Stream error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Streaming failed: {str(e)}")
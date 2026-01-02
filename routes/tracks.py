import json
import os
import asyncio
import time
import httpx
from fastapi import APIRouter, HTTPException, Request, Query
from fastapi.responses import JSONResponse, StreamingResponse, Response
from yandex_music import Client
from aiocache import Cache
from aiocache.serializers import JsonSerializer
from services.users_services import UserServices
from services.stream_service import (
    generate_stream_token, 
    verify_stream_token, 
    register_stream, 
    unregister_stream
)
from db.base import Database
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor


db = Database()
load_dotenv()
OAUTH_TOKEN = os.getenv("OAUTH_TOKEN")

router = APIRouter(prefix="/tracks")

# Пул потоков для синхронных операций
executor = ThreadPoolExecutor(max_workers=10)

# Кэши для треков и метаданных
track_object_cache = {}  # In-memory кэш для объектов треков (не сериализуемые)
track_meta_cache = Cache(Cache.MEMORY, serializer=JsonSerializer())  # Кэш для сериализуемых метаданных

# Кэш для прямых ссылок на треки (увеличен TTL)
direct_link_cache = {}
DIRECT_LINK_TTL = 180  # 3 минуты (ссылки Yandex живут ~5 минут)

# TTL для кэша объектов треков (10 минут)
TRACK_CACHE_TTL = 600

# Глобальный клиент (переиспользуется для скорости)
_yandex_client = None

def get_yandex_client(token: str = None):
    """Получить или создать клиент Yandex Music"""
    global _yandex_client
    if _yandex_client is None:
        _yandex_client = Client(token or OAUTH_TOKEN).init()
    return _yandex_client


def _get_track_sync(track_id: str, token: str):
    """Синхронное получение трека из Yandex Music API"""
    client = get_yandex_client(token)
    track = client.tracks(track_id)[0]
    return track


def _get_download_info_sync(track, get_direct: bool = True):
    """Синхронное получение информации о загрузке"""
    return track.get_download_info(get_direct_links=get_direct)[0]


async def get_track_cached(track_id: str, token: str):
    """
    Получение трека с кэшированием.
    Объекты Track не сериализуемы, поэтому храним их в простом dict.
    """
    import time
    cache_key = f"track:{track_id}:{token}"
    current_time = time.time()
    
    # Проверяем кэш объектов
    if cache_key in track_object_cache:
        cached_data = track_object_cache[cache_key]
        if current_time - cached_data["timestamp"] < TRACK_CACHE_TTL:
            return cached_data["track"]
        else:
            # Удаляем устаревший кэш
            del track_object_cache[cache_key]
    
    # Получаем трек из API
    loop = asyncio.get_event_loop()
    track = await loop.run_in_executor(executor, _get_track_sync, track_id, token)
    
    # Сохраняем в кэш
    track_object_cache[cache_key] = {
        "track": track,
        "timestamp": current_time
    }
    
    return track


async def get_track_metadata_cached(track_id: str, token: str) -> dict:
    """
    Получение метаданных трека с кэшированием.
    Возвращает сериализуемый словарь.
    """
    cache_key = f"track_meta:{track_id}"
    
    # Проверяем кэш метаданных
    cached_meta = await track_meta_cache.get(cache_key)
    if cached_meta:
        return cached_meta
    
    # Получаем трек
    track = await get_track_cached(track_id, token)
    
    # Формируем метаданные
    metadata = {
        "title": track.title,
        "artist": ", ".join(artist.name for artist in track.artists),
        "cover": f"https://{track.cover_uri.replace('%%', '400x400')}" if track.cover_uri else None,
        "duration": track.duration_ms / 1000 if track.duration_ms else None,
    }
    
    # Кэшируем на 10 минут
    await track_meta_cache.set(cache_key, metadata, ttl=600)
    
    return metadata


@router.get("/track_info")
async def get_track_info(url: str, user_id: str, request: Request):
    """Получить информацию о треке по URL"""
    try:
        user_model = UserServices(db)
        yan_tok = await user_model.get_yandex_token_by_user_id(user_id=user_id)
        
        track_id = url.split('track/')[1].split('/')[0] if 'track/' in url else url
        
        # Используем кэшированные метаданные
        metadata = await get_track_metadata_cached(track_id, yan_tok or OAUTH_TOKEN)

        return metadata
    except Exception as e:
        print(f"Error in get_track_info: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    

@router.get("/track_and_stream")
async def track_and_stream(url: str, user_id: str, room_id: str = "default"):
    """
    Получить информацию о треке и прямую ссылку для стриминга.
    Прямая ссылка Yandex обеспечивает быструю загрузку без проксирования.
    """
    try:
        clean_url = url.split("?")[0]
        track_id = clean_url.split("track/")[1].split("/")[0]
        
        # Параллельно получаем метаданные и прямую ссылку
        metadata_task = get_track_metadata_cached(track_id, OAUTH_TOKEN)
        direct_link_task = _get_direct_link_cached(track_id)
        
        metadata, (direct_url, mime_type) = await asyncio.gather(
            metadata_task, 
            direct_link_task
        )
        
        track_info = {
            **metadata,
            "stream_url": direct_url,  # Прямая ссылка Yandex для быстрой загрузки
            "track_id": track_id,
            "mime_type": mime_type,
        }

        return JSONResponse(track_info)
    except Exception as e:
        print(f"Error in track_and_stream: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


async def _get_direct_link_cached(track_id: str) -> tuple[str, str]:
    """
    Получение прямой ссылки на трек с кэшированием.
    Возвращает (stream_url, mime_type)
    """
    current_time = time.time()
    cache_key = f"direct:{track_id}"
    
    # Проверяем кэш
    if cache_key in direct_link_cache:
        cached = direct_link_cache[cache_key]
        if current_time - cached["timestamp"] < DIRECT_LINK_TTL:
            return cached["url"], cached["mime_type"]
    
    # Получаем трек
    track = await get_track_cached(track_id, OAUTH_TOKEN)
    
    # Получаем прямую ссылку
    loop = asyncio.get_event_loop()
    download_info = await loop.run_in_executor(
        executor, _get_download_info_sync, track, True
    )
    stream_url = await loop.run_in_executor(executor, download_info.get_direct_link)
    
    mime_type = {
        "mp3": "audio/mpeg",
        "aac": "audio/aac",
        "flac": "audio/flac",
    }.get(download_info.codec, "audio/mpeg")
    
    # Кэшируем
    direct_link_cache[cache_key] = {
        "url": stream_url,
        "mime_type": mime_type,
        "timestamp": current_time
    }
    
    return stream_url, mime_type


@router.get("/stream/{token}")
async def stream_audio_secure(token: str, request: Request):
    """
    Защищённый стриминг аудио по токену.
    Токен содержит track_id, user_id, room_id и подпись.
    """
    # Верифицируем токен
    stream_token = verify_stream_token(token)
    if not stream_token:
        raise HTTPException(status_code=403, detail="Invalid or expired stream token")
    
    try:
        track_id = stream_token.track_id
        
        # Регистрируем активный стрим
        register_stream(token, track_id, stream_token.user_id)
        
        # Получаем прямую ссылку (из кэша или API)
        stream_url, mime_type = await _get_direct_link_cached(track_id)
        
        # Получаем метаданные для заголовков
        metadata = await get_track_metadata_cached(track_id, OAUTH_TOKEN)
        duration_sec = metadata.get("duration")

        # Получаем Content-Length
        content_length = None
        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
            try:
                head_response = await client.head(stream_url, follow_redirects=True)
                content_length = head_response.headers.get("content-length")
            except Exception as e:
                print(f"Error getting content length: {e}")

        if not content_length and duration_sec:
            content_length = str(int(duration_sec * 16000))

        response_headers = {
            "Content-Type": mime_type,
            "Content-Disposition": "inline",
            "X-Content-Type-Options": "nosniff",
            "Cache-Control": "no-store, no-cache, must-revalidate",  # Запрещаем кэширование в браузере
            "Accept-Ranges": "bytes",
            "X-Stream-Token": "valid",  # Индикатор валидного токена
        }

        if content_length:
            response_headers["Content-Length"] = content_length

        async def generate():
            try:
                async with httpx.AsyncClient(timeout=httpx.Timeout(None), follow_redirects=True) as client:
                    async with client.stream("GET", stream_url) as response:
                        if response.status_code != 200:
                            return
                        
                        # Используем небольшие чанки для быстрого старта
                        async for chunk in response.aiter_bytes(chunk_size=32 * 1024):
                            if await request.is_disconnected():
                                break
                            yield chunk
            finally:
                # Удаляем стрим из активных при завершении
                unregister_stream(token)

        return StreamingResponse(
            generate(),
            media_type=mime_type,
            headers=response_headers
        )

    except Exception as e:
        unregister_stream(token)
        print(f"Secure stream error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Streaming failed: {str(e)}")


# Оставляем старый эндпоинт для обратной совместимости, но помечаем как deprecated
@router.get("/search")
async def search_tracks(query: str, limit: int = 10):
    """
    Поиск треков по названию в Yandex Music.
    Возвращает список треков с метаданными и URL.
    """
    try:
        loop = asyncio.get_event_loop()
        client = get_yandex_client()
        
        # Выполняем поиск в отдельном потоке
        search_result = await loop.run_in_executor(
            executor, 
            lambda: client.search(query, type_='track')
        )
        
        if not search_result or not search_result.tracks:
            return {"results": []}
        
        tracks = search_result.tracks.results[:limit]
        results = []
        
        for track in tracks:
            try:
                track_url = f"https://music.yandex.ru/track/{track.id}"
                results.append({
                    "id": str(track.id),
                    "title": track.title,
                    "artist": ", ".join(artist.name for artist in track.artists) if track.artists else "Unknown",
                    "cover": f"https://{track.cover_uri.replace('%%', '200x200')}" if track.cover_uri else None,
                    "duration": track.duration_ms / 1000 if track.duration_ms else None,
                    "url": track_url
                })
            except Exception as e:
                print(f"Error processing track {track.id}: {e}")
                continue
        
        return {"results": results}
        
    except Exception as e:
        print(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/playlist")
async def get_playlist_tracks(url: str, limit: int = 50):
    """
    Получить треки из плейлиста Yandex Music.
    Поддерживает ссылки вида:
    - https://music.yandex.ru/users/{user}/playlists/{id}
    - https://music.yandex.ru/album/{id}
    """
    try:
        loop = asyncio.get_event_loop()
        client = get_yandex_client()
        
        tracks_data = []
        
        # Определяем тип ссылки
        if "/users/" in url and "/playlists/" in url:
            # Плейлист пользователя
            parts = url.split("/users/")[1].split("/playlists/")
            user_id = parts[0]
            playlist_id = parts[1].split("/")[0].split("?")[0]
            
            playlist = await loop.run_in_executor(
                executor,
                lambda: client.users_playlists(playlist_id, user_id)
            )
            
            if playlist and playlist.tracks:
                for track_short in playlist.tracks[:limit]:
                    try:
                        track = track_short.track
                        if track:
                            track_url = f"https://music.yandex.ru/track/{track.id}"
                            tracks_data.append({
                                "id": str(track.id),
                                "title": track.title,
                                "artist": ", ".join(artist.name for artist in track.artists) if track.artists else "Unknown",
                                "cover": f"https://{track.cover_uri.replace('%%', '200x200')}" if track.cover_uri else None,
                                "duration": track.duration_ms / 1000 if track.duration_ms else None,
                                "url": track_url
                            })
                    except Exception as e:
                        print(f"Error processing playlist track: {e}")
                        continue
                        
        elif "/album/" in url:
            # Альбом
            album_id = url.split("/album/")[1].split("/")[0].split("?")[0]
            
            album = await loop.run_in_executor(
                executor,
                lambda: client.albums_with_tracks(album_id)
            )
            
            if album and album.volumes:
                for volume in album.volumes:
                    for track in volume[:limit]:
                        try:
                            track_url = f"https://music.yandex.ru/track/{track.id}"
                            tracks_data.append({
                                "id": str(track.id),
                                "title": track.title,
                                "artist": ", ".join(artist.name for artist in track.artists) if track.artists else "Unknown",
                                "cover": f"https://{track.cover_uri.replace('%%', '200x200')}" if track.cover_uri else None,
                                "duration": track.duration_ms / 1000 if track.duration_ms else None,
                                "url": track_url
                            })
                        except Exception as e:
                            print(f"Error processing album track: {e}")
                            continue
        else:
            raise HTTPException(status_code=400, detail="Unsupported URL format. Use playlist or album links.")
        
        return {
            "tracks": tracks_data,
            "count": len(tracks_data)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Playlist error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch playlist: {str(e)}")


@router.post("/batch_info")
async def get_batch_track_info(track_urls: list[str]):
    """
    Получить информацию о нескольких треках одновременно.
    Пропускает треки, которые не удалось обработать.
    """
    try:
        results = []
        
        for url in track_urls:
            try:
                clean_url = url.split("?")[0]
                if "track/" not in clean_url:
                    continue
                    
                track_id = clean_url.split("track/")[1].split("/")[0]
                metadata = await get_track_metadata_cached(track_id, OAUTH_TOKEN)
                direct_url, mime_type = await _get_direct_link_cached(track_id)
                
                results.append({
                    **metadata,
                    "stream_url": direct_url,
                    "track_id": track_id,
                    "url": url,
                    "mime_type": mime_type
                })
            except Exception as e:
                print(f"Error processing track {url}: {e}")
                continue
        
        return {"tracks": results, "count": len(results)}
        
    except Exception as e:
        print(f"Batch info error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch processing failed: {str(e)}")


@router.get("/stream")
async def stream_audio(url: str, request: Request, user_id: str):
    """Стриминг аудио трека"""
    try:
        if "music.yandex.ru" not in url or "track/" not in url:
            raise HTTPException(status_code=400, detail="Invalid track URL. Must be a Yandex Music track URL")

        clean_url = url.split("?")[0]
        track_id = clean_url.split("track/")[1].split("/")[0]

        # Получаем трек (из кэша или API)
        track = await get_track_cached(track_id, OAUTH_TOKEN)
        
        # Получаем прямую ссылку в отдельном потоке
        loop = asyncio.get_event_loop()
        download_info = await loop.run_in_executor(
            executor, 
            _get_download_info_sync, track, True
        )
        stream_url = await loop.run_in_executor(executor, download_info.get_direct_link)

        # Определяем MIME-тип по кодеку
        mime_type = {
            "mp3": "audio/mpeg",
            "aac": "audio/aac",
            "flac": "audio/flac",
        }.get(download_info.codec, "audio/mpeg")

        # Используем кэшированные метаданные
        metadata = await get_track_metadata_cached(track_id, OAUTH_TOKEN)
        duration_sec = metadata.get("duration")

        # Получаем Content-Length с таймаутом
        content_length = None
        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
            try:
                head_response = await client.head(stream_url, follow_redirects=True)
                content_length = head_response.headers.get("content-length")
            except Exception as e:
                print(f"Error getting content length: {e}")

        # Если не удалось получить Content-Length, используем примерный расчет
        if not content_length and duration_sec:
            content_length = str(int(duration_sec * 16000))

        response_headers = {
            "Content-Type": mime_type,
            "Content-Disposition": "inline",
            "X-Content-Type-Options": "nosniff",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Expose-Headers": "Track-Info, Content-Duration",
            "Track-Info": json.dumps(metadata),
            "Content-Duration": str(duration_sec) if duration_sec else "0",
            "Cache-Control": "public, max-age=3600",
            "Accept-Ranges": "bytes",
        }

        if content_length:
            response_headers["Content-Length"] = content_length

        # Асинхронный генератор с оптимальным размером чанка
        async def generate():
            async with httpx.AsyncClient(timeout=httpx.Timeout(None), follow_redirects=True) as client:
                async with client.stream("GET", stream_url) as response:
                    if response.status_code != 200:
                        raise HTTPException(
                            status_code=502,
                            detail=f"Upstream error: {response.status_code}"
                        )
                    
                    # Оптимальный размер чанка (64KB - баланс между задержкой и производительностью)
                    async for chunk in response.aiter_bytes(chunk_size=64 * 1024):
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
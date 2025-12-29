"""
Сервис безопасного стриминга аудио с токенизированными URL и шифрованием
"""
import os
import time
import secrets
import hashlib
import hmac
from typing import Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

# Секретный ключ для подписи токенов (должен быть в .env)
STREAM_SECRET = os.getenv("STREAM_SECRET", secrets.token_urlsafe(32))
TOKEN_EXPIRY_SECONDS = 300  # 5 минут жизни токена


@dataclass
class StreamToken:
    """Токен для доступа к стриму"""
    track_id: str
    user_id: str
    room_id: str
    expires_at: int
    signature: str


def generate_stream_token(track_id: str, user_id: str, room_id: str) -> str:
    """
    Генерирует подписанный токен для доступа к стриму.
    Токен содержит: track_id, user_id, room_id, время истечения и подпись.
    """
    expires_at = int(time.time()) + TOKEN_EXPIRY_SECONDS
    
    # Формируем данные для подписи
    data = f"{track_id}:{user_id}:{room_id}:{expires_at}"
    
    # Создаём HMAC подпись
    signature = hmac.new(
        STREAM_SECRET.encode(),
        data.encode(),
        hashlib.sha256
    ).hexdigest()[:32]  # Берём первые 32 символа для компактности
    
    # Формируем токен: base64(track_id:user_id:room_id:expires:signature)
    import base64
    token_data = f"{track_id}:{user_id}:{room_id}:{expires_at}:{signature}"
    token = base64.urlsafe_b64encode(token_data.encode()).decode()
    
    return token


def verify_stream_token(token: str) -> Optional[StreamToken]:
    """
    Проверяет и декодирует токен стрима.
    Возвращает StreamToken или None если токен невалиден.
    """
    try:
        import base64
        
        # Декодируем токен
        token_data = base64.urlsafe_b64decode(token.encode()).decode()
        parts = token_data.split(':')
        
        if len(parts) != 5:
            return None
        
        track_id, user_id, room_id, expires_str, signature = parts
        expires_at = int(expires_str)
        
        # Проверяем время истечения
        if time.time() > expires_at:
            return None
        
        # Проверяем подпись
        data = f"{track_id}:{user_id}:{room_id}:{expires_at}"
        expected_signature = hmac.new(
            STREAM_SECRET.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()[:32]
        
        if not hmac.compare_digest(signature, expected_signature):
            return None
        
        return StreamToken(
            track_id=track_id,
            user_id=user_id,
            room_id=room_id,
            expires_at=expires_at,
            signature=signature
        )
        
    except Exception:
        return None


def get_token_remaining_time(token: str) -> int:
    """Возвращает оставшееся время жизни токена в секундах"""
    stream_token = verify_stream_token(token)
    if stream_token:
        return max(0, stream_token.expires_at - int(time.time()))
    return 0


# Кэш активных стримов для отслеживания
active_streams: dict[str, dict] = {}


def register_stream(token: str, track_id: str, user_id: str):
    """Регистрирует активный стрим"""
    active_streams[token] = {
        "track_id": track_id,
        "user_id": user_id,
        "started_at": time.time()
    }


def unregister_stream(token: str):
    """Удаляет стрим из активных"""
    active_streams.pop(token, None)


def cleanup_expired_streams():
    """Очищает истёкшие стримы"""
    current_time = time.time()
    expired = [
        token for token, data in active_streams.items()
        if current_time - data["started_at"] > TOKEN_EXPIRY_SECONDS * 2
    ]
    for token in expired:
        del active_streams[token]

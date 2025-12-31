/**
 * Audio Player Utils - Модуль для работы с аудио плеером
 */

import { tracksApi } from './api.js';

/**
 * Загрузить трек и получить метаданные
 */
export async function loadTrackMetadata(trackUrl, userId) {
  const data = await tracksApi.getTrackAndStream(trackUrl, userId);
  return {
    title: data.title,
    artist: data.artist,
    cover: data.cover,
    streamUrl: data.stream_url, // Прямая ссылка Yandex (без проксирования)
    duration: data.duration,    // Длительность в секундах
  };
}

/**
 * Загрузить аудио в элемент (прямая загрузка, без MediaSource)
 * Возвращает Promise который резолвится когда трек готов к воспроизведению
 */
export async function loadAudioStream(audioElement, streamUrl, knownDuration = null) {
  return new Promise((resolve, reject) => {
    // Останавливаем текущее воспроизведение
    audioElement.pause();
    
    let resolved = false;
    let timeoutId = null;
    
    // Очистка старых обработчиков
    const cleanup = () => {
      audioElement.oncanplaythrough = null;
      audioElement.oncanplay = null;
      audioElement.onerror = null;
      audioElement.onloadedmetadata = null;
      audioElement.onloadeddata = null;
      if (timeoutId) clearTimeout(timeoutId);
    };
    
    const resolveOnce = (duration) => {
      if (resolved) return;
      resolved = true;
      cleanup();
      resolve(duration);
    };

    // Обработчик успешной загрузки (основной)
    audioElement.oncanplaythrough = () => {
      const duration = audioElement.duration && isFinite(audioElement.duration) 
        ? audioElement.duration 
        : knownDuration;
      resolveOnce(duration);
    };
    
    // Альтернативный обработчик (для фоновых вкладок)
    audioElement.oncanplay = () => {
      const duration = audioElement.duration && isFinite(audioElement.duration) 
        ? audioElement.duration 
        : knownDuration;
      resolveOnce(duration);
    };
    
    // Ещё один fallback - loadeddata
    audioElement.onloadeddata = () => {
      // Даём немного времени на определение длительности
      setTimeout(() => {
        if (!resolved) {
          const duration = audioElement.duration && isFinite(audioElement.duration) 
            ? audioElement.duration 
            : knownDuration;
          resolveOnce(duration);
        }
      }, 100);
    };

    // Обработчик ошибки
    audioElement.onerror = (e) => {
      if (resolved) return;
      cleanup();
      reject(new Error(`Ошибка загрузки аудио: ${audioElement.error?.message || 'Unknown'}`));
    };

    // Загрузка метаданных (для получения duration)
    audioElement.onloadedmetadata = () => {
      // Если в фоновой вкладке, резолвим сразу - загрузка и play важнее точной duration
      if (document.hidden) {
        const duration = audioElement.duration && isFinite(audioElement.duration) 
          ? audioElement.duration 
          : knownDuration;
        resolveOnce(duration);
      }
    };
    
    // Таймаут на случай если события не сработают (например в фоне)
    // В фоне используем короткий таймаут чтобы не блокировать загрузку
    const timeout = document.hidden ? 1000 : 5000;
    timeoutId = setTimeout(() => {
      if (!resolved) {
        resolveOnce(knownDuration);
      }
    }, timeout);

    // Устанавливаем источник и начинаем загрузку
    audioElement.src = streamUrl;
    audioElement.load();
  });
}

/**
 * Настроить Media Session API для системных медиа-контролов
 */
export function setupMediaSession(metadata, handlers = {}) {
  if (!('mediaSession' in navigator)) return;

  navigator.mediaSession.metadata = new MediaMetadata({
    title: metadata.title,
    artist: metadata.artist,
    artwork: [{ src: metadata.cover, sizes: '400x400', type: 'image/jpeg' }],
  });

  if (handlers.play) {
    navigator.mediaSession.setActionHandler('play', handlers.play);
  }
  if (handlers.pause) {
    navigator.mediaSession.setActionHandler('pause', handlers.pause);
  }
  if (handlers.previoustrack) {
    navigator.mediaSession.setActionHandler('previoustrack', handlers.previoustrack);
  }
  if (handlers.nexttrack) {
    navigator.mediaSession.setActionHandler('nexttrack', handlers.nexttrack);
  }
}

/**
 * Форматирование времени в mm:ss
 */
export function formatTime(seconds) {
  if (!seconds || !isFinite(seconds)) return '0:00';
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.floor(seconds % 60);
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
}

/**
 * Синхронизация воспроизведения
 */
export function syncPlayback(audioElement, playing, position) {
  if (Math.abs(audioElement.currentTime - position) > 0.5) {
    audioElement.currentTime = position;
  }

  if (playing && audioElement.paused) {
    audioElement.play().catch(() => {});
    return true;
  } else if (!playing && !audioElement.paused) {
    audioElement.pause();
    return false;
  }
  
  return playing;
}

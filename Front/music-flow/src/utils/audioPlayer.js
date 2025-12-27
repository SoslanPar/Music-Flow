/**
 * Audio Player Utils - Модуль для работы с аудио плеером
 */

import { tracksApi } from './api.js';
import { loadWithMediaSource } from './mediaSourcePlayer.js';

/**
 * Загрузить трек и получить метаданные
 */
export async function loadTrackMetadata(trackUrl, userId) {
  const data = await tracksApi.getTrackAndStream(trackUrl, userId);
  return {
    title: data.title,
    artist: data.artist,
    cover: data.cover,
    streamUrl: `/api/tracks${data.stream_url}`,
    duration: data.duration,
  };
}

/**
 * Загрузить аудио в элемент через MediaSource
 */
export async function loadAudioStream(audioElement, streamUrl) {
  audioElement.pause();
  audioElement.removeAttribute('src');
  audioElement.load();

  // Очистка старых обработчиков
  audioElement.onerror = null;
  audioElement.onloadedmetadata = null;
  audioElement.ondurationchange = null;

  await loadWithMediaSource(audioElement, streamUrl);

  // Ждём, пока длительность станет известна
  await waitForDuration(audioElement);
  
  return audioElement.duration;
}

/**
 * Ожидание загрузки длительности трека
 */
function waitForDuration(audioElement, timeout = 10000) {
  return new Promise((resolve, reject) => {
    const checkDuration = () => {
      if (audioElement.duration && audioElement.duration > 0) {
        resolve(audioElement.duration);
      } else {
        setTimeout(checkDuration, 100);
      }
    };

    const timeoutId = setTimeout(() => {
      reject(new Error('Не удалось определить длительность трека'));
    }, timeout);

    checkDuration();
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
    audioElement.play().catch(e => console.log('Play error:', e));
    return true;
  } else if (!playing && !audioElement.paused) {
    audioElement.pause();
    return false;
  }
  
  return playing;
}

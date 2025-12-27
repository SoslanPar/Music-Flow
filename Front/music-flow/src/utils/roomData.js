import { roomsApi } from './api.js';

/**
 * Получить очередь треков комнаты
 */
export async function fetchQueue(roomId, trackId = '') {
  return roomsApi.getQueue(roomId, trackId);
}

/**
 * Форматировать список участников в массив объектов
 */
export function formatParticipants(participants) {
  if (!participants) return [];
  return Object.entries(participants).map(([id, name]) => ({ id, name }));
}


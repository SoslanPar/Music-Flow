/**
 * API Service - Централизованный модуль для работы с бэкендом
 */

const API_BASE = '/api';

/**
 * Базовый fetch с обработкой ошибок
 */
async function fetchWithError(url, options = {}) {
  const defaultOptions = {
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  };

  const response = await fetch(url, { ...defaultOptions, ...options });
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || errorData.message || `HTTP Error: ${response.status}`);
  }
  
  return response.json();
}

// ============ AUTH API ============

export const authApi = {
  /**
   * Проверить токен Яндекса и авторизоваться
   */
  async checkToken(code) {
    return fetchWithError(`${API_BASE}/auth/check_token?code=${encodeURIComponent(code)}`);
  },

  /**
   * Получить текущего пользователя
   */
  async getCurrentUser() {
    return fetchWithError(`${API_BASE}/auth/current-user`);
  },

  /**
   * Войти по логину и паролю
   */
  async signIn(nickname, hashedPassword) {
    return fetchWithError(
      `${API_BASE}/auth/sign-in?nickname=${encodeURIComponent(nickname)}&hashed_password=${encodeURIComponent(hashedPassword)}`
    );
  },
};

// ============ ROOMS API ============

export const roomsApi = {
  /**
   * Создать новую комнату
   */
  async createRoom(name) {
    return fetchWithError(`${API_BASE}/rooms/create?name_rooms=${encodeURIComponent(name)}`, {
      method: 'POST',
    });
  },

  /**
   * Получить очередь треков комнаты
   */
  async getQueue(roomId, trackId = '') {
    return fetchWithError(`${API_BASE}/rooms/${roomId}/queue?track_id=${encodeURIComponent(trackId)}`);
  },
  
  /**
   * Получить комнаты пользователя
   */
  async getUserRooms(userId) {
    return fetchWithError(`${API_BASE}/rooms/user/${userId}/rooms`);
  },
};

// ============ TRACKS API ============

export const tracksApi = {
  /**
   * Получить информацию о треке
   */
  async getTrackInfo(url, userId) {
    return fetchWithError(
      `${API_BASE}/tracks/track_info?url=${encodeURIComponent(url)}&user_id=${encodeURIComponent(userId)}`
    );
  },

  /**
   * Получить трек и поток
   */
  async getTrackAndStream(url, userId) {
    return fetchWithError(
      `${API_BASE}/tracks/track_and_stream?url=${encodeURIComponent(url)}&user_id=${encodeURIComponent(userId)}`
    );
  },

  /**
   * Получить URL потока
   */
  getStreamUrl(url, userId) {
    return `${API_BASE}/tracks/stream?url=${encodeURIComponent(url)}&user_id=${encodeURIComponent(userId)}`;
  },
};

export default {
  auth: authApi,
  rooms: roomsApi,
  tracks: tracksApi,
};

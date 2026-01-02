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
   * Войти по логину и паролю (POST с JSON body)
   * Пароль отправляется в открытом виде - хеширование на сервере через bcrypt
   */
  async signIn(nickname, password) {
    return fetchWithError(`${API_BASE}/auth/sign-in`, {
      method: 'POST',
      body: JSON.stringify({ nickname, password }),
    });
  },

  /**
   * Регистрация нового пользователя (POST с JSON body)
   * Пароль отправляется в открытом виде - хеширование на сервере через bcrypt
   */
  async signUp(email, username, password, birthday = null) {
    return fetchWithError(`${API_BASE}/auth/sign-up`, {
      method: 'POST',
      body: JSON.stringify({ email, username, password, birthday }),
    });
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
   * Присоединиться к комнате по ID (добавляет в список комнат пользователя)
   */
  async joinRoom(roomId) {
    return fetchWithError(`${API_BASE}/rooms/${roomId}/join`, {
      method: 'POST',
    });
  },

  /**
   * Удалить комнату из списка пользователя (не удаляет саму комнату)
   */
  async removeRoomFromList(roomId) {
    return fetchWithError(`${API_BASE}/rooms/${roomId}/leave`, {
      method: 'DELETE',
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

  /**
   * Поиск треков по названию
   */
  async searchTracks(query, limit = 10) {
    return fetchWithError(
      `${API_BASE}/tracks/search?query=${encodeURIComponent(query)}&limit=${limit}`
    );
  },

  /**
   * Получить треки из плейлиста/альбома
   */
  async getPlaylistTracks(url, limit = 50) {
    return fetchWithError(
      `${API_BASE}/tracks/playlist?url=${encodeURIComponent(url)}&limit=${limit}`
    );
  },

  /**
   * Получить информацию о нескольких треках
   */
  async getBatchTrackInfo(trackUrls) {
    return fetchWithError(`${API_BASE}/tracks/batch_info`, {
      method: 'POST',
      body: JSON.stringify(trackUrls),
    });
  },
};

export default {
  auth: authApi,
  rooms: roomsApi,
  tracks: tracksApi,
};

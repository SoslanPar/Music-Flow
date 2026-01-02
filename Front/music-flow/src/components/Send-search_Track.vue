<template>
  <div class="search-container">
    <!-- Поле ввода -->
    <div class="input-wrapper">
      <input 
        type="text" 
        v-model="searchQuery" 
        :placeholder="inputPlaceholder"
        class="search-input"
        @input="handleInput"
        @keyup.enter="handleEnter"
        @focus="showResults = true"
      >
      <div class="input-actions">
        <!-- Индикатор загрузки -->
        <div v-if="isLoading" class="loading-spinner"></div>
        
        <!-- Кнопка очистки -->
        <button v-if="searchQuery && !isLoading" class="clear-btn" @click="clearSearch">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
            <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
          </svg>
        </button>
        
        <!-- Кнопка отправки (для прямых ссылок) -->
        <button 
          v-if="isDirectLink" 
          class="send-btn" 
          @click="handleDirectLink"
          :disabled="isLoading"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- Результаты поиска -->
    <div v-if="showResults && (searchResults.length > 0 || playlistTracks.length > 0)" class="search-results">
      <!-- Плейлист/Альбом результаты -->
      <template v-if="playlistTracks.length > 0">
        <div class="results-header">
          <span>Треки из плейлиста ({{ playlistTracks.length }})</span>
          <button class="add-all-btn" @click="addAllPlaylistTracks" :disabled="isAddingAll">
            {{ isAddingAll ? 'Добавление...' : 'Добавить все' }}
          </button>
        </div>
        <ul class="results-list">
          <li 
            v-for="track in playlistTracks" 
            :key="track.id" 
            class="result-item"
            :class="{ 'added': addedTracks.includes(track.id) }"
          >
            <img v-if="track.cover" :src="track.cover" class="track-cover" alt="">
            <div v-else class="track-cover-placeholder">♪</div>
            <div class="track-info">
              <span class="track-title">{{ track.title }}</span>
              <span class="track-artist">{{ track.artist }}</span>
            </div>
            <span v-if="track.duration" class="track-duration">{{ formatDuration(track.duration) }}</span>
            <button 
              class="add-track-btn" 
              @click="addTrack(track)"
              :disabled="addedTracks.includes(track.id)"
            >
              <svg v-if="addedTracks.includes(track.id)" width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
              </svg>
              <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
              </svg>
            </button>
          </li>
        </ul>
      </template>

      <!-- Результаты поиска -->
      <template v-else-if="searchResults.length > 0">
        <div class="results-header">
          <span>Результаты поиска</span>
        </div>
        <ul class="results-list">
          <li 
            v-for="track in searchResults" 
            :key="track.id" 
            class="result-item"
            :class="{ 'added': addedTracks.includes(track.id) }"
          >
            <img v-if="track.cover" :src="track.cover" class="track-cover" alt="">
            <div v-else class="track-cover-placeholder">♪</div>
            <div class="track-info">
              <span class="track-title">{{ track.title }}</span>
              <span class="track-artist">{{ track.artist }}</span>
            </div>
            <span v-if="track.duration" class="track-duration">{{ formatDuration(track.duration) }}</span>
            <button 
              class="add-track-btn" 
              @click="addTrack(track)"
              :disabled="addedTracks.includes(track.id)"
            >
              <svg v-if="addedTracks.includes(track.id)" width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
              </svg>
              <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
              </svg>
            </button>
          </li>
        </ul>
      </template>
    </div>

    <!-- Сообщение "нет результатов" -->
    <div v-if="showResults && noResults && searchQuery.length >= 2" class="no-results">
      <span>Ничего не найдено</span>
    </div>

    <!-- Оверлей для закрытия результатов -->
    <div v-if="showResults && (searchResults.length > 0 || playlistTracks.length > 0)" class="results-overlay" @click="showResults = false"></div>
  </div>
</template>

<script>
import { tracksApi } from '@/utils/api.js';

export default {
  data() {
    return {
      searchQuery: '',
      searchResults: [],
      playlistTracks: [],
      addedTracks: [],
      isLoading: false,
      isAddingAll: false,
      showResults: false,
      searchTimeout: null,
      noResults: false,
      resultsAnimated: false
    };
  },

  computed: {
    isDirectLink() {
      return this.searchQuery.includes('music.yandex.ru/track/');
    },
    isPlaylistLink() {
      return this.searchQuery.includes('music.yandex.ru/users/') && 
             this.searchQuery.includes('/playlists/');
    },
    isAlbumLink() {
      return this.searchQuery.includes('music.yandex.ru/album/');
    },
    inputPlaceholder() {
      return 'Поиск треков или вставьте ссылку...';
    }
  },

  watch: {
    // Анимация появления результатов
    showResults(newVal) {
      if (newVal) {
        this.$nextTick(() => {
          this.animateResultsIn();
        });
      }
    },
    // Анимация новых треков при изменении списка
    searchResults(newVal, oldVal) {
      if (newVal.length > 0 && this.showResults) {
        this.$nextTick(() => {
          this.animateNewItems(newVal.length - (oldVal?.length || 0));
        });
      }
    },
    playlistTracks(newVal, oldVal) {
      if (newVal.length > 0 && this.showResults) {
        this.$nextTick(() => {
          this.animateNewItems(newVal.length - (oldVal?.length || 0));
        });
      }
    }
  },

  methods: {
    animateResultsIn() {
      const resultsEl = this.$el.querySelector('.search-results');
      if (resultsEl && !this.resultsAnimated) {
        resultsEl.style.opacity = '0';
        resultsEl.style.transform = 'translateY(10px)';
        
        requestAnimationFrame(() => {
          resultsEl.style.transition = 'opacity 0.25s ease, transform 0.25s ease';
          resultsEl.style.opacity = '1';
          resultsEl.style.transform = 'translateY(0)';
        });
        
        // Анимируем каждый элемент списка с задержкой
        const items = resultsEl.querySelectorAll('.result-item');
        items.forEach((item, index) => {
          item.style.opacity = '0';
          item.style.transform = 'translateX(-10px)';
          
          setTimeout(() => {
            item.style.transition = 'opacity 0.2s ease, transform 0.2s ease';
            item.style.opacity = '1';
            item.style.transform = 'translateX(0)';
          }, 50 + index * 30);
        });
        
        this.resultsAnimated = true;
      }
    },

    animateNewItems(count) {
      if (count <= 0) return;
      
      const resultsEl = this.$el.querySelector('.results-list');
      if (resultsEl) {
        const items = resultsEl.querySelectorAll('.result-item');
        // Анимируем только новые элементы (последние count)
        const newItems = Array.from(items).slice(-Math.abs(count));
        
        newItems.forEach((item, index) => {
          item.style.opacity = '0';
          item.style.transform = 'translateX(-10px)';
          
          setTimeout(() => {
            item.style.transition = 'opacity 0.2s ease, transform 0.2s ease';
            item.style.opacity = '1';
            item.style.transform = 'translateX(0)';
          }, index * 30);
        });
      }
    },

    handleInput() {
      // Очищаем предыдущий таймаут
      if (this.searchTimeout) {
        clearTimeout(this.searchTimeout);
      }

      this.noResults = false;
      this.resultsAnimated = false;

      // Определяем тип ввода
      if (this.isPlaylistLink || this.isAlbumLink) {
        // Обработка плейлиста/альбома
        this.searchResults = [];
        this.searchTimeout = setTimeout(() => {
          this.loadPlaylist();
        }, 500);
      } else if (this.isDirectLink) {
        // Прямая ссылка на трек - не ищем
        this.searchResults = [];
        this.playlistTracks = [];
      } else if (this.searchQuery.length >= 2) {
        // Поиск по названию с debounce
        this.playlistTracks = [];
        this.searchTimeout = setTimeout(() => {
          this.performSearch();
        }, 400);
      } else {
        this.searchResults = [];
        this.playlistTracks = [];
      }
    },

    async performSearch() {
      if (this.searchQuery.length < 2) return;

      this.isLoading = true;
      this.resultsAnimated = false;
      try {
        const response = await tracksApi.searchTracks(this.searchQuery, 10);
        this.searchResults = response.results || [];
        this.noResults = this.searchResults.length === 0;
        this.showResults = true;
      } catch (error) {
        console.error('Search error:', error);
        this.searchResults = [];
        this.noResults = true;
      } finally {
        this.isLoading = false;
      }
    },

    async loadPlaylist() {
      this.isLoading = true;
      this.resultsAnimated = false;
      try {
        const response = await tracksApi.getPlaylistTracks(this.searchQuery);
        this.playlistTracks = response.tracks || [];
        this.noResults = this.playlistTracks.length === 0;
        this.showResults = true;
      } catch (error) {
        console.error('Playlist load error:', error);
        this.playlistTracks = [];
        this.noResults = true;
      } finally {
        this.isLoading = false;
      }
    },

    handleEnter() {
      if (this.isDirectLink) {
        this.handleDirectLink();
      } else if (this.searchResults.length > 0) {
        // Добавить первый результат
        this.addTrack(this.searchResults[0]);
      }
    },

    handleDirectLink() {
      if (this.searchQuery.trim()) {
        this.$emit('send', this.searchQuery.trim());
        this.clearSearch();
      }
    },

    addTrack(track) {
      if (this.addedTracks.includes(track.id)) return;
      
      this.$emit('send', track.url);
      this.addedTracks.push(track.id);
      
      // Через 3 секунды убираем из "добавленных" чтобы можно было добавить снова
      setTimeout(() => {
        const index = this.addedTracks.indexOf(track.id);
        if (index > -1) {
          this.addedTracks.splice(index, 1);
        }
      }, 3000);
    },

    async addAllPlaylistTracks() {
      this.isAddingAll = true;
      
      for (const track of this.playlistTracks) {
        if (!this.addedTracks.includes(track.id)) {
          this.$emit('send', track.url);
          this.addedTracks.push(track.id);
          // Небольшая задержка между добавлениями
          await new Promise(resolve => setTimeout(resolve, 100));
        }
      }
      
      this.isAddingAll = false;
      this.showResults = false;
      this.clearSearch();
    },

    clearSearch() {
      this.searchQuery = '';
      this.searchResults = [];
      this.playlistTracks = [];
      this.showResults = false;
      this.noResults = false;
      this.resultsAnimated = false;
    },

    formatDuration(seconds) {
      if (!seconds) return '';
      const mins = Math.floor(seconds / 60);
      const secs = Math.floor(seconds % 60);
      return `${mins}:${secs.toString().padStart(2, '0')}`;
    }
  }
};
</script>

<style scoped>
.search-container {
  position: relative;
  width: 100%;
}

.input-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: rgba(23, 18, 34, 0.8);
  border-radius: 16px;
  border: 1px solid rgba(208, 188, 255, 0.15);
  transition: all 0.2s;
}

.input-wrapper:focus-within {
  border-color: rgba(139, 92, 246, 0.5);
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
}

.search-input {
  flex: 1;
  background: transparent;
  border: none;
  color: white;
  font-size: 14px;
  outline: none;
  min-width: 0;
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.input-actions {
  height: 28px;
  width: 28px;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(139, 92, 246, 0.3);
  border-top-color: #8b5cf6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.clear-btn {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.clear-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  color: white;
}

.send-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border: none;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.send-btn:hover:not(:disabled) {
  transform: scale(1.05);
  box-shadow: 0 0 15px rgba(139, 92, 246, 0.4);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.send-btn svg {
  margin-left: 2px;
}

/* Results dropdown */
.search-results {
  position: absolute;
  bottom: calc(100% + 8px);
  left: 0;
  right: 0;
  max-height: 400px;
  background: rgba(23, 18, 34, 0.98);
  border-radius: 16px;
  border: 1px solid rgba(208, 188, 255, 0.15);
  overflow: hidden;
  z-index: 100;
  box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.3);
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid rgba(208, 188, 255, 0.1);
  color: rgba(255, 255, 255, 0.7);
  font-size: 13px;
}

.add-all-btn {
  padding: 6px 12px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.add-all-btn:hover:not(:disabled) {
  transform: scale(1.02);
}

.add-all-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.results-list {
  list-style: none;
  margin: 0;
  padding: 0;
  max-height: 340px;
  overflow-y: auto;
}

.results-list::-webkit-scrollbar {
  width: 6px;
}

.results-list::-webkit-scrollbar-track {
  background: transparent;
}

.results-list::-webkit-scrollbar-thumb {
  background: rgba(139, 92, 246, 0.3);
  border-radius: 3px;
}

.result-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  cursor: pointer;
  transition: background 0.15s;
}

.result-item:hover {
  background: rgba(139, 92, 246, 0.1);
}

.result-item:hover .track-cover {
  transform: scale(1.05);
}

.result-item.added {
  background: rgba(34, 197, 94, 0.1);
}

.track-cover {
  width: 44px;
  height: 44px;
  border-radius: 8px;
  object-fit: cover;
  flex-shrink: 0;
  transition: transform 0.2s ease;
}

.track-cover-placeholder {
  width: 44px;
  height: 44px;
  border-radius: 8px;
  background: rgba(139, 92, 246, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #8b5cf6;
  font-size: 18px;
  flex-shrink: 0;
  transition: transform 0.2s ease;
}

.result-item:hover .track-cover-placeholder {
  transform: scale(1.05);
}

.track-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.track-title {
  color: white;
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: color 0.15s ease;
}

.result-item:hover .track-title {
  color: #d0bcff;
}

.track-artist {
  color: rgba(255, 255, 255, 0.5);
  font-size: 12px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.track-duration {
  color: rgba(255, 255, 255, 0.4);
  font-size: 12px;
  flex-shrink: 0;
}

.add-track-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(139, 92, 246, 0.2);
  border: none;
  color: #8b5cf6;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.add-track-btn:hover:not(:disabled) {
  background: rgba(139, 92, 246, 0.4);
  transform: scale(1.15);
  box-shadow: 0 0 12px rgba(139, 92, 246, 0.4);
}

.add-track-btn:active:not(:disabled) {
  transform: scale(0.95);
}

.add-track-btn:disabled {
  background: rgba(34, 197, 94, 0.3);
  color: #22c55e;
  cursor: default;
  animation: pulse-success 0.3s ease;
}

@keyframes pulse-success {
  0% { transform: scale(1); }
  50% { transform: scale(1.2); }
  100% { transform: scale(1); }
}

.no-results {
  position: absolute;
  bottom: calc(100% + 8px);
  left: 0;
  right: 0;
  padding: 20px;
  background: rgba(23, 18, 34, 0.98);
  border-radius: 16px;
  border: 1px solid rgba(208, 188, 255, 0.15);
  text-align: center;
  color: rgba(255, 255, 255, 0.5);
  font-size: 14px;
  z-index: 100;
  animation: fadeSlideIn 0.2s ease;
}

@keyframes fadeSlideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.results-overlay {
  position: fixed;
  inset: 0;
  z-index: 99;
}
</style>
<template>
  <div class="music-player">
    <!-- Прелоадер -->
    <div class="preloader" v-if="isLoading">
      <div class="preloader-content">
        <Logo class="Logo-player"></Logo>
        <div class="loading-text">Загрузка...</div>
      </div>
    </div>

    <!-- Основной контент -->
    <div class="player-container" v-show="!isLoading">
      <!-- Обложка -->
      <div class="cover-section" ref="frame">
        <img id="cover" src="" alt="Обложка" class="cover-image" ref="coverImage">
      </div>

      <!-- Информация и контролы -->
      <div class="player-content">
        <div class="song-info" ref="songInfo">
          <audio id="audio" preload="auto" ref="audioElement"></audio>
          <div class="song-title-row">
            <h2 class="song-title">{{ currentTrackTitle }}</h2>
            <button class="like-btn">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
              </svg>
            </button>
          </div>
          <p class="song-artist">{{ currentArtist }}</p>
        </div>

        <div class="player-controls">
          <TimeBar 
            :currentTime="currentTime" 
            :duration="duration" 
            @seek="onSeekLocal" 
            @seek-end="onSeekCommit"
            ref="timeBar" 
          />

          <div class="controls-row" ref="controls">
            <play-control-block 
              :is-playing="isPlaying" 
              @play="sendPlayCommand" 
              @pause="sendPauseCommand"
              @prev="prevTrack" 
              @next="nextTrack" 
              ref="playControl" 
            />
          </div>
          
          <div class="volume-row">
            <volume 
              v-if="!isLoading"
              :volume="currentVolume"
              @update:volume="handleVolumeUpdate"
              ref="volumeControl"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import playControlBlock from '@/components/play-control-block.vue';
import volume from '@/components/volume.vue';
import Logo from '@/assets/Logo-for-player.vue';
import TimeBar from '@/components/time-bar.vue';
import { sendSocketMessage } from '@/utils/playerSocket.js';
import { loadTrackMetadata, loadAudioStream, setupMediaSession, syncPlayback } from '@/utils/audioPlayer.js';
import { fetchQueue, formatParticipants } from '@/utils/roomData.js';
import { connectToRoom } from '@/utils/roomConnection.js';
import { gsap } from 'gsap';

export default {
  name: 'AudioPlayer',
  emits: ['participants-update', 'update-tracks', 'player-state'],
  
  components: {
    volume,
    Logo,
    playControlBlock,
    TimeBar
  },
  
  props: {
    roomId: {
      type: String,
      required: true
    }
  },
  
  data() {
    return {
      // Состояние загрузки
      isLoading: true,
      isInitialLoad: true,
      
      // Информация о треке
      currentTrackTitle: 'Название трека',
      currentArtist: 'Исполнитель',
      
      // Состояние воспроизведения
      isPlaying: false,
      currentTime: 0,
      duration: 0,
      currentVolume: 0.5,
      
      // Треки и очередь
      currentTrackIndex: 0,
      list_tracks: [],
      
      // WebSocket
      socket: null,
      userId: null,
      
      // Флаги синхронизации
      isSyncing: false,
      
      // Флаг намеренной паузы (чтобы не возобновлять в фоне)
      userInitiatedPause: false,
      
      // Внутренние переменные
      currentAudio: null,
      timeUpdateInterval: null,
      nextTrackTimeout: null,
      
      // Предзагрузка следующего трека
      preloadedTrack: null,
      
      // Состояние видимости вкладки
      wasPlayingBeforeHidden: false,
      
      // Интервал синхронизации времени в фоне
      backgroundSyncInterval: null,
      // Время когда вкладка была скрыта
      hiddenAtTime: 0,
      
      // Ожидаемый индекс трека (для синхронизации в фоне)
      expectedTrackIndex: 0,
      // Флаг загрузки трека в фоне
      pendingTrackLoad: null,
    };
  },

  async mounted() {
    console.log('[AudioPlayer] Mounted with roomId:', this.roomId);
    
    this.currentAudio = this.$refs.audioElement;
    
    if (!this.currentAudio) {
      console.error('Audio element not found');
      return;
    }

    this.setupAudioListeners();
    this.setupVisibilityHandler();
    await this.initWebSocket();
    
    // Интервал обновления времени
    this.timeUpdateInterval = setInterval(() => {
      if (this.currentAudio && !isNaN(this.currentAudio.duration)) {
        this.currentTime = this.currentAudio.currentTime;
        // Эмитим состояние плеера для внешних компонентов
        this.$emit('player-state', {
          currentTime: this.currentTime,
          duration: this.duration,
          isPlaying: this.isPlaying,
          isLoading: this.isLoading
        });
      }
    }, 250);

    this.handleVolumeUpdate(this.currentVolume);
  },

  beforeUnmount() {
    console.log('[AudioPlayer] Unmounting, roomId was:', this.roomId);
    
    if (this.socket) {
      this.socket.close(1000, "Page closed");
      this.socket = null;
    }
    if (this.timeUpdateInterval) {
      clearInterval(this.timeUpdateInterval);
    }
    if (this.nextTrackTimeout) {
      clearTimeout(this.nextTrackTimeout);
    }
    // Останавливаем фоновую синхронизацию
    if (this.backgroundSyncInterval) {
      clearInterval(this.backgroundSyncInterval);
    }
    // Удаляем обработчик видимости
    document.removeEventListener('visibilitychange', this.handleVisibilityChange);
  },

  methods: {
    // ============ ИНИЦИАЛИЗАЦИЯ ============
    
    setupVisibilityHandler() {
      // Обработка сворачивания/разворачивания вкладки
      this.handleVisibilityChange = async () => {
        if (document.hidden) {
          // Вкладка скрыта - запоминаем состояние и время
          this.wasPlayingBeforeHidden = this.isPlaying;
          this.hiddenAtTime = this.currentAudio.currentTime;
          this.expectedTrackIndex = this.currentTrackIndex;
          
          // Запускаем периодическую синхронизацию времени с сервером
          this.startBackgroundSync();
        } else {
          // Вкладка снова видна - останавливаем фоновую синхронизацию
          this.stopBackgroundSync();
          
          // Проверяем, есть ли отложенная загрузка трека
          if (this.pendingTrackLoad) {
            const { url, index, shouldPlay } = this.pendingTrackLoad;
            this.pendingTrackLoad = null;
            
            // Загружаем отложенный трек
            await this.loadTrack(url, {
              autoPlay: shouldPlay,
              startTime: 0
            });
            this.currentTrackIndex = index;
            this.expectedTrackIndex = index;
            this.$emit('update-tracks', this.list_tracks, this.currentTrackIndex);
            return;
          }
          
          // Запрашиваем состояние комнаты для проверки синхронизации
          if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            // Отправляем текущее локальное время на сервер
            if (this.isPlaying || this.wasPlayingBeforeHidden) {
              sendSocketMessage(this.socket, {
                type: 'sync_time',
                position: this.currentAudio.currentTime
              });
            }
            // Запрашиваем состояние комнаты
            sendSocketMessage(this.socket, { type: 'sync_state' });
          }
          
          // Небольшая задержка для обработки sync_state
          await new Promise(r => setTimeout(r, 200));
          
          // Возобновляем воспроизведение если было активно и пауза
          if (this.wasPlayingBeforeHidden && this.currentAudio.paused) {
            try {
              await this.currentAudio.play();
              this.isPlaying = true;
            } catch (e) {
              // Ошибка возобновления воспроизведения
            }
          }
        }
      };
      document.addEventListener('visibilitychange', this.handleVisibilityChange);
    },
    
    startBackgroundSync() {
      // Синхронизируем время каждые 5 секунд пока вкладка в фоне
      if (this.backgroundSyncInterval) return;
      
      this.backgroundSyncInterval = setInterval(() => {
        if (this.socket && this.socket.readyState === WebSocket.OPEN && this.isPlaying) {
          sendSocketMessage(this.socket, {
            type: 'sync_time',
            position: this.currentAudio.currentTime
          });
        }
      }, 5000);
    },
    
    stopBackgroundSync() {
      if (this.backgroundSyncInterval) {
        clearInterval(this.backgroundSyncInterval);
        this.backgroundSyncInterval = null;
      }
    },
    
    setupAudioListeners() {
      let isTrackEnding = false;

      this.currentAudio.addEventListener('ended', async () => {
        if (isTrackEnding) return;
        isTrackEnding = true;
        
        // Небольшая задержка для предотвращения двойного срабатывания
        await new Promise(resolve => setTimeout(resolve, 200));

        // Переключаем на следующий трек (работает и в фоне)
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
          sendSocketMessage(this.socket, { type: 'next_track' });
        }

        // Сбрасываем флаг через секунду
        setTimeout(() => { isTrackEnding = false; }, 1000);
      });

      this.currentAudio.addEventListener('timeupdate', () => {
        if (!this.isSyncing) {
          this.currentTime = this.currentAudio.currentTime;
        }
      });

      this.currentAudio.addEventListener('loadedmetadata', () => {
        if (this.currentAudio && Number.isFinite(this.currentAudio.duration)) {
          this.duration = this.currentAudio.duration;
        }
      });
      
      // Обработка паузы браузером (при сворачивании)
      this.currentAudio.addEventListener('pause', () => {
        // Если это намеренная пауза от пользователя - не возобновляем
        if (this.userInitiatedPause) {
          return;
        }
        
        // Если пауза не от пользователя и вкладка скрыта - это браузер
        if (document.hidden && this.wasPlayingBeforeHidden) {
          // Пробуем возобновить
          setTimeout(() => {
            if (document.hidden && this.wasPlayingBeforeHidden && !this.userInitiatedPause) {
              this.currentAudio.play().catch(() => {});
            }
          }, 100);
        }
      });
    },

    async initWebSocket() {
      try {
        const { socket, userId } = connectToRoom(this.roomId, (data) => this.handleSocketMessage(data));
        this.socket = socket;
        this.userId = userId;
      } catch (e) {
        console.error('WebSocket error:', e);
        alert('Требуется авторизация');
      }
    },

    // ============ УПРАВЛЕНИЕ ГРОМКОСТЬЮ ============
    
    handleVolumeUpdate(volume) {
      this.currentVolume = volume;
      if (this.currentAudio) {
        this.currentAudio.volume = volume;
      }
    },

    // ============ УПРАВЛЕНИЕ ТРЕКАМИ ============
    
    updateTracksList(tracksArray, currentIndex) {
      this.list_tracks = tracksArray;
      this.currentTrackIndex = currentIndex;
      this.$emit('update-tracks', tracksArray, currentIndex);
    },

    async loadTrack(trackUrl, options = {}) {
      const { callback, autoPlay = false, startTime = 0 } = typeof options === 'function' 
        ? { callback: options } 
        : options;
      
      try {
        // Анимация исчезновения (кроме первой загрузки)
        if (!this.isInitialLoad) {
          await gsap.to(
            [this.$refs.coverImage, this.$refs.songInfo],
            { opacity: 0, y: 20, duration: 0.4, ease: 'power2.in' }
          );
        } else {
          this.isLoading = true;
          this.isInitialLoad = false;
        }

        // Загружаем метаданные
        const metadata = await loadTrackMetadata(trackUrl, this.userId);
        
        this.currentTrackTitle = metadata.title;
        this.currentArtist = metadata.artist;
        this.$refs.coverImage.src = metadata.cover;

        // Устанавливаем duration из API сразу (для отображения в UI)
        if (metadata.duration) {
          this.duration = metadata.duration;
        }

        // Загружаем аудио (передаём известную длительность)
        const loadedDuration = await loadAudioStream(
          this.currentAudio, 
          metadata.streamUrl, 
          metadata.duration
        );
        
        // Обновляем duration если браузер определил точнее
        if (loadedDuration && isFinite(loadedDuration)) {
          this.duration = loadedDuration;
        }

        // Настраиваем Media Session
        setupMediaSession(metadata, {
          play: () => this.sendPlayCommand(),
          pause: () => this.sendPauseCommand(),
          previoustrack: () => this.prevTrack(),
          nexttrack: () => this.nextTrack(),
        });

        // Устанавливаем позицию если указана
        if (startTime > 0) {
          this.currentAudio.currentTime = startTime;
        }

        // Автовоспроизведение при переключении трека
        if (autoPlay) {
          try {
            await this.currentAudio.play();
            this.isPlaying = true;
          } catch (e) {
            // AutoPlay заблокирован браузером
          }
        }

        // Callback и скрытие прелоадера
        if (callback) callback();
        if (this.isLoading) this.hideLoader();

        // Анимация появления
        await gsap.fromTo(
          [this.$refs.coverImage, this.$refs.songInfo],
          { opacity: 0, y: -20 },
          { opacity: 0.8, y: 0, duration: 0.6, ease: 'power2.out', stagger: 0.1 }
        );
        
        // Предзагрузка следующего трека (асинхронно, не блокирует)
        this.preloadNextTrack();
      } catch (error) {
        console.error('Ошибка загрузки трека:', error);
        if (this.isLoading) this.hideLoader();
      }
    },
    
    // Предзагрузка метаданных и ссылки следующего трека
    async preloadNextTrack() {
      if (this.list_tracks.length <= 1) return;
      
      const nextIndex = (this.currentTrackIndex + 1) % this.list_tracks.length;
      const nextTrackUrl = this.list_tracks[nextIndex]?.url || this.list_tracks[nextIndex];
      
      if (!nextTrackUrl || typeof nextTrackUrl !== 'string') return;
      
      try {
        // Предзагружаем метаданные следующего трека
        const metadata = await loadTrackMetadata(nextTrackUrl, this.userId);
        this.preloadedTrack = {
          index: nextIndex,
          url: nextTrackUrl,
          metadata: metadata
        };
        
        // Предзагружаем начало аудио в кэш браузера
        if (metadata.streamUrl) {
          const preloadLink = document.createElement('link');
          preloadLink.rel = 'prefetch';
          preloadLink.href = metadata.streamUrl;
          preloadLink.as = 'audio';
          document.head.appendChild(preloadLink);
          
          // Удаляем через 30 секунд
          setTimeout(() => preloadLink.remove(), 15000);
        }
      } catch (e) {
        // Ошибка предзагрузки (некритично)
      }
    },

    // ============ КОМАНДЫ ВОСПРОИЗВЕДЕНИЯ ============
    
    async sendPlayCommand() {
      // Сбрасываем флаг намеренной паузы
      this.userInitiatedPause = false;
      
      // Сначала выполняем локально - важно для фонового режима
      try {
        await this.currentAudio.play();
        this.isPlaying = true;
        this.wasPlayingBeforeHidden = true;
        
        // Обновляем Media Session
        if ('mediaSession' in navigator) {
          navigator.mediaSession.playbackState = 'playing';
        }
      } catch (e) {
        // Ошибка воспроизведения
      }
      
      // Отправляем на сервер
      sendSocketMessage(this.socket, {
        type: 'play',
        position: this.currentAudio.currentTime
      });
    },

    async sendPauseCommand() {
      // Отмечаем что это намеренная пауза
      this.userInitiatedPause = true;
      
      // Сначала выполняем локально - важно для фонового режима
      this.currentAudio.pause();
      this.isPlaying = false;
      this.wasPlayingBeforeHidden = false;
      
      // Обновляем Media Session
      if ('mediaSession' in navigator) {
        navigator.mediaSession.playbackState = 'paused';
      }
      
      // Отправляем на сервер
      sendSocketMessage(this.socket, {
        type: 'pause',
        position: this.currentAudio.currentTime
      });
    },

    async onSeek(currentTime) {
      if (!this.isSyncing && this.currentAudio) {
        this.currentAudio.currentTime = currentTime;
        this.sendSeekCommand(currentTime);
      }
    },

    // Локальный seek (во время перетаскивания) - только локальное обновление + broadcast
    async onSeekLocal(currentTime) {
      if (!this.isSyncing && this.currentAudio) {
        this.currentAudio.currentTime = currentTime;
        // Отправляем другим участникам без сохранения в БД
        sendSocketMessage(this.socket, {
          type: 'seek',
          position: currentTime
        });
      }
    },

    // Финальный seek (когда отпустил ползунок) - сохраняем в БД
    async onSeekCommit(currentTime) {
      if (!this.isSyncing && this.currentAudio) {
        this.currentAudio.currentTime = currentTime;
        // Сохраняем финальную позицию в БД
        sendSocketMessage(this.socket, {
          type: 'seek_commit',
          position: currentTime
        });
      }
    },

    async sendSeekCommand(position) {
      sendSocketMessage(this.socket, {
        type: 'seek',
        position
      });
    },

    // Методы для внешнего управления
    seekTo(time) {
      this.onSeek(time);
    },
    
    setVolume(value) {
      this.handleVolumeUpdate(value);
    },

    prevTrack() {
      this.sendPrevTrack();
    },

    nextTrack() {
      this.sendNextTrack();
    },

    async sendNextTrack() {
      if (this.nextTrackTimeout) clearTimeout(this.nextTrackTimeout);

      this.nextTrackTimeout = setTimeout(async () => {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
          sendSocketMessage(this.socket, { type: 'next_track' });
        }
        this.nextTrackTimeout = null;
      }, 200);
    },

    async sendPrevTrack() {
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        // Если трек играет больше 5 секунд - возвращаем на начало
        if (this.currentAudio.currentTime > 5) {
          this.onSeek(0);
        } else {
          // Иначе переключаем на предыдущий трек
          sendSocketMessage(this.socket, { type: 'previous_track' });
        }
      }
    },

    async playTrack(url) {
      if (!url.includes('music.yandex.')) {
        alert('Пожалуйста, введите ссылку Яндекс.Музыки');
        return;
      }

      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        this.sendAddTrack(url);
      }
    },

    async sendAddTrack(trackUrl) {
      sendSocketMessage(this.socket, {
        type: 'add_track',
        tracks: [trackUrl]
      });
    },

    // Воспроизвести трек по индексу (клик в очереди)
    playTrackByIndex(index) {
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        sendSocketMessage(this.socket, {
          type: 'play_track_by_index',
          index: index
        });
      }
    },

    // Отправить новый порядок треков на сервер
    sendReorderTracks(newTracks, newCurrentIndex, oldIndex, newIndex) {
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        // Извлекаем URL-ы из объектов метаданных для сервера
        const trackUrls = newTracks.map(track => track.url || track);
        
        sendSocketMessage(this.socket, {
          type: 'reorder_tracks',
          tracks: trackUrls,
          index: newCurrentIndex,
          old_index: oldIndex,
          new_index: newIndex
        });
      }
    },

    // Удалить трек из очереди (отправка на сервер)
    removeTrack(index) {
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        sendSocketMessage(this.socket, {
          type: 'remove_track',
          index: index
        });
      }
    },

    // ============ ОБРАБОТКА СООБЩЕНИЙ WEBSOCKET ============
    
    async handleSocketMessage(data) {
      switch (data.type) {
        case 'request_current_time':
          sendSocketMessage(this.socket, {
            type: "current_time",
            position: this.currentAudio.currentTime,
            request_id: data.request_id
          });
          break;

        case 'init':
          // Всегда загружаем очередь для синхронизации состояния
          const queueData = await fetchQueue(this.roomId);
          this.updateTracksList(queueData.list_track || [], queueData.index || 0);
          
          // Инициализируем ожидаемый индекс
          this.expectedTrackIndex = queueData.index || 0;
          
          // Загружаем трек только если он есть
          if (data.track_url) {
            await this.loadTrack(data.track_url, {
              autoPlay: data.is_playing,
              startTime: data.current_time || 0
            });
          } else {
            // Для пустой комнаты сбрасываем состояние плеера
            this.isLoading = false;
            this.isInitialLoad = false;
            this.currentTrackTitle = 'Добавьте треки';
            this.currentArtist = '';
          }
          break;

        case 'track_state':
          await this.loadTrack(data.url, {
            autoPlay: data.is_playing,
            startTime: data.position || 0
          });
          break;

        case 'state_sync':
          // Синхронизация состояния при возврате из фоновой вкладки
          // Проверяем индекс трека - если отличается или есть ожидаемый индекс
          const serverIndex = data.index;
          const needsTrackSync = serverIndex !== this.currentTrackIndex || 
                                  serverIndex !== this.expectedTrackIndex;
          
          if (needsTrackSync && data.track_url) {
            // Если уже есть pendingTrackLoad с этим индексом - не загружаем повторно
            if (this.pendingTrackLoad && this.pendingTrackLoad.index === serverIndex) {
              this.currentTrackIndex = serverIndex;
              this.expectedTrackIndex = serverIndex;
              this.$emit('update-tracks', this.list_tracks, this.currentTrackIndex);
            } else {
              this.currentTrackIndex = serverIndex;
              this.expectedTrackIndex = serverIndex;
              this.$emit('update-tracks', this.list_tracks, this.currentTrackIndex);
              
              // Загружаем правильный трек
              await this.loadTrack(data.track_url, {
                autoPlay: data.is_playing,
                startTime: data.current_time || 0
              });
            }
            this.isPlaying = data.is_playing;
            this.wasPlayingBeforeHidden = data.is_playing;
          } else {
            // Трек тот же - НЕ перематываем если локальное время впереди (играли в фоне)
            const localTime = this.currentAudio.currentTime;
            const serverTime = data.current_time || 0;
            
            // Если сервер впереди более чем на 2 секунды - синхронизируемся
            if (serverTime > localTime + 2) {
              this.currentAudio.currentTime = serverTime;
            }
            
            // Синхронизируем состояние play/pause
            if (data.is_playing && this.currentAudio.paused) {
              this.currentAudio.play().catch(() => {});
              this.isPlaying = true;
            } else if (!data.is_playing && !this.currentAudio.paused) {
              this.currentAudio.pause();
              this.isPlaying = false;
            }
            this.wasPlayingBeforeHidden = data.is_playing;
          }
          break;

        case 'play':
          this.handlePlayMessage(data);
          // В фоне тоже обновляем флаг
          this.wasPlayingBeforeHidden = true;
          break;

        case 'pause':
          this.handlePauseMessage(data);
          // В фоне тоже обновляем флаг
          this.wasPlayingBeforeHidden = false;
          break;

        case 'change_track':
          if (data.tracks && data.tracks.length > 0 && !this.isSyncing) {
            await this.loadTrack(data.tracks[data.index], {
              autoPlay: true  // Всегда автовоспроизведение при смене трека
            });
          }
          if (data.tracks) {
            this.updateTracksList(data.tracks, data.index);
          }
          break;

        case 'seek':
          this.handleSeekMessage(data);
          break;

        case 'participants_update':
          const formattedParticipants = formatParticipants(data.participants);
          this.$emit('participants-update', formattedParticipants);
          break;

        case 'load_track':
          // При переключении трека обновляем ожидаемый индекс
          this.expectedTrackIndex = data.index;
          
          // Если вкладка в фоне - откладываем загрузку на момент возврата
          // НО аудио всё равно загружаем для Media Session
          if (document.hidden) {
            // Сохраняем информацию для UI при возврате из фона
            this.pendingTrackLoad = {
              url: data.url,
              index: data.index,
              shouldPlay: true
            };
            
            // Обновляем индекс сразу
            this.currentTrackIndex = data.index;
            this.$emit('update-tracks', this.list_tracks, this.currentTrackIndex);
            
            // Загружаем аудио в фоне (без UI анимаций)
            try {
              const metadata = await loadTrackMetadata(data.url, this.userId);
              
              // Обновляем данные трека
              this.currentTrackTitle = metadata.title;
              this.currentArtist = metadata.artist;
              
              // Обновляем Media Session для системных контролов
              setupMediaSession(metadata, {
                play: () => this.sendPlayCommand(),
                pause: () => this.sendPauseCommand(),
                previoustrack: () => this.prevTrack(),
                nexttrack: () => this.nextTrack(),
              });
              
              // Загружаем аудио
              await loadAudioStream(this.currentAudio, metadata.streamUrl, metadata.duration);
              if (metadata.duration) {
                this.duration = metadata.duration;
              }
              
              // Пробуем воспроизвести
              try {
                await this.currentAudio.play();
                this.isPlaying = true;
                this.wasPlayingBeforeHidden = true;
                // Если удалось воспроизвести - очищаем pending
                this.pendingTrackLoad = null;
              } catch (playError) {
                // Background autoplay заблокирован
                this.wasPlayingBeforeHidden = true;
              }
            } catch (e) {
              // Ошибка загрузки трека в фоне
              this.wasPlayingBeforeHidden = true;
            }
          } else {
            // Вкладка активна - нормальная загрузка с UI
            this.currentTrackIndex = data.index;
            this.$emit('update-tracks', this.list_tracks, this.currentTrackIndex);
            
            try {
              await this.loadTrack(data.url, { 
                autoPlay: true
              });
              this.isPlaying = true;
            } catch (e) {
              // Ошибка загрузки трека
            }
          }
          break;

        case 'track_removed':
          // Обработка удаления трека - обновляем локальный массив
          if (data.removed_index !== undefined && this.list_tracks.length > 0) {
            // Удаляем элемент из локального массива метаданных
            this.list_tracks.splice(data.removed_index, 1);
            this.currentTrackIndex = data.index;
            
            // Если удалили текущий трек - нужно загрузить новый
            if (data.removed_current && this.list_tracks.length > 0) {
              const newTrackUrl = this.list_tracks[data.index]?.url || this.list_tracks[data.index];
              if (newTrackUrl) {
                await this.loadTrack(newTrackUrl, { autoPlay: this.isPlaying });
              }
            }
            
            this.updateTracksList([...this.list_tracks], this.currentTrackIndex);
          }
          break;

        case 'tracks_reordered':
          // Обработка перемещения треков другим участником
          // data.tracks содержит новый порядок URL-ов, нужно переставить локальные данные
          if (data.tracks && data.old_index !== undefined && data.new_index !== undefined) {
            // Переставляем элемент в локальном массиве метаданных
            const [movedTrack] = this.list_tracks.splice(data.old_index, 1);
            this.list_tracks.splice(data.new_index, 0, movedTrack);
            this.currentTrackIndex = data.index;
            this.updateTracksList([...this.list_tracks], this.currentTrackIndex);
          }
          break;

        case 'add_track':
          // Запрашиваем метаданные нового трека, включая URL
          const newTrackData = await fetchQueue(this.roomId, data.track_id);
          if (newTrackData.new_track) {
            // Добавляем URL к метаданным если не пришёл с сервера
            const newTrack = {
              ...newTrackData.new_track,
              url: newTrackData.new_track.url || data.track_url || `https://music.yandex.ru/track/${data.track_id}`
            };
            this.list_tracks.push(newTrack);
            this.updateTracksList([...this.list_tracks], this.currentTrackIndex);
          }
          break;
      }
    },

    handlePlayMessage(data) {
      this.isSyncing = true;
      this.userInitiatedPause = false;  // Сбрасываем флаг паузы
      this.isPlaying = syncPlayback(this.currentAudio, true, data.position);
      this.currentAudio.play().catch(() => {});
      this.wasPlayingBeforeHidden = true;
      
      // Обновляем состояние Media Session
      if ('mediaSession' in navigator) {
        navigator.mediaSession.playbackState = 'playing';
      }
      setTimeout(() => { this.isSyncing = false; }, 100);
    },

    handlePauseMessage(data) {
      this.isSyncing = true;
      this.userInitiatedPause = true;  // Устанавливаем флаг паузы
      this.isPlaying = syncPlayback(this.currentAudio, false, data.position);
      this.currentAudio.pause();
      this.wasPlayingBeforeHidden = false;
      
      // Обновляем состояние Media Session
      if ('mediaSession' in navigator) {
        navigator.mediaSession.playbackState = 'paused';
      }
      setTimeout(() => { this.isSyncing = false; }, 100);
    },

    handleSeekMessage(data) {
      if (!this.isSyncing) {
        this.isSyncing = true;
        this.currentAudio.currentTime = data.position;
        setTimeout(() => { this.isSyncing = false; }, 100);
      }
    },

    // ============ АНИМАЦИИ ============
    
    async hideLoader() {
      await gsap.to(".preloader", {
        opacity: 0,
        duration: 0.8,
        ease: "power2.out",
        onComplete: () => {
          this.isLoading = false;
          this.$nextTick(() => this.playEntranceAnimation());
        }
      });
    },

    async playEntranceAnimation() {
      if (!this.$refs.frame || !this.$refs.coverImage || !this.$refs.songInfo) {
        return;
      }

      const tl = gsap.timeline();

      tl.from(this.$refs.frame, {
        scale: 0.9,
        y: 30,
        opacity: 0,
        duration: 1,
        ease: "back.out(1.7)"
      })
      .from(this.$refs.coverImage, {
        scale: 1.1,
        opacity: 0,
        duration: 1.2,
        ease: "power2.out"
      }, "-=0.5")
      .from(this.$refs.songInfo.children, {
        y: 20,
        opacity: 0,
        duration: 0.7,
        stagger: 0.1,
        ease: "power2.out"
      });

      if (this.$refs.timeBar?.$el) {
        tl.from(this.$refs.timeBar.$el, {
          scaleX: 0,
          duration: 1,
          transformOrigin: "left center",
          ease: "power3.out"
        }, "<+0.5");
      }

      if (this.$refs.playControl?.$el) {
        tl.from(this.$refs.playControl.$el, {
          y: 20,
          opacity: 0,
          duration: 0.8,
          ease: "elastic.out(1, 0.5)"
        }, "<+0.5");
      }

      if (this.$refs.volumeControl?.$el) {
        tl.from(this.$refs.volumeControl.$el, {
          y: 30,
          opacity: 0,
          duration: 0.8,
          ease: "elastic.out(1, 0.5)"
        }, "-=0.3");
      }

      return tl;
    },
  }
};
</script>

<style scoped>
.music-player {
  width: 100%;
  height: 100%;
  min-height: 320px;
  background: rgba(23, 18, 34, 0.5);
  border-radius: 24px;
  backdrop-filter: blur(10px);
  padding: 20px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

.player-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.preloader {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 24px;
  backdrop-filter: blur(10px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 100;
  background: rgba(23, 18, 34, 0.9);
}

.preloader-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.Logo-player {
  width: 60px;
  height: 60px;
  opacity: 0.8;
}

.loading-text {
  color: rgba(255, 255, 255, 0.6);
  font-size: 13px;
  letter-spacing: 1px;
}

/* Cover Section */
.cover-section {
  width: 100%;
  aspect-ratio: 1/1;
  max-height: 180px;
  margin: 0 auto;
  background: rgba(18, 11, 33, 0.5);
  border-radius: 12px;
  overflow: hidden;
  flex-shrink: 0;
}

.cover-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Song Info */
.player-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.song-info {
  margin-bottom: 12px;
  flex-shrink: 0;
}

.song-title-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 10px;
}

.song-title {
  font-size: 16px;
  font-weight: 600;
  color: #D0BCFF;
  margin: 0;
  line-height: 1.3;
  word-break: break-word;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
}

.like-btn {
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  padding: 4px;
  flex-shrink: 0;
  transition: all 0.2s;
}

.like-btn:hover {
  color: #ff6b9d;
}

.song-artist {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
  margin: 4px 0 0 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Controls */
.player-controls {
  margin-top: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.controls-row {
  display: flex;
  justify-content: center;
  padding: 4px 0;
}

.volume-row {
  display: flex;
  justify-content: center;
  padding-top: 4px;
}

/* Responsive */
@media (max-width: 1100px) {
  .music-player {
    flex-direction: row;
    min-height: auto;
    gap: 20px;
    padding: 16px;
  }
  
  .player-container {
    flex-direction: row;
    align-items: center;
  }
  
  .cover-section {
    width: 120px;
    height: 120px;
    max-height: none;
    flex-shrink: 0;
  }
  
  .player-content {
    flex: 1;
  }
  
  .player-controls {
    margin-top: 0;
  }
}

@media (max-width: 768px) {
  .music-player {
    padding: 12px 16px;
    min-height: auto;
    border-radius: 20px 20px 0 0;
    background: linear-gradient(180deg, rgba(30, 25, 50, 0.98) 0%, rgba(20, 15, 35, 0.99) 100%);
    backdrop-filter: blur(25px);
    -webkit-backdrop-filter: blur(25px);
    box-shadow: 0 -8px 40px rgba(0, 0, 0, 0.5);
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 200;
  }
  
  .player-container {
    gap: 12px;
  }
  
  .cover-section {
    width: 56px;
    height: 56px;
    border-radius: 10px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
    flex-shrink: 0;
  }

  .song-title {
    font-size: 14px;
    font-weight: 600;
    -webkit-line-clamp: 1;
    line-clamp: 1;
    color: white;
  }

  .song-artist {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.6);
  }
  
  .song-info {
    margin-bottom: 0;
    flex: 1;
    min-width: 0;
  }
  
  .song-title-row {
    align-items: center;
    gap: 8px;
  }
  
  .like-btn {
    padding: 8px;
    margin-right: -4px;
  }
  
  .player-controls {
    gap: 8px;
  }
  
  .controls-row {
    padding: 0;
    transform: scale(0.9);
    transform-origin: center;
  }
  
  /* Hide volume on mobile - like Spotify */
  .volume-row {
    display: none;
  }
  
  /* TimeBar компактнее */
  .player-content {
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .music-player {
    padding: 8px 12px 12px;
    border-radius: 16px 16px 0 0;
  }
  
  .player-container {
    gap: 10px;
  }
  
  .cover-section {
    width: 48px;
    height: 48px;
    border-radius: 8px;
  }
  
  .song-title {
    font-size: 13px;
  }
  
  .song-artist {
    font-size: 10px;
  }
  
  .controls-row {
    transform: scale(0.85);
  }
}
</style>

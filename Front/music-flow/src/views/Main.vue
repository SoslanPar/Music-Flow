<template>
  <div class="main-wrapper">
    <!-- Header -->
    <header class="main-header">
      <div class="header-left">
        <!-- Кнопка для открытия комнат на десктопе -->
        <button v-if="connected" class="rooms-menu-btn" @click="showRoomsDropdown = !showRoomsDropdown">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <path d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z"/>
          </svg>
        </button>
        
        <!-- Мобильная кнопка sidebar -->
        <button v-if="connected" class="sidebar-toggle mobile-only" @click="sidebarOpen = !sidebarOpen">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5z"/>
          </svg>
        </button>
        
        <Logo class="header-logo-full" />
        
        <!-- Dropdown с комнатами на десктопе -->
        <div v-if="showRoomsDropdown" class="rooms-dropdown">
          <div class="rooms-dropdown-header">
            <span>Ваши комнаты</span>
            <button class="add-room-small-btn" @click.stop="showCreateRoomModal = true">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
              </svg>
            </button>
          </div>
          <ul class="rooms-dropdown-list">
            <li 
              v-for="room in rooms" 
              :key="room.id" 
              class="rooms-dropdown-item"
              :class="{ 'current': room.id === roomId }"
              @click="switchRoom(room)"
            >
              <div class="room-avatar-small">{{ room.name.charAt(0).toUpperCase() }}</div>
              <span>{{ room.name }}</span>
              <span v-if="room.id === roomId" class="current-badge">Сейчас</span>
            </li>
            <li v-if="rooms.length === 0" class="empty-dropdown-item">Нет комнат</li>
          </ul>
        </div>
      </div>
      
      <div class="header-center" v-if="connected && currentRoomName">
        <span class="room-title">{{ currentRoomName }}</span>
      </div>
      
      <div class="header-right">
        <button class="icon-btn help-btn" title="Помощь">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 17h-2v-2h2v2zm2.07-7.75l-.9.92C13.45 12.9 13 13.5 13 15h-2v-.5c0-1.1.45-2.1 1.17-2.83l1.24-1.26c.37-.36.59-.86.59-1.41 0-1.1-.9-2-2-2s-2 .9-2 2H8c0-2.21 1.79-4 4-4s4 1.79 4 4c0 .88-.36 1.68-.93 2.25z"/>
          </svg>
        </button>
        
        <!-- Меню аккаунта -->
        <div class="account-menu-wrapper">
          <button class="icon-btn account-btn" @click="showAccountMenu = !showAccountMenu">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"/>
            </svg>
          </button>
          
          <!-- Dropdown меню -->
          <div v-if="showAccountMenu" class="account-dropdown">
            <div class="dropdown-item user-info">
              <span class="user-name">{{ userName }}</span>
            </div>
            <button class="dropdown-item logout-btn" @click="handleLogout">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                <path d="M17 7l-1.41 1.41L18.17 11H8v2h10.17l-2.58 2.58L17 17l5-5zM4 5h8V3H4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h8v-2H4V5z"/>
              </svg>
              <span>Выйти</span>
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <div class="main-content">
      <!-- Sidebar (когда в комнате) -->
      <aside v-if="connected" class="sidebar" :class="{ 'sidebar-open': sidebarOpen }">
        <div class="sidebar-section">
          <div class="sidebar-header">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/>
            </svg>
            <span>Участники</span>
          </div>
          <ul class="sidebar-list friends-list">
            <li v-for="participant in participants" :key="participant.id" class="sidebar-item">
              <div class="item-avatar" :class="{ 'you': participant.id === userId }">
                {{ participant.name.charAt(0).toUpperCase() }}
              </div>
              <span class="item-name">{{ participant.name }}</span>
              <span v-if="participant.id === userId" class="you-badge">Вы</span>
            </li>
            <li v-if="participants.length === 0" class="empty-item">
              Нет участников
            </li>
          </ul>
        </div>
        
        <!-- Кнопка выхода в sidebar для мобильных -->
        <div class="sidebar-section sidebar-leave-section">
          <button class="sidebar-leave-btn" @click="leaveRoom">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
              <path d="M10.09 15.59L11.5 17l5-5-5-5-1.41 1.41L12.67 11H3v2h9.67l-2.58 2.59zM19 3H5c-1.11 0-2 .9-2 2v4h2V5h14v14H5v-4H3v4c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2z"/>
            </svg>
            <span>Выйти из комнаты</span>
          </button>
        </div>
      </aside>

      <!-- Rooms View (не подключены) -->
      <div v-if="!connected" class="rooms-view">
        <aside class="rooms-sidebar">
          <div class="sidebar-section">
            <div class="sidebar-header clickable" @click="showFriends = !showFriends">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                <path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/>
              </svg>
              <span>Friends</span>
              <svg class="chevron" :class="{ 'expanded': showFriends }" width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M7 10l5 5 5-5z"/>
              </svg>
            </div>
            <ul v-if="showFriends" class="sidebar-list friends-list">
              <li class="empty-item">Скоро...</li>
            </ul>
          </div>
          
          <div class="sidebar-section rooms-section">
            <div class="sidebar-header">
              <span>Rooms</span>
              <button class="add-room-btn" @click="showCreateRoom = true" title="Создать комнату">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
                </svg>
              </button>
            </div>
            
            <div v-if="loadingRooms" class="loading-rooms">
              <span>Загрузка...</span>
            </div>
            
            <ul v-else class="sidebar-list rooms-list">
              <li 
                v-for="room in rooms" 
                :key="room.id" 
                class="sidebar-item room-item"
                :class="{ 'selected': selectedRoom === room.id }"
                draggable="true"
                @dragstart="onRoomDragStart($event, room)"
                @dragover.prevent
                @drop="onRoomDrop($event, room)"
                @click="selectRoom(room)"
              >
                <div class="drag-handle">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M11 18c0 1.1-.9 2-2 2s-2-.9-2-2 .9-2 2-2 2 .9 2 2zm-2-8c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm0-6c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm6 4c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zm0 2c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm0 6c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z"/>
                  </svg>
                </div>
                <div class="item-avatar room-avatar">
                  {{ room.name.charAt(0).toUpperCase() }}
                </div>
                <span class="item-name">{{ room.name }}</span>
                <div class="room-meta" v-if="room.participants_count > 0">
                  <span class="participants-count">{{ room.participants_count }}</span>
                </div>
                <button 
                  v-if="selectedRoom === room.id" 
                  class="join-btn" 
                  @click.stop="joinRoom(room.id)"
                >
                  Войти
                </button>
              </li>
              <li v-if="rooms.length === 0 && !loadingRooms" class="empty-item">
                У вас пока нет комнат
              </li>
            </ul>
            
            <!-- Создание комнаты -->
            <div v-if="showCreateRoom" class="create-room-form">
              <input 
                v-model="newRoomName" 
                placeholder="Название комнаты"
                class="create-room-input"
                @keyup.enter="createRoom"
                ref="newRoomInput"
              />
              <div class="create-room-buttons">
                <button class="btn-cancel" @click="showCreateRoom = false">Отмена</button>
                <button class="btn-create" @click="createRoom" :disabled="!newRoomName.trim()">Создать</button>
              </div>
            </div>
            
            <!-- Быстрый вход по ID -->
            <div class="quick-join">
              <input 
                v-model="roomIdInput" 
                placeholder="ID комнаты"
                class="quick-join-input"
                @keyup.enter="quickJoin"
              />
              <button class="quick-join-btn" @click="quickJoin" :disabled="!roomIdInput.trim()">Войти</button>
            </div>
          </div>
        </aside>
        
        <div class="rooms-main-area">
          <div class="welcome-message">
            <Logo class="welcome-logo" />
            <h2>Добро пожаловать в Music Flow</h2>
            <p>Выберите комнату слева или создайте новую</p>
          </div>
        </div>
      </div>

      <!-- Room View (подключены к комнате) -->
      <div v-else class="room-view">
        <!-- Центральный блок: Очередь треков -->
        <div class="center-column">
          <div class="track-queue-wrapper">
            <TrackQueue 
              :tracks="tracks" 
              :currentTrackIndex="currentTrackIndex"
              :isPlaying="isPlayerPlaying"
              :isLoading="isQueueLoading"
              @reorder="onTracksReorder"
              @play-track="onPlayTrack"
              @delete-track="onDeleteTrack"
            />
          </div>
          <div class="send-track-wrapper">
            <SendTrack @send="handleSendTrack"/>
          </div>
        </div>
      </div>
      
      <!-- Скрытый AudioPlayer для управления воспроизведением -->
      <AudioPlayer
        v-if="connected"
        ref="audioPlayer"
        :roomId="roomId"
        class="hidden-player"
        @participants-update="updateParticipantsList"
        @update-tracks="updateTracksList"
        @player-state="updatePlayerState"
      />
    </div>
    
    <!-- Мобильный плеер (показывается внизу при подключении) -->
    <PlayerMobile
      v-if="connected"
      class="mobile-only"
      :title="currentTrack?.title || 'Выберите трек'"
      :artist="currentTrack?.artist || ''"
      :coverUrl="currentTrack?.cover || ''"
      :currentTime="playerCurrentTime"
      :duration="playerDuration"
      :isPlaying="isPlayerPlaying"
      :roomName="currentRoomName"
      @play="handlePlayerPlay"
      @pause="handlePlayerPause"
      @prev="handlePlayerPrev"
      @next="handlePlayerNext"
      @seek="handlePlayerSeek"
      @show-queue="showMobileQueue"
    />
    
    <!-- Десктопный плеер (внизу экрана) -->
    <PlayerDesktop
      v-if="connected"
      class="desktop-only"
      :title="currentTrack?.title || 'Выберите трек'"
      :artist="currentTrack?.artist || ''"
      :coverUrl="currentTrack?.cover || ''"
      :currentTime="playerCurrentTime"
      :duration="playerDuration"
      :volume="playerVolume"
      :isPlaying="isPlayerPlaying"
      :isLoading="isPlayerLoading"
      @play="handlePlayerPlay"
      @pause="handlePlayerPause"
      @prev="handlePlayerPrev"
      @next="handlePlayerNext"
      @seek="handlePlayerSeek"
      @volume-change="handleVolumeChange"
      @toggle-queue="toggleQueueSidebar"
    />

    <!-- Кнопка выхода из комнаты (только на десктопе) -->
    <button v-if="connected" class="leave-room-btn desktop-only" @click="leaveRoom">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
        <path d="M10.09 15.59L11.5 17l5-5-5-5-1.41 1.41L12.67 11H3v2h9.67l-2.58 2.59zM19 3H5c-1.11 0-2 .9-2 2v4h2V5h14v14H5v-4H3v4c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2z"/>
      </svg>
      <span>Выйти из комнаты</span>
    </button>
    
    <!-- Overlay для sidebar на мобильных -->
    <div 
      v-if="connected && sidebarOpen" 
      class="sidebar-overlay" 
      @click="sidebarOpen = false"
    ></div>
    
    <!-- Overlay для закрытия меню -->
    <div v-if="showAccountMenu" class="menu-overlay" @click="showAccountMenu = false"></div>
  </div>
</template>

<script>
import AudioPlayer from '@/components/PlayerRefactored.vue';
import PlayerMobile from '@/components/PlayerMobile.vue';
import PlayerDesktop from '@/components/PlayerDesktop.vue';
import TrackQueue from '@/components/Track_queue.vue';
import SendTrack from '@/components/Send-search_Track.vue';
import Logo from '@/assets/logo.vue';
import { getCookie, logout } from '@/utils/cookies.js';
import { roomsApi } from '@/utils/api.js';

export default {
  name: 'MainView',
  
  components: {
    AudioPlayer,
    PlayerMobile,
    PlayerDesktop,
    TrackQueue,
    SendTrack,
    Logo
  },
  
  data() {
    return {
      tracks: [],
      currentTrackIndex: 0,
      participants: [],
      userId: getCookie('user_id'),
      userName: getCookie('username') || 'Пользователь',
      roomId: null,
      currentRoomName: '',
      connected: false,
      sidebarOpen: true,
      rooms: [],
      selectedRoom: null,
      showCreateRoom: false,
      newRoomName: '',
      roomIdInput: '',
      showFriends: false,
      showAccountMenu: false,
      showRoomsDropdown: false,
      showCreateRoomModal: false,
      loadingRooms: false,
      draggedRoom: null,
      // Player state
      playerCurrentTime: 0,
      playerDuration: 0,
      playerVolume: 1,
      isPlayerPlaying: false,
      isPlayerLoading: false,
      isQueueLoading: false,
      showQueueSidebar: false,
    };
  },
  
  computed: {
    currentTrack() {
      return this.tracks[this.currentTrackIndex] || null;
    }
  },

  mounted() {
    if (!this.userId) {
      this.$router.push('/login');
      return;
    }
    this.loadRooms();
    
    // Закрытие меню при клике вне
    document.addEventListener('click', this.closeMenuOnOutsideClick);
  },
  
  beforeUnmount() {
    document.removeEventListener('click', this.closeMenuOnOutsideClick);
  },
  
  watch: {
    showCreateRoom(val) {
      if (val) {
        this.$nextTick(() => {
          this.$refs.newRoomInput?.focus();
        });
      }
    }
  },
  
  methods: {
    closeMenuOnOutsideClick(e) {
      if (this.showAccountMenu && !e.target.closest('.account-menu-wrapper')) {
        this.showAccountMenu = false;
      }
      if (this.showRoomsDropdown && !e.target.closest('.rooms-menu-btn') && !e.target.closest('.rooms-dropdown')) {
        this.showRoomsDropdown = false;
      }
    },
    
    async loadRooms() {
      this.loadingRooms = true;
      try {
        const response = await roomsApi.getUserRooms(this.userId);
        this.rooms = response.rooms || [];
      } catch (error) {
        console.error('Error loading rooms:', error);
        this.rooms = [];
      } finally {
        this.loadingRooms = false;
      }
    },
    
    selectRoom(room) {
      this.selectedRoom = room.id;
    },
    
    joinRoom(roomId) {
      this.roomId = roomId;
      const room = this.rooms.find(r => r.id === roomId);
      this.currentRoomName = room ? room.name : `Room ${roomId}`;
      this.connected = true;
      this.showRoomsDropdown = false;
      // Показать загрузку очереди
      this.isQueueLoading = true;
      setTimeout(() => {
        this.isQueueLoading = false;
      }, 1500);
    },
    
    switchRoom(room) {
      if (room.id === this.roomId) {
        this.showRoomsDropdown = false;
        return;
      }
      // Сначала выходим из текущей комнаты
      this.leaveRoom();
      // Затем входим в новую
      this.$nextTick(() => {
        this.joinRoom(room.id);
      });
    },
    
    quickJoin() {
      const id = this.roomIdInput.trim();
      if (id) {
        this.roomId = id;
        this.currentRoomName = `Room ${id}`;
        this.connected = true;
        this.roomIdInput = '';
      }
    },
    
    async createRoom() {
      const name = this.newRoomName.trim();
      if (!name) return;
      
      try {
        const result = await roomsApi.createRoom(name);
        if (Array.isArray(result) && result.length > 0) {
          const newRoom = result[result.length - 1];
          this.rooms.push({ id: newRoom.id, name: name, participants_count: 1 });
          this.newRoomName = '';
          this.showCreateRoom = false;
          this.joinRoom(newRoom.id);
        }
      } catch (error) {
        console.error('Error creating room:', error);
      }
    },
    
    updateParticipantsList(participantsArray) {
      this.participants = participantsArray;
    },
    
    leaveRoom() {
      this.sidebarOpen = false; // Закрываем sidebar сначала
      this.connected = false;
      this.roomId = null;
      this.currentRoomName = '';
      this.tracks = [];
      this.participants = [];
      this.currentTrackIndex = 0;
    },
    
    handleLogout() {
      this.showAccountMenu = false;
      logout();
      this.$router.push('/login');
    },
    
    updateTracksList(tracksArray, currentIndex) {
      this.tracks = tracksArray;
      this.currentTrackIndex = currentIndex;
    },
    
    handleSendTrack(url) {
      if (url && this.$refs.audioPlayer) {
        this.$refs.audioPlayer.playTrack(url);
      }
    },
    
    onTracksReorder(newTracks, oldIndex, newIndex) {
      // Пересчитываем currentTrackIndex после перетаскивания
      let updatedIndex = this.currentTrackIndex;
      
      // Если перетащили текущий трек
      if (oldIndex === this.currentTrackIndex) {
        updatedIndex = newIndex;
      } 
      // Если перетащили трек через текущий
      else if (oldIndex < this.currentTrackIndex && newIndex >= this.currentTrackIndex) {
        updatedIndex = this.currentTrackIndex - 1;
      } else if (oldIndex > this.currentTrackIndex && newIndex <= this.currentTrackIndex) {
        updatedIndex = this.currentTrackIndex + 1;
      }
      
      this.tracks = newTracks;
      this.currentTrackIndex = updatedIndex;
      
      // Отправляем на сервер
      if (this.$refs.audioPlayer) {
        this.$refs.audioPlayer.sendReorderTracks(newTracks, updatedIndex);
      }
    },
    
    onPlayTrack(index) {
      if (this.$refs.audioPlayer) {
        // Если кликнули на текущий трек - toggle play/pause
        if (index === this.currentTrackIndex) {
          if (this.isPlaying) {
            this.$refs.audioPlayer.sendPauseCommand();
          } else {
            this.$refs.audioPlayer.sendPlayCommand();
          }
        } else {
          this.$refs.audioPlayer.playTrackByIndex(index);
        }
      }
    },
    
    // Методы управления плеерами
    handlePlayerPlay() {
      if (this.$refs.audioPlayer) {
        this.$refs.audioPlayer.sendPlayCommand();
      }
    },
    
    handlePlayerPause() {
      if (this.$refs.audioPlayer) {
        this.$refs.audioPlayer.sendPauseCommand();
      }
    },
    
    handlePlayerPrev() {
      if (this.$refs.audioPlayer) {
        this.$refs.audioPlayer.prevTrack();
      }
    },
    
    handlePlayerNext() {
      if (this.$refs.audioPlayer) {
        this.$refs.audioPlayer.nextTrack();
      }
    },
    
    handlePlayerSeek(time) {
      if (this.$refs.audioPlayer) {
        this.$refs.audioPlayer.seekTo(time);
      }
    },
    
    handleVolumeChange(volume) {
      this.playerVolume = volume;
      if (this.$refs.audioPlayer) {
        this.$refs.audioPlayer.setVolume(volume);
      }
    },
    
    toggleQueueSidebar(show) {
      this.showQueueSidebar = show;
    },
    
    showMobileQueue() {
      // Закрытие full player в PlayerMobile происходит автоматически
      // Очередь треков уже видна на главном экране
    },
    
    // Обновление состояния плеера из AudioPlayer
    updatePlayerState(state) {
      this.playerCurrentTime = state.currentTime || 0;
      this.playerDuration = state.duration || 0;
      this.isPlayerPlaying = state.isPlaying || false;
      this.isPlayerLoading = state.isLoading || false;
    },
    
    // Drag and drop для комнат
    onRoomDragStart(event, room) {
      this.draggedRoom = room;
      event.dataTransfer.effectAllowed = 'move';
    },
    
    onRoomDrop(event, targetRoom) {
      if (!this.draggedRoom || this.draggedRoom.id === targetRoom.id) return;
      
      const oldIndex = this.rooms.findIndex(r => r.id === this.draggedRoom.id);
      const newIndex = this.rooms.findIndex(r => r.id === targetRoom.id);
      
      if (oldIndex !== -1 && newIndex !== -1) {
        const [removed] = this.rooms.splice(oldIndex, 1);
        this.rooms.splice(newIndex, 0, removed);
      }
      
      this.draggedRoom = null;
    },
    
    // Удаление трека из очереди
    async onDeleteTrack(index) {
      if (index < 0 || index >= this.tracks.length) return;
      
      // Создаём новый список без удалённого трека
      const newTracks = [...this.tracks];
      newTracks.splice(index, 1);
      
      // Корректируем currentTrackIndex
      let newCurrentIndex = this.currentTrackIndex;
      if (index < this.currentTrackIndex) {
        newCurrentIndex = this.currentTrackIndex - 1;
      } else if (index === this.currentTrackIndex) {
        // Если удаляем текущий трек, переключаемся на следующий (или предыдущий если в конце)
        if (newCurrentIndex >= newTracks.length) {
          newCurrentIndex = Math.max(0, newTracks.length - 1);
        }
      }
      
      // Обновляем локальное состояние
      this.tracks = newTracks;
      this.currentTrackIndex = newCurrentIndex;
      
      // Отправляем обновление на бекенд
      if (this.$refs.audioPlayer) {
        this.$refs.audioPlayer.sendReorderTracks(newTracks, newCurrentIndex);
      }
    }
  }
};
</script>

<style scoped>
.main-wrapper {
  display: flex;
  flex-direction: column;
  height: 100vh;
  height: 100dvh;
  overflow: hidden;
  background: linear-gradient(135deg, #1a1025 0%, #0d1a24 50%, #1a0f28 100%);
}

/* Header */
.main-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background: rgba(23, 18, 34, 0.8);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(0, 217, 231, 0.2);
  flex-shrink: 0;
  z-index: 100;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.sidebar-toggle {
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  transition: all 0.2s;
}

.sidebar-toggle:hover {
  background: rgba(208, 188, 255, 0.1);
  color: white;
}

/* Rooms Menu Button */
.rooms-menu-btn {
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  transition: all 0.2s;
  position: relative;
}

.rooms-menu-btn:hover {
  background: rgba(208, 188, 255, 0.1);
  color: white;
}

/* Rooms Dropdown */
.rooms-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  margin-top: 8px;
  min-width: 220px;
  max-width: 300px;
  background: rgba(25, 20, 40, 0.98);
  border: 1px solid rgba(208, 188, 255, 0.2);
  border-radius: 12px;
  overflow: hidden;
  z-index: 1000;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
}

.rooms-dropdown-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 14px;
  border-bottom: 1px solid rgba(208, 188, 255, 0.1);
  color: rgba(255, 255, 255, 0.7);
  font-size: 12px;
  font-weight: 500;
}

.add-room-small-btn {
  background: rgba(0, 217, 231, 0.2);
  border: none;
  color: #00d9e7;
  padding: 4px;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.add-room-small-btn:hover {
  background: rgba(0, 217, 231, 0.3);
}

.rooms-dropdown-list {
  list-style: none;
  margin: 0;
  padding: 8px;
  max-height: 300px;
  overflow-y: auto;
}

.rooms-dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  color: white;
  font-size: 13px;
}

.rooms-dropdown-item:hover {
  background: rgba(208, 188, 255, 0.1);
}

.rooms-dropdown-item.current {
  background: rgba(0, 217, 231, 0.1);
  border: 1px solid rgba(0, 217, 231, 0.2);
}

.room-avatar-small {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 11px;
  flex-shrink: 0;
}

.current-badge {
  margin-left: auto;
  font-size: 10px;
  color: #00d9e7;
  background: rgba(0, 217, 231, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
}

.empty-dropdown-item {
  color: rgba(255, 255, 255, 0.4);
  font-size: 12px;
  padding: 16px;
  text-align: center;
}

/* Mobile only button */
.mobile-only {
  display: none;
}

/* Desktop only */
.desktop-only {
  display: block;
}

/* Hidden player (controls playback but not visible) */
.hidden-player {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  opacity: 0;
  pointer-events: none;
}

/* Sidebar leave section */
.sidebar-leave-section {
  margin-top: auto;
  padding-top: 12px;
  border-top: 1px solid rgba(208, 188, 255, 0.1);
}

.sidebar-leave-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 12px 14px;
  background: rgba(255, 100, 100, 0.1);
  border: 1px solid rgba(255, 100, 100, 0.2);
  border-radius: 10px;
  color: #ff8a8a;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.sidebar-leave-btn:hover {
  background: rgba(255, 100, 100, 0.2);
  border-color: rgba(255, 100, 100, 0.4);
}

.header-logo-full {
  height: 28px;
  width: auto;
}

.header-logo-full :deep(svg) {
  height: 28px;
  width: auto;
}

.header-center {
  flex: 1;
  display: flex;
  justify-content: center;
}

.room-title {
  font-size: 16px;
  font-weight: 500;
  color: white;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.icon-btn {
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  padding: 8px;
  border-radius: 50%;
  transition: all 0.2s;
}

.icon-btn:hover {
  background: rgba(208, 188, 255, 0.1);
  color: white;
}

/* Account Menu */
.account-menu-wrapper {
  position: relative;
}

.account-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 8px;
  min-width: 180px;
  background: rgba(30, 25, 45, 0.98);
  border: 1px solid rgba(208, 188, 255, 0.2);
  border-radius: 12px;
  overflow: hidden;
  z-index: 1000;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  color: white;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
  width: 100%;
  border: none;
  background: transparent;
  text-align: left;
}

.dropdown-item:hover {
  background: rgba(208, 188, 255, 0.1);
}

.user-info {
  border-bottom: 1px solid rgba(208, 188, 255, 0.1);
  cursor: default;
}

.user-info:hover {
  background: transparent;
}

.user-name {
  font-weight: 500;
}

.logout-btn {
  color: #ff8a8a;
}

.logout-btn:hover {
  background: rgba(255, 100, 100, 0.1);
}

.menu-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 99;
}

/* Sidebar overlay для мобильных */
.sidebar-overlay {
  display: none;
}

@media (max-width: 768px) {
  .sidebar-overlay {
    display: block;
    position: fixed;
    top: 56px;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(4px);
    -webkit-backdrop-filter: blur(4px);
    z-index: 140;
    animation: fadeIn 0.2s ease;
  }
  
  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }
}

/* Main Content */
.main-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

/* Sidebar */
.sidebar {
  width: 280px;
  min-width: 280px;
  background: rgba(23, 18, 34, 0.6);
  border-right: 1px solid rgba(208, 188, 255, 0.1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: transform 0.3s ease, width 0.3s ease;
  height: 100%;
}

.sidebar-section {
  padding: 12px;
  flex-shrink: 0;
}

.sidebar-section.friends-list-section {
  flex: 1;
  overflow-y: auto;
  min-height: 0;
}

.sidebar-leave-section {
  margin-top: auto;
  padding: 16px;
  border-top: 1px solid rgba(208, 188, 255, 0.1);
  flex-shrink: 0;
  background: rgba(15, 12, 25, 0.5);
}

.sidebar-leave-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 16px;
  background: rgba(255, 100, 100, 0.1);
  border: 1px solid rgba(255, 100, 100, 0.3);
  border-radius: 12px;
  color: #ff8a8a;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.sidebar-leave-btn:hover {
  background: rgba(255, 100, 100, 0.2);
  border-color: rgba(255, 100, 100, 0.5);
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  background: rgba(208, 188, 255, 0.1);
  border-radius: 10px;
  margin-bottom: 10px;
  color: white;
  font-weight: 500;
  font-size: 14px;
}

.sidebar-header.clickable {
  cursor: pointer;
  transition: background 0.2s;
}

.sidebar-header.clickable:hover {
  background: rgba(208, 188, 255, 0.2);
}

.chevron {
  margin-left: auto;
  transition: transform 0.2s;
}

.chevron.expanded {
  transform: rotate(180deg);
}

.rooms-section .sidebar-header {
  justify-content: space-between;
}

.add-room-btn {
  background: rgba(0, 217, 231, 0.2);
  border: none;
  color: #00d9e7;
  cursor: pointer;
  padding: 4px;
  border-radius: 6px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.add-room-btn:hover {
  background: rgba(0, 217, 231, 0.3);
}

.sidebar-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
  overflow-y: auto;
  max-height: calc(100vh - 280px);
}

.sidebar-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  background: rgba(208, 188, 255, 0.05);
}

.sidebar-item:hover {
  background: rgba(208, 188, 255, 0.15);
}

.sidebar-item.selected {
  background: rgba(208, 188, 255, 0.2);
  border: 1px solid rgba(208, 188, 255, 0.3);
}

.drag-handle {
  cursor: grab;
  color: rgba(255, 255, 255, 0.3);
  padding: 2px;
}

.drag-handle:hover {
  color: rgba(255, 255, 255, 0.6);
}

.item-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #D0BCFF 0%, #2EA48C 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 13px;
  color: #1F1431;
  flex-shrink: 0;
}

.item-avatar.you {
  border: 2px solid #00d9e7;
  box-shadow: 0 0 8px rgba(0, 217, 231, 0.4);
}

.you-badge {
  font-size: 10px;
  color: #00d9e7;
  background: rgba(0, 217, 231, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  margin-left: auto;
}

.room-avatar {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
}

.item-name {
  color: white;
  font-size: 13px;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.room-meta {
  display: flex;
  align-items: center;
}

.participants-count {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  background: rgba(255, 255, 255, 0.1);
  padding: 2px 6px;
  border-radius: 10px;
}

.join-btn {
  background: linear-gradient(135deg, #00d9e7 0%, #8b5cf6 100%);
  border: none;
  color: white;
  font-size: 11px;
  padding: 4px 10px;
  border-radius: 6px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.join-btn:hover {
  opacity: 0.9;
}

.empty-item {
  color: rgba(255, 255, 255, 0.4);
  font-size: 12px;
  padding: 12px;
  text-align: center;
}

.loading-rooms {
  color: rgba(255, 255, 255, 0.5);
  font-size: 13px;
  padding: 20px;
  text-align: center;
}

/* Create Room Form */
.create-room-form {
  margin-top: 12px;
  padding: 12px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 10px;
}

.create-room-input {
  width: 100%;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(208, 188, 255, 0.2);
  border-radius: 8px;
  color: white;
  font-size: 13px;
  outline: none;
  margin-bottom: 10px;
  box-sizing: border-box;
}

.create-room-input:focus {
  border-color: rgba(208, 188, 255, 0.5);
}

.create-room-input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.create-room-buttons {
  display: flex;
  gap: 8px;
}

.btn-cancel, .btn-create {
  flex: 1;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.7);
}

.btn-cancel:hover {
  background: rgba(255, 255, 255, 0.1);
}

.btn-create {
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border: none;
  color: white;
}

.btn-create:hover:not(:disabled) {
  opacity: 0.9;
}

.btn-create:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Quick Join */
.quick-join {
  margin-top: 12px;
  display: flex;
  gap: 8px;
}

.quick-join-input {
  flex: 1;
  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(208, 188, 255, 0.2);
  border-radius: 8px;
  color: white;
  font-size: 12px;
  outline: none;
  min-width: 0;
}

.quick-join-input:focus {
  border-color: rgba(208, 188, 255, 0.5);
}

.quick-join-input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.quick-join-btn {
  padding: 10px 14px;
  background: rgba(0, 217, 231, 0.2);
  border: 1px solid rgba(0, 217, 231, 0.3);
  border-radius: 8px;
  color: #00d9e7;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.quick-join-btn:hover:not(:disabled) {
  background: rgba(0, 217, 231, 0.3);
}

.quick-join-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Rooms View */
.rooms-view {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.rooms-sidebar {
  width: 260px;
  min-width: 260px;
  background: rgba(23, 18, 34, 0.6);
  border-right: 1px solid rgba(208, 188, 255, 0.1);
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  padding: 12px;
}

.rooms-main-area {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid rgba(0, 217, 231, 0.3);
  margin: 16px;
  border-radius: 20px;
  background: rgba(0, 0, 0, 0.2);
}

.welcome-message {
  text-align: center;
  color: rgba(255, 255, 255, 0.6);
  padding: 40px;
}

.welcome-logo {
  width: 320px;
  height: auto;
  margin: 0 auto 32px auto;
  display: block;
}

.welcome-logo :deep(svg) {
  width: 320px;
  height: auto;
}

@media (max-width: 768px) {
  .welcome-logo {
    width: 200px;
  }
  
  .welcome-logo :deep(svg) {
    width: 200px;
  }
}

.welcome-message h2 {
  font-size: 24px;
  color: white;
  margin: 0 0 12px 0;
}

.welcome-message p {
  font-size: 16px;
  margin: 0;
}

/* Room View */
.room-view {
  flex: 1;
  display: flex;
  gap: 16px;
  padding: 16px;
  padding-bottom: 100px; /* Место для десктопного плеера */
  overflow: hidden;
}

.center-column {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  gap: 12px;
  min-width: 0;
}

.track-queue-wrapper {
  flex: 1;
  overflow: hidden;
  min-height: 0;
}

.send-track-wrapper {
  flex-shrink: 0;
}

/* Leave Button (desktop only) */
.leave-room-btn {
  position: fixed;
  bottom: 100px; /* Above desktop player */
  left: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: rgba(255, 100, 100, 0.1);
  border: 1px solid rgba(255, 100, 100, 0.3);
  border-radius: 20px;
  color: #ff8a8a;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  z-index: 100;
}

.leave-room-btn:hover {
  background: rgba(255, 100, 100, 0.2);
  border-color: rgba(255, 100, 100, 0.5);
}

/* Responsive */
@media (max-width: 1100px) {
  .center-column {
    min-height: 200px;
  }
}

@media (max-width: 768px) {
  .main-header {
    padding: 10px 12px;
  }
  
  .header-logo-full {
    height: 24px;
  }
  
  .header-logo-full :deep(svg) {
    height: 24px;
  }
  
  /* Desktop rooms menu скрываем на мобильных */
  .rooms-menu-btn,
  .rooms-dropdown {
    display: none !important;
  }
  
  /* Показываем мобильную кнопку комнат */
  .mobile-only {
    display: flex !important;
  }
  
  /* Скрываем десктопные элементы */
  .desktop-only {
    display: none !important;
  }
  
  /* Мобильный sidebar с overlay */
  .sidebar {
    position: fixed;
    left: 0;
    top: 56px;
    bottom: 0;
    z-index: 1100; /* Above mobile player (z-index: 1000) */
    transform: translateX(-100%);
    width: 280px;
    background: rgba(15, 12, 25, 0.98);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    box-shadow: 4px 0 30px rgba(0, 0, 0, 0.5);
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    display: flex;
    flex-direction: column;
  }
  
  .sidebar.sidebar-open {
    transform: translateX(0);
  }
  
  .sidebar-leave-section {
    padding: 16px;
    padding-bottom: calc(80px + env(safe-area-inset-bottom, 16px)); /* Extra padding for player space */
    background: rgba(15, 12, 25, 0.9);
  }
  
  .sidebar-leave-btn {
    font-size: 15px;
    padding: 14px 20px;
  }
  
  .rooms-view {
    flex-direction: column;
  }
  
  .rooms-sidebar {
    width: 100%;
    min-width: 0;
    max-height: none;
    flex: 1;
    border-right: none;
    border-bottom: none;
    padding: 16px;
  }
  
  .rooms-main-area {
    display: none;
  }
  
  .room-view {
    padding: 10px;
    gap: 10px;
    padding-bottom: 80px; /* Место для мобильного плеера */
  }
  
  /* Кнопка выхода скрыта на мобильных - она в sidebar */
  .leave-room-btn {
    display: none !important;
  }
}

@media (max-width: 480px) {
  .header-left {
    gap: 8px;
  }
  
  .header-logo-full {
    height: 20px;
  }
  
  .header-logo-full :deep(svg) {
    height: 20px;
  }
  
  .room-view {
    padding: 8px;
    padding-bottom: 80px;
  }
}
</style>

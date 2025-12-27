<template>
  <div class="mobile-player-wrapper">
    <!-- Mobile Bottom Player (Spotify-style) -->
    <div class="mobile-player" @click="openFullPlayer">
      <!-- Mini Progress -->
      <div class="mini-progress">
        <div class="mini-progress-fill" :style="{ width: progressPercent + '%' }"></div>
      </div>
      
      <!-- Main Content -->
      <div class="mobile-player-content">
        <!-- Cover & Info -->
        <div class="mobile-left">
          <div class="mobile-cover" ref="cover">
            <img 
              v-if="coverUrl" 
              :src="coverUrl" 
              alt="Cover" 
              class="cover-img"
            />
            <div v-else class="cover-placeholder">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z"/>
              </svg>
            </div>
          </div>
          
          <div class="mobile-info">
            <div class="mobile-title">{{ title }}</div>
            <div class="mobile-artist">{{ artist }}</div>
          </div>
        </div>
        
        <!-- Controls -->
        <div class="mobile-controls">
          <button class="mobile-btn like-btn" @click.stop="toggleLike">
            <svg width="22" height="22" viewBox="0 0 24 24" :fill="isLiked ? '#D0BCFF' : 'none'" :stroke="isLiked ? '#D0BCFF' : 'currentColor'" stroke-width="2">
              <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
            </svg>
          </button>
          
          <button class="mobile-btn play-btn" @click.stop="togglePlay">
            <svg v-if="!isPlaying" width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
              <path d="M8 5v14l11-7z"/>
            </svg>
            <svg v-else width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
              <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
    
    <!-- Full Screen Player Modal -->
    <Teleport to="body">
      <Transition name="slide-up">
        <div v-if="showFullPlayer" class="full-player-overlay" @click.self="closeFullPlayer">
          <div class="full-player">
            <!-- Header -->
            <div class="full-player-header">
              <button class="header-btn" @click="closeFullPlayer">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                <path d="M7 10l5 5 5-5z"/>
              </svg>
            </button>
            <div class="header-title">
              <span class="playing-from">PLAYING FROM</span>
              <span class="playlist-name">{{ roomName }}</span>
            </div>
            <!-- Placeholder для симметрии -->
            <div class="header-btn-placeholder"></div>
          </div>
          
          <!-- Cover -->
          <div class="full-cover-wrapper">
            <Transition name="cover-fade" mode="out-in">
              <div class="full-cover" :class="{ 'playing': isPlaying }" :key="coverUrl">
                <img 
                  v-if="coverUrl" 
                  :src="highResCoverUrl" 
                  alt="Cover"
                />
                <div v-else class="cover-placeholder-large">
                  <svg width="80" height="80" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z"/>
                  </svg>
                </div>
              </div>
            </Transition>
          </div>
          
          <!-- Info -->
          <div class="full-info">
            <Transition name="info-slide" mode="out-in">
              <div class="full-info-left" :key="title">
                <h2 class="full-title">{{ title }}</h2>
                <p class="full-artist">{{ artist }}</p>
              </div>
            </Transition>
            <button class="like-btn-full" @click="toggleLike">
              <svg width="24" height="24" viewBox="0 0 24 24" :fill="isLiked ? '#bf5af2' : 'none'" :stroke="isLiked ? '#bf5af2' : 'currentColor'" stroke-width="2">
                <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
              </svg>
            </button>
          </div>
          
          <!-- Progress Bar -->
          <div class="full-progress">
            <div 
              class="progress-track"
              ref="progressTrack"
              @mousedown="startProgressDrag"
              @touchstart.prevent="startProgressDrag"
            >
              <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
              <div class="progress-thumb" :style="{ left: progressPercent + '%' }"></div>
            </div>
            <div class="progress-times">
              <span>{{ formatTime(currentTime) }}</span>
              <span>{{ formatTime(duration) }}</span>
            </div>
          </div>
          
          <!-- Main Controls -->
          <div class="full-controls">
            <button class="control-btn prev-btn" @click="prevTrack">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="currentColor">
                <path d="M6 6h2v12H6zm3.5 6l8.5 6V6z"/>
              </svg>
            </button>
            
            <button class="control-btn play-btn-main" @click="togglePlay">
              <svg v-if="!isPlaying" width="28" height="28" viewBox="0 0 24 24" fill="currentColor">
                <path d="M8 5v14l11-7z"/>
              </svg>
              <svg v-else width="28" height="28" viewBox="0 0 24 24" fill="currentColor">
                <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>
              </svg>
            </button>
            
            <button class="control-btn next-btn" @click="nextTrack">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="currentColor">
                <path d="M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z"/>
              </svg>
            </button>
          </div>
          
          <!-- Bottom Actions -->
          <div class="full-bottom">
            <button class="bottom-btn queue-btn" @click="showQueue">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor">
                <path d="M15 6H3v2h12V6zm0 4H3v2h12v-2zM3 16h8v-2H3v2zM17 6v8.18c-.31-.11-.65-.18-1-.18-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3V8h3V6h-5z"/>
              </svg>
              <span>Очередь</span>
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
  </div>
</template>

<script>
export default {
  name: 'PlayerMobile',
  
  props: {
    title: { type: String, default: 'Название трека' },
    artist: { type: String, default: 'Исполнитель' },
    coverUrl: { type: String, default: '' },
    currentTime: { type: Number, default: 0 },
    duration: { type: Number, default: 0 },
    isPlaying: { type: Boolean, default: false },
    roomName: { type: String, default: 'Комната' },
  },
  
  emits: ['play', 'pause', 'prev', 'next', 'seek', 'show-queue'],
  
  data() {
    return {
      showFullPlayer: false,
      isLiked: false,
      isDragging: false,
      dragProgress: 0,
    };
  },
  
  computed: {
    progressPercent() {
      if (this.isDragging) return this.dragProgress;
      if (!this.duration) return 0;
      return (this.currentTime / this.duration) * 100;
    },
    
    /**
     * Обложка высокого разрешения для полноэкранного режима
     */
    highResCoverUrl() {
      if (!this.coverUrl) return '';
      // Yandex Music cover URLs содержат размер, например: 100x100, 200x200
      // Заменяем на 400x400 для высокого разрешения
      return this.coverUrl.replace(/\d+x\d+/, '400x400');
    }
  },
  
  methods: {
    formatTime(seconds) {
      if (!seconds || !isFinite(seconds)) return '0:00';
      const mins = Math.floor(seconds / 60);
      const secs = Math.floor(seconds % 60);
      return `${mins}:${secs.toString().padStart(2, '0')}`;
    },
    
    togglePlay() {
      if (this.isPlaying) {
        this.$emit('pause');
      } else {
        this.$emit('play');
      }
    },
    
    prevTrack() {
      this.$emit('prev');
    },
    
    nextTrack() {
      this.$emit('next');
    },
    
    toggleLike() {
      this.isLiked = !this.isLiked;
    },
    
    openFullPlayer() {
      this.showFullPlayer = true;
      document.body.style.overflow = 'hidden';
    },
    
    closeFullPlayer() {
      this.showFullPlayer = false;
      document.body.style.overflow = '';
    },
    
    showQueue() {
      this.closeFullPlayer();
      this.$emit('show-queue');
    },
    
    // Progress drag
    startProgressDrag(e) {
      this.isDragging = true;
      this.updateDragProgress(e);
      
      document.addEventListener('mousemove', this.handleProgressDrag);
      document.addEventListener('mouseup', this.stopProgressDrag);
      document.addEventListener('touchmove', this.handleProgressDrag);
      document.addEventListener('touchend', this.stopProgressDrag);
    },
    
    handleProgressDrag(e) {
      if (!this.isDragging) return;
      this.updateDragProgress(e);
    },
    
    updateDragProgress(e) {
      const track = this.$refs.progressTrack;
      if (!track) return;
      
      const rect = track.getBoundingClientRect();
      const clientX = e.touches ? e.touches[0].clientX : e.clientX;
      const x = Math.max(0, Math.min(clientX - rect.left, rect.width));
      this.dragProgress = (x / rect.width) * 100;
    },
    
    stopProgressDrag() {
      if (!this.isDragging) return;
      
      const newTime = (this.dragProgress / 100) * this.duration;
      this.$emit('seek', newTime);
      
      this.isDragging = false;
      document.removeEventListener('mousemove', this.handleProgressDrag);
      document.removeEventListener('mouseup', this.stopProgressDrag);
      document.removeEventListener('touchmove', this.handleProgressDrag);
      document.removeEventListener('touchend', this.stopProgressDrag);
    }
  },
  
  beforeUnmount() {
    this.stopProgressDrag();
    document.body.style.overflow = '';
  }
};
</script>

<style scoped>
/* ============ MINI PLAYER ============ */
.mobile-player {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(180deg, rgba(25, 20, 40, 0.98) 0%, rgba(15, 12, 25, 0.99) 100%);
  backdrop-filter: blur(30px);
  -webkit-backdrop-filter: blur(30px);
  z-index: 1000;
  cursor: pointer;
  user-select: none;
}

.mini-progress {
  height: 2px;
  background: rgba(255, 255, 255, 0.1);
}

.mini-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #00d9e7, #633A89);
  transition: width 0.25s linear;
}

.mobile-player-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px 12px;
  gap: 12px;
}

.mobile-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.mobile-cover {
  width: 48px;
  height: 48px;
  border-radius: 6px;
  overflow: hidden;
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.05);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.mobile-cover .cover-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.3);
}

.mobile-info {
  flex: 1;
  min-width: 0;
}

.mobile-title {
  font-size: 14px;
  font-weight: 600;
  color: white;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.mobile-artist {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-top: 2px;
}

.mobile-controls {
  display: flex;
  align-items: center;
  gap: 4px;
}

.mobile-btn {
  background: transparent;
  border: none;
  color: white;
  padding: 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.15s, opacity 0.15s;
}

.mobile-btn:active {
  transform: scale(0.9);
  opacity: 0.7;
}

.like-btn {
  color: rgba(255, 255, 255, 0.6);
}

.play-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #633A89;
  color: white;
}

/* ============ FULL PLAYER ============ */
.full-player-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 2000;
  background: linear-gradient(180deg, #1a1030 0%, #0d0815 30%, #050208 100%);
}

.full-player {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 16px 24px;
  box-sizing: border-box;
  padding-top: env(safe-area-inset-top, 16px);
  padding-bottom: calc(env(safe-area-inset-bottom, 16px) + 16px);
}

.full-player-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 0;
  flex-shrink: 0;
}

.header-btn {
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.7);
  padding: 8px;
  cursor: pointer;
  transition: color 0.2s;
}

.header-btn:hover {
  color: white;
}

.header-btn-placeholder {
  width: 40px;
  height: 40px;
}

.header-title {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.playing-from {
  font-size: 10px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.5);
  letter-spacing: 1px;
}

.playlist-name {
  font-size: 12px;
  font-weight: 600;
  color: white;
}

/* Cover */
.full-cover-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px 0;
  min-height: 0;
}

.full-cover {
  width: 100%;
  max-width: 340px;
  aspect-ratio: 1/1;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 
    0 20px 60px rgba(0, 0, 0, 0.5),
    0 0 0 rgba(99, 58, 137, 0);
  transition: box-shadow 0.8s ease;
}

.full-cover.playing {
  box-shadow: 
    0 20px 80px rgba(99, 58, 137, 0.35),
    0 0 50px rgba(191, 90, 242, 0.2);
}

/* Pulse animation only when loading */
.full-cover.loading {
  animation: pulse-glow-loading 1.5s ease-in-out infinite;
}

@keyframes pulse-glow-loading {
  0%, 100% { 
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  }
  50% { 
    box-shadow: 
      0 20px 80px rgba(99, 58, 137, 0.5),
      0 0 60px rgba(191, 90, 242, 0.3);
  }
}

.full-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-placeholder-large {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #3a2e5a 0%, #1a1030 100%);
  color: rgba(255, 255, 255, 0.2);
}

/* Info */
.full-info {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding: 16px 0;
  flex-shrink: 0;
}

.full-info-left {
  flex: 1;
  min-width: 0;
}

.full-title {
  font-size: 22px;
  font-weight: 700;
  background: linear-gradient(90deg, #D0BCFF, #00d9e7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.full-artist {
  font-size: 15px;
  color: rgba(255, 255, 255, 0.6);
  margin: 4px 0 0 0;
}

.like-btn-full {
  background: transparent;
  border: none;
  padding: 8px;
  cursor: pointer;
  color: rgba(255, 255, 255, 0.6);
  flex-shrink: 0;
  transition: color 0.2s, transform 0.2s;
}

.like-btn-full:hover {
  color: #ff6b9d;
  transform: scale(1.1);
}

/* Progress */
.full-progress {
  flex-shrink: 0;
  padding: 8px 0;
}

.progress-track {
  position: relative;
  height: 4px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
  cursor: pointer;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #00d9e7, #633A89);
  border-radius: 2px;
  position: relative;
  transition: none;
}

.progress-thumb {
  position: absolute;
  top: 50%;
  width: 16px;
  height: 16px;
  background: #D0BCFF;
  border-radius: 50%;
  transform: translate(-50%, -50%);
  opacity: 1;
  box-shadow: 0 0 12px rgba(208, 188, 255, 0.6);
}

.progress-track:hover .progress-thumb,
.progress-track:active .progress-thumb {
  opacity: 1;
  transform: translate(-50%, -50%) scale(1.1);
}

.progress-times {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  font-weight: 600;
  margin-top: 8px;
}

.progress-times span:first-child {
  color: #00ffff;
  text-shadow: 
    0 0 5px rgba(0, 255, 255, 0.8),
    0 0 10px rgba(0, 255, 255, 0.5);
}

.progress-times span:last-child {
  color: #bf5af2;
  text-shadow: 
    0 0 5px rgba(191, 90, 242, 0.8),
    0 0 10px rgba(191, 90, 242, 0.5);
}

/* Controls */
.full-controls {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 24px;
  padding: 16px 0;
  flex-shrink: 0;
}

.control-btn {
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.15s, opacity 0.15s, color 0.15s;
}

.control-btn:hover {
  color: #D0BCFF;
}

.control-btn:active {
  transform: scale(0.9);
}

.prev-btn,
.next-btn {
  padding: 12px;
  color: #633A89;
  width: 56px;
  height: 56px;
}

.prev-btn:hover,
.next-btn:hover {
  color: #bf5af2;
}

.play-btn-main {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: #633A89;
  color: white;
  box-shadow: 0 4px 20px rgba(99, 58, 137, 0.4);
}

.play-btn-main:hover {
  box-shadow: 0 6px 28px rgba(99, 58, 137, 0.6);
}

/* Bottom */
.full-bottom {
  display: flex;
  justify-content: center;
  padding: 16px 0;
  flex-shrink: 0;
}

.queue-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: white;
  padding: 12px 24px;
  border-radius: 24px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background 0.2s;
}

.queue-btn:hover {
  background: rgba(255, 255, 255, 0.15);
}

/* ============ ANIMATIONS ============ */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: transform 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(100%);
}

/* Cover fade animation */
.cover-fade-enter-active,
.cover-fade-leave-active {
  transition: all 0.3s ease;
}

.cover-fade-enter-from {
  opacity: 0;
  transform: scale(0.95);
}

.cover-fade-leave-to {
  opacity: 0;
  transform: scale(1.05);
}

/* Info slide animation */
.info-slide-enter-active,
.info-slide-leave-active {
  transition: all 0.25s ease;
}

.info-slide-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.info-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Safe area for devices with notch */
@supports (padding: max(0px)) {
  .full-player {
    padding-top: max(16px, env(safe-area-inset-top));
    padding-bottom: max(16px, env(safe-area-inset-bottom));
  }
}
</style>

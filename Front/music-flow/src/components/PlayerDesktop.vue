<template>
  <div class="desktop-player" :class="{ 'expanded': showQueue }">
    <!-- Preloader -->
    <transition name="fade">
      <div v-if="isLoading" class="player-preloader">
        <div class="loader-ring"></div>
      </div>
    </transition>

    <!-- Main Layout -->
    <div class="player-layout">
      <!-- Left Panel - Cover & Info -->
      <div class="player-left">
        <div class="cover-container">
          <div class="cover-wrapper" :class="{ 'is-playing': isPlaying }">
            <img 
              v-if="coverUrl" 
              :src="coverUrl" 
              alt="Cover"
              class="cover-image"
            />
            <div v-else class="cover-placeholder">
              <svg width="64" height="64" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z"/>
              </svg>
            </div>
          </div>
        </div>
        
        <div class="track-info">
          <h2 class="track-title">{{ title }}</h2>
          <p class="track-artist">{{ artist }}</p>
        </div>
      </div>

      <!-- Center Panel - Controls -->
      <div class="player-center">
        <!-- Main Controls -->
        <div class="main-controls">
          <button 
            class="control-btn shuffle-btn" 
            :class="{ active: isShuffle }"
            @click="toggleShuffle"
            title="Перемешать"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
              <path d="M10.59 9.17L5.41 4 4 5.41l5.17 5.17 1.42-1.41zM14.5 4l2.04 2.04L4 18.59 5.41 20 17.96 7.46 20 9.5V4h-5.5zm.33 9.41l-1.41 1.41 3.13 3.13L14.5 20H20v-5.5l-2.04 2.04-3.13-3.13z"/>
            </svg>
          </button>
          
          <button class="control-btn prev-btn" @click="prevTrack" title="Предыдущий">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="currentColor">
              <path d="M6 6h2v12H6zm3.5 6l8.5 6V6z"/>
            </svg>
          </button>
          
          <button class="control-btn play-btn" @click="togglePlay" :title="isPlaying ? 'Пауза' : 'Воспроизвести'">
            <svg v-if="!isPlaying" width="28" height="28" viewBox="0 0 24 24" fill="currentColor">
              <path d="M8 5v14l11-7z"/>
            </svg>
            <svg v-else width="28" height="28" viewBox="0 0 24 24" fill="currentColor">
              <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>
            </svg>
          </button>
          
          <button class="control-btn next-btn" @click="nextTrack" title="Следующий">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="currentColor">
              <path d="M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z"/>
            </svg>
          </button>
          
          <button 
            class="control-btn repeat-btn"
            :class="{ active: isRepeat }"
            @click="toggleRepeat"
            title="Повтор"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
              <path d="M7 7h10v3l4-4-4-4v3H5v6h2V7zm10 10H7v-3l-4 4 4 4v-3h12v-6h-2v4z"/>
            </svg>
          </button>
        </div>
        
        <!-- Progress Bar -->
        <div class="progress-container">
          <span class="time current-time">{{ formatTime(currentTime) }}</span>
          <div 
            class="progress-bar"
            ref="progressBar"
            @mousedown="startProgressDrag"
          >
            <div class="progress-track">
              <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
            </div>
            <div 
              class="progress-thumb"
              :style="{ left: progressPercent + '%' }"
            ></div>
          </div>
          <span class="time duration">{{ formatTime(duration) }}</span>
        </div>
      </div>

      <!-- Right Panel - Volume & Extra -->
      <div class="player-right">
        <button 
          class="extra-btn queue-btn" 
          :class="{ active: showQueue }"
          @click="toggleQueue"
          title="Очередь"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <path d="M15 6H3v2h12V6zm0 4H3v2h12v-2zM3 16h8v-2H3v2zM17 6v8.18c-.31-.11-.65-.18-1-.18-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3V8h3V6h-5z"/>
          </svg>
        </button>
        
        <!-- Volume Control -->
        <div class="volume-control">
          <button class="volume-btn" @click="toggleMute" :title="isMuted ? 'Включить звук' : 'Выключить звук'">
            <svg v-if="isMuted || volume === 0" width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M16.5 12c0-1.77-1.02-3.29-2.5-4.03v2.21l2.45 2.45c.03-.2.05-.41.05-.63zm2.5 0c0 .94-.2 1.82-.54 2.64l1.51 1.51C20.63 14.91 21 13.5 21 12c0-4.28-2.99-7.86-7-8.77v2.06c2.89.86 5 3.54 5 6.71zM4.27 3L3 4.27 7.73 9H3v6h4l5 5v-6.73l4.25 4.25c-.67.52-1.42.93-2.25 1.18v2.06c1.38-.31 2.63-.95 3.69-1.81L19.73 21 21 19.73l-9-9L4.27 3zM12 4L9.91 6.09 12 8.18V4z"/>
            </svg>
            <svg v-else-if="volume < 0.5" width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M18.5 12c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM5 9v6h4l5 5V4L9 9H5z"/>
            </svg>
            <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/>
            </svg>
          </button>
          
          <div 
            class="volume-slider"
            ref="volumeSlider"
            @mousedown="startVolumeDrag"
          >
            <div class="volume-track">
              <div class="volume-fill" :style="{ width: volumePercent + '%' }"></div>
            </div>
            <div 
              class="volume-thumb"
              :style="{ left: volumePercent + '%' }"
            ></div>
          </div>
        </div>
        
        <button class="extra-btn fullscreen-btn" @click="toggleFullscreen" title="На весь экран">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
            <path d="M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PlayerDesktop',
  
  props: {
    title: { type: String, default: 'Название трека' },
    artist: { type: String, default: 'Исполнитель' },
    coverUrl: { type: String, default: '' },
    currentTime: { type: Number, default: 0 },
    duration: { type: Number, default: 0 },
    volume: { type: Number, default: 1 },
    isPlaying: { type: Boolean, default: false },
    isLoading: { type: Boolean, default: false },
  },
  
  emits: ['play', 'pause', 'prev', 'next', 'seek', 'volume-change', 'shuffle', 'repeat', 'toggle-queue', 'fullscreen'],
  
  data() {
    return {
      showQueue: false,
      isShuffle: false,
      isRepeat: false,
      isMuted: false,
      prevVolume: 1,
      
      // Drag states
      isProgressDragging: false,
      isVolumeDragging: false,
      dragProgress: 0,
      dragVolume: 0,
    };
  },
  
  computed: {
    progressPercent() {
      if (this.isProgressDragging) return this.dragProgress;
      if (!this.duration) return 0;
      return (this.currentTime / this.duration) * 100;
    },
    
    volumePercent() {
      if (this.isVolumeDragging) return this.dragVolume * 100;
      return (this.isMuted ? 0 : this.volume) * 100;
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
    
    toggleShuffle() {
      this.isShuffle = !this.isShuffle;
      this.$emit('shuffle', this.isShuffle);
    },
    
    toggleRepeat() {
      this.isRepeat = !this.isRepeat;
      this.$emit('repeat', this.isRepeat);
    },
    
    toggleQueue() {
      this.showQueue = !this.showQueue;
      this.$emit('toggle-queue', this.showQueue);
    },
    
    toggleMute() {
      if (this.isMuted) {
        this.isMuted = false;
        this.$emit('volume-change', this.prevVolume);
      } else {
        this.prevVolume = this.volume;
        this.isMuted = true;
        this.$emit('volume-change', 0);
      }
    },
    
    toggleFullscreen() {
      this.$emit('fullscreen');
    },
    
    // ========== Progress Drag ==========
    startProgressDrag(e) {
      this.isProgressDragging = true;
      this.updateDragProgress(e);
      
      document.addEventListener('mousemove', this.handleProgressDrag);
      document.addEventListener('mouseup', this.stopProgressDrag);
    },
    
    handleProgressDrag(e) {
      if (!this.isProgressDragging) return;
      requestAnimationFrame(() => this.updateDragProgress(e));
    },
    
    updateDragProgress(e) {
      const bar = this.$refs.progressBar;
      if (!bar) return;
      
      const rect = bar.getBoundingClientRect();
      const x = Math.max(0, Math.min(e.clientX - rect.left, rect.width));
      this.dragProgress = (x / rect.width) * 100;
    },
    
    stopProgressDrag() {
      if (!this.isProgressDragging) return;
      
      const newTime = (this.dragProgress / 100) * this.duration;
      this.$emit('seek', newTime);
      
      this.isProgressDragging = false;
      document.removeEventListener('mousemove', this.handleProgressDrag);
      document.removeEventListener('mouseup', this.stopProgressDrag);
    },
    
    // ========== Volume Drag ==========
    startVolumeDrag(e) {
      this.isVolumeDragging = true;
      this.isMuted = false;
      this.updateVolumeFromEvent(e);
      
      document.addEventListener('mousemove', this.handleVolumeDrag);
      document.addEventListener('mouseup', this.stopVolumeDrag);
    },
    
    handleVolumeDrag(e) {
      if (!this.isVolumeDragging) return;
      requestAnimationFrame(() => this.updateVolumeFromEvent(e));
    },
    
    updateVolumeFromEvent(e) {
      const slider = this.$refs.volumeSlider;
      if (!slider) return;
      
      const rect = slider.getBoundingClientRect();
      const x = Math.max(0, Math.min(e.clientX - rect.left, rect.width));
      this.dragVolume = x / rect.width;
      
      // Emit immediately for real-time feedback
      this.$emit('volume-change', this.dragVolume);
    },
    
    stopVolumeDrag() {
      if (!this.isVolumeDragging) return;
      
      this.isVolumeDragging = false;
      document.removeEventListener('mousemove', this.handleVolumeDrag);
      document.removeEventListener('mouseup', this.stopVolumeDrag);
    },
  },
  
  beforeUnmount() {
    this.stopProgressDrag();
    this.stopVolumeDrag();
  }
};
</script>

<style scoped>
.desktop-player {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 90px;
  background: linear-gradient(180deg, rgba(35, 30, 55, 0.95) 0%, rgba(20, 16, 35, 0.98) 100%);
  backdrop-filter: blur(30px);
  -webkit-backdrop-filter: blur(30px);
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  z-index: 100;
  transition: height 0.3s ease;
}

/* Preloader */
.player-preloader {
  position: absolute;
  inset: 0;
  background: rgba(20, 16, 35, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

.loader-ring {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-top-color: #8b5cf6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Layout */
.player-layout {
  display: grid;
  grid-template-columns: minmax(180px, 280px) 1fr minmax(180px, 280px);
  align-items: center;
  height: 100%;
  padding: 0 16px;
  gap: 16px;
}

/* Left Panel */
.player-left {
  display: flex;
  align-items: center;
  gap: 14px;
  min-width: 0;
}

.cover-container {
  flex-shrink: 0;
}

.cover-wrapper {
  width: 56px;
  height: 56px;
  border-radius: 6px;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.cover-wrapper.is-playing {
  box-shadow: 0 4px 20px rgba(139, 92, 246, 0.3);
}

.cover-image {
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
  background: linear-gradient(135deg, #3a2e5a 0%, #1a1030 100%);
  color: rgba(255, 255, 255, 0.2);
}

.track-info {
  min-width: 0;
}

.track-title {
  font-size: 14px;
  font-weight: 600;
  color: white;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  cursor: default;
}

.track-title:hover {
  text-decoration: underline;
  cursor: pointer;
}

.track-artist {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.55);
  margin: 3px 0 0 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  cursor: default;
}

.track-artist:hover {
  color: rgba(255, 255, 255, 0.75);
  cursor: pointer;
}

/* Center Panel */
.player-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  max-width: 720px;
  margin: 0 auto;
  width: 100%;
}

/* Main Controls */
.main-controls {
  display: flex;
  align-items: center;
  gap: 16px;
}

.control-btn {
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4px;
  border-radius: 50%;
  transition: all 0.15s ease;
}

.control-btn:hover {
  color: white;
  transform: scale(1.06);
}

.control-btn:active {
  transform: scale(0.95);
}

.shuffle-btn.active,
.repeat-btn.active {
  color: #8b5cf6;
}

.shuffle-btn.active::after,
.repeat-btn.active::after {
  content: '';
  position: absolute;
  bottom: -4px;
  left: 50%;
  transform: translateX(-50%);
  width: 4px;
  height: 4px;
  background: #8b5cf6;
  border-radius: 50%;
}

.shuffle-btn,
.repeat-btn {
  position: relative;
}

.play-btn {
  width: 40px;
  height: 40px;
  background: white;
  color: black;
}

.play-btn:hover {
  transform: scale(1.08);
  color: black;
}

/* Progress Bar */
.progress-container {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
}

.time {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  font-variant-numeric: tabular-nums;
  min-width: 35px;
}

.current-time {
  text-align: right;
}

.duration {
  text-align: left;
}

.progress-bar {
  flex: 1;
  height: 16px;
  display: flex;
  align-items: center;
  cursor: pointer;
  position: relative;
}

.progress-track {
  width: 100%;
  height: 4px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 2px;
  transition: width 0.1s linear;
}

.progress-bar:hover .progress-fill {
  background: #8b5cf6;
}

.progress-thumb {
  position: absolute;
  top: 50%;
  width: 12px;
  height: 12px;
  background: white;
  border-radius: 50%;
  transform: translate(-50%, -50%);
  opacity: 0;
  transition: opacity 0.15s ease;
  pointer-events: none;
}

.progress-bar:hover .progress-thumb {
  opacity: 1;
}

/* Right Panel */
.player-right {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
}

.extra-btn {
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.55);
  cursor: pointer;
  padding: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.15s ease;
}

.extra-btn:hover {
  color: white;
}

.extra-btn.active {
  color: #8b5cf6;
}

/* Volume Control */
.volume-control {
  display: flex;
  align-items: center;
  gap: 8px;
}

.volume-btn {
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.55);
  cursor: pointer;
  padding: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: color 0.15s ease;
}

.volume-btn:hover {
  color: white;
}

.volume-slider {
  width: 93px;
  height: 16px;
  display: flex;
  align-items: center;
  cursor: pointer;
  position: relative;
}

.volume-track {
  width: 100%;
  height: 4px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 2px;
  overflow: hidden;
}

.volume-fill {
  height: 100%;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 2px;
  transition: none; /* No transition for immediate response */
}

.volume-slider:hover .volume-fill {
  background: #8b5cf6;
}

.volume-thumb {
  position: absolute;
  top: 50%;
  width: 12px;
  height: 12px;
  background: white;
  border-radius: 50%;
  transform: translate(-50%, -50%);
  opacity: 0;
  transition: opacity 0.15s ease;
  pointer-events: none;
}

.volume-slider:hover .volume-thumb {
  opacity: 1;
}

/* Animations */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Responsive for smaller screens */
@media (max-width: 1024px) {
  .player-layout {
    grid-template-columns: minmax(140px, 220px) 1fr minmax(140px, 200px);
    gap: 12px;
  }
  
  .cover-wrapper {
    width: 48px;
    height: 48px;
  }
  
  .track-title {
    font-size: 13px;
  }
}

@media (max-width: 768px) {
  .desktop-player {
    display: none; /* Hide on mobile, use PlayerMobile instead */
  }
}
</style>

<template>
  <div class="desktop-player-wrapper">
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
            <Transition name="cover-swap" mode="out-in">
              <div class="cover-wrapper" :class="{ 'is-playing': isPlaying }" :key="coverUrl">
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
            </Transition>
          </div>
          
          <Transition name="info-swap" mode="out-in">
            <div class="track-info" :key="title">
              <h2 class="track-title" :class="{ 'is-long': isLongTitle }">
                <span class="track-title-inner">
                  <span class="track-title-text">{{ title }}</span>
                  <span v-if="isLongTitle" class="track-title-text">{{ title }}</span>
                </span>
              </h2>
              <p class="track-artist">{{ artist }}</p>
            </div>
          </Transition>
        </div>

        <!-- Center Panel - Controls -->
        <div class="player-center">
          <!-- Main Controls -->
          <div class="main-controls">
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
    
    <!-- Fullscreen Mode -->
    <Teleport to="body">
      <Transition name="fade-scale">
        <div v-if="showFullscreen" class="fullscreen-player-overlay">
          <div class="fullscreen-player">
            <!-- Close button -->
            <button class="fs-close-btn" @click="toggleFullscreen">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
              </svg>
            </button>
            
            <!-- Large Cover -->
            <div class="fs-cover-wrapper">
              <Transition name="fs-cover-swap" mode="out-in">
                <div class="fs-cover" :class="{ 'playing': isPlaying }" :key="coverUrl">
                  <img v-if="coverUrl" :src="highResCoverUrl" alt="Cover"/>
                  <div v-else class="fs-cover-placeholder">
                    <svg width="120" height="120" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z"/>
                    </svg>
                  </div>
                </div>
              </Transition>
            </div>
            
            <!-- Track Info -->
            <Transition name="fs-info-swap" mode="out-in">
              <div class="fs-info" :key="title">
                <h1 class="fs-title" :class="{ 'is-long': isLongTitle }">
                  <span class="fs-title-inner">
                    <span class="fs-title-text">{{ title }}</span>
                    <span v-if="isLongTitle" class="fs-title-text">{{ title }}</span>
                  </span>
                </h1>
                <p class="fs-artist">{{ artist }}</p>
              </div>
            </Transition>
            
            <!-- Progress -->
            <div class="fs-progress">
              <div 
                class="fs-progress-bar"
                ref="fsProgressBar"
                @mousedown="startProgressDrag"
              >
                <div class="fs-progress-track">
                  <div class="fs-progress-fill" :style="{ width: progressPercent + '%' }"></div>
                </div>
                <div class="fs-progress-thumb" :style="{ left: progressPercent + '%' }"></div>
              </div>
              <div class="fs-times">
                <span class="fs-time-current">{{ formatTime(currentTime) }}</span>
                <span class="fs-time-duration">{{ formatTime(duration) }}</span>
              </div>
            </div>
            
            <!-- Controls -->
            <div class="fs-controls">
              <button class="fs-control-btn" @click="prevTrack">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M6 6h2v12H6zm3.5 6l8.5 6V6z"/>
                </svg>
              </button>
              
              <button class="fs-play-btn" @click="togglePlay">
                <svg v-if="!isPlaying" width="48" height="48" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M8 5v14l11-7z"/>
                </svg>
                <svg v-else width="48" height="48" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>
                </svg>
              </button>
              
              <button class="fs-control-btn" @click="nextTrack">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z"/>
                </svg>
              </button>
            </div>
            
            <!-- Volume -->
            <div class="fs-volume">
              <button class="fs-volume-btn" @click="toggleMute">
                <svg v-if="isMuted || volume === 0" width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M16.5 12c0-1.77-1.02-3.29-2.5-4.03v2.21l2.45 2.45c.03-.2.05-.41.05-.63zm2.5 0c0 .94-.2 1.82-.54 2.64l1.51 1.51C20.63 14.91 21 13.5 21 12c0-4.28-2.99-7.86-7-8.77v2.06c2.89.86 5 3.54 5 6.71zM4.27 3L3 4.27 7.73 9H3v6h4l5 5v-6.73l4.25 4.25c-.67.52-1.42.93-2.25 1.18v2.06c1.38-.31 2.63-.95 3.69-1.81L19.73 21 21 19.73l-9-9L4.27 3zM12 4L9.91 6.09 12 8.18V4z"/>
                </svg>
                <svg v-else width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/>
                </svg>
              </button>
              <div 
                class="fs-volume-slider"
                ref="fsVolumeSlider"
                @mousedown="startVolumeDrag"
              >
                <div class="fs-volume-track">
                  <div class="fs-volume-fill" :style="{ width: volumePercent + '%' }"></div>
                </div>
                <div class="fs-volume-thumb" :style="{ left: volumePercent + '%' }"></div>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onBeforeUnmount } from 'vue';
import { formatTime, useProgressDrag, useVolumeDrag, getHighResCover } from '@/composables/usePlayer';

const props = defineProps({
  title: { type: String, default: 'Название трека' },
  artist: { type: String, default: 'Исполнитель' },
  coverUrl: { type: String, default: '' },
  currentTime: { type: Number, default: 0 },
  duration: { type: Number, default: 0 },
  volume: { type: Number, default: 1 },
  isPlaying: { type: Boolean, default: false },
  isLoading: { type: Boolean, default: false },
});

const emit = defineEmits(['play', 'pause', 'prev', 'next', 'seek', 'volume-change', 'toggle-queue', 'fullscreen']);

// Local state
const showQueue = ref(false);
const showFullscreen = ref(false);
const isMuted = ref(false);
const prevVolume = ref(1);

// Refs
const progressBar = ref(null);
const fsProgressBar = ref(null);
const volumeSlider = ref(null);
const fsVolumeSlider = ref(null);

// Get active refs based on fullscreen state
const getActiveProgressRef = () => showFullscreen.value ? fsProgressBar.value : progressBar.value;
const getActiveVolumeRef = () => showFullscreen.value ? fsVolumeSlider.value : volumeSlider.value;

// Progress drag
const { 
  isDragging: isProgressDragging, 
  dragPercent: dragProgress, 
  startDrag: startProgressDragBase,
  cleanup: cleanupProgressDrag
} = useProgressDrag(
  { value: null }, // Dummy ref, we'll use custom ref getter
  (percent) => {
    const newTime = (percent / 100) * props.duration;
    emit('seek', newTime);
  }
);

// Volume drag
const {
  isDragging: isVolumeDragging,
  dragValue: dragVolume,
  startDrag: startVolumeDragBase,
  cleanup: cleanupVolumeDrag
} = useVolumeDrag(
  { value: null },
  (vol) => {
    isMuted.value = false;
    emit('volume-change', vol);
  }
);

// Custom start drag functions that use active refs
const startProgressDrag = (e) => {
  const activeRef = getActiveProgressRef();
  if (!activeRef) return;
  
  isProgressDragging.value = true;
  updateProgressFromEvent(e, activeRef);
  
  const handleMove = (e) => {
    if (!isProgressDragging.value) return;
    requestAnimationFrame(() => updateProgressFromEvent(e, activeRef));
  };
  
  const handleEnd = () => {
    if (!isProgressDragging.value) return;
    const newTime = (dragProgress.value / 100) * props.duration;
    emit('seek', newTime);
    isProgressDragging.value = false;
    document.removeEventListener('mousemove', handleMove);
    document.removeEventListener('mouseup', handleEnd);
  };
  
  document.addEventListener('mousemove', handleMove);
  document.addEventListener('mouseup', handleEnd);
};

const updateProgressFromEvent = (e, element) => {
  const rect = element.getBoundingClientRect();
  const x = Math.max(0, Math.min(e.clientX - rect.left, rect.width));
  dragProgress.value = (x / rect.width) * 100;
};

const startVolumeDrag = (e) => {
  const activeRef = getActiveVolumeRef();
  if (!activeRef) return;
  
  isVolumeDragging.value = true;
  isMuted.value = false;
  updateVolumeFromEvent(e, activeRef);
  
  const handleMove = (e) => {
    if (!isVolumeDragging.value) return;
    requestAnimationFrame(() => updateVolumeFromEvent(e, activeRef));
  };
  
  const handleEnd = () => {
    isVolumeDragging.value = false;
    document.removeEventListener('mousemove', handleMove);
    document.removeEventListener('mouseup', handleEnd);
  };
  
  document.addEventListener('mousemove', handleMove);
  document.addEventListener('mouseup', handleEnd);
};

const updateVolumeFromEvent = (e, element) => {
  const rect = element.getBoundingClientRect();
  const x = Math.max(0, Math.min(e.clientX - rect.left, rect.width));
  dragVolume.value = x / rect.width;
  emit('volume-change', dragVolume.value);
};

// Computed
const progressPercent = computed(() => {
  if (isProgressDragging.value) return dragProgress.value;
  if (!props.duration) return 0;
  return (props.currentTime / props.duration) * 100;
});

const volumePercent = computed(() => {
  if (isVolumeDragging.value) return dragVolume.value * 100;
  return (isMuted.value ? 0 : props.volume) * 100;
});

const isLongTitle = computed(() => props.title && props.title.length > 25);
const highResCoverUrl = computed(() => getHighResCover(props.coverUrl));

// Methods
const togglePlay = () => emit(props.isPlaying ? 'pause' : 'play');
const prevTrack = () => emit('prev');
const nextTrack = () => emit('next');

const toggleQueue = () => {
  showQueue.value = !showQueue.value;
  emit('toggle-queue', showQueue.value);
};

const toggleMute = () => {
  if (isMuted.value) {
    isMuted.value = false;
    emit('volume-change', prevVolume.value);
  } else {
    prevVolume.value = props.volume;
    isMuted.value = true;
    emit('volume-change', 0);
  }
};

const toggleFullscreen = () => {
  showFullscreen.value = !showFullscreen.value;
  document.body.style.overflow = showFullscreen.value ? 'hidden' : '';
  emit('fullscreen', showFullscreen.value);
};

onBeforeUnmount(() => {
  document.body.style.overflow = '';
});
</script>

<style scoped>
.desktop-player {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 90px;
  background: linear-gradient(180deg, rgba(20, 16, 30, 0.98) 0%, rgba(12, 10, 20, 0.99) 100%);
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
  transition: transform 0.3s ease, box-shadow 0.5s ease;
}

.cover-wrapper.is-playing {
  box-shadow: 
    0 4px 20px rgba(99, 58, 137, 0.4),
    0 0 30px rgba(191, 90, 242, 0.2);
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
  overflow: hidden;
}

.track-title {
  font-size: 14px;
  font-weight: 600;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  cursor: default;
}

.track-title .track-title-text {
  background: linear-gradient(90deg, #D0BCFF, #00d9e7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Marquee анимация для длинных названий */
.track-title.is-long {
  text-overflow: clip;
}

.track-title.is-long .track-title-inner {
  display: inline-flex;
  animation: desktop-marquee 14s linear infinite;
}

.track-title.is-long .track-title-text {
  flex-shrink: 0;
  padding-right: 60px;
}

@keyframes desktop-marquee {
  0% { transform: translateX(0); }
  100% { transform: translateX(-50%); }
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
  color: #633A89;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px;
  border-radius: 50%;
  transition: all 0.15s ease;
  width: 44px;
  height: 44px;
}

.control-btn:hover {
  color: #bf5af2;
  transform: scale(1.1);
}

.control-btn:active {
  transform: scale(0.95);
}

.shuffle-btn.active,
.repeat-btn.active {
  color: #D0BCFF;
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
  background: #D0BCFF;
  border-radius: 50%;
}

.shuffle-btn,
.repeat-btn {
  position: relative;
}

.play-btn {
  width: 40px;
  height: 40px;
  background: #633A89;
  color: white;
  box-shadow: 0 2px 12px rgba(99, 58, 137, 0.3);
}

.play-btn:hover {
  transform: scale(1.08);
  color: white;
  box-shadow: 0 4px 20px rgba(99, 58, 137, 0.5);
}

/* Progress Bar */
.progress-container {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
}

.time {
  font-size: 12px;
  font-variant-numeric: tabular-nums;
  min-width: 35px;
  font-weight: 600;
}

.current-time {
  text-align: right;
  color: #00ffff;
  text-shadow: 
    0 0 5px rgba(0, 255, 255, 0.8),
    0 0 10px rgba(0, 255, 255, 0.5);
}

.duration {
  text-align: left;
  color: #bf5af2;
  text-shadow: 
    0 0 5px rgba(191, 90, 242, 0.8),
    0 0 10px rgba(191, 90, 242, 0.5);
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
  background: linear-gradient(90deg, #00d9e7 0%, #633A89 100%);
  border-radius: 2px;
  transition: none;
}

.progress-bar:hover .progress-fill {
  background: linear-gradient(90deg, #00d9e7 0%, #633A89 100%);
}

.progress-thumb {
  position: absolute;
  top: 50%;
  width: 14px;
  height: 14px;
  background: #D0BCFF;
  border-radius: 50%;
  transform: translate(-50%, -50%);
  opacity: 0;
  transition: opacity 0.15s ease;
  pointer-events: none;
  box-shadow: 0 0 8px rgba(208, 188, 255, 0.5);
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
  color: #D0BCFF;
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
  background: linear-gradient(90deg, #00d9e7 0%, #633A89 100%);
  border-radius: 2px;
  transition: none;
}

.volume-slider:hover .volume-fill {
  background: linear-gradient(90deg, #00d9e7 0%, #633A89 100%);
}

.volume-thumb {
  position: absolute;
  top: 50%;
  width: 14px;
  height: 14px;
  background: #D0BCFF;
  border-radius: 50%;
  transform: translate(-50%, -50%);
  opacity: 0;
  transition: opacity 0.15s ease;
  pointer-events: none;
  box-shadow: 0 0 8px rgba(208, 188, 255, 0.5);
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

.fade-scale-enter-active,
.fade-scale-leave-active {
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}

.fade-scale-enter-from,
.fade-scale-leave-to {
  opacity: 0;
  transform: scale(0.95);
}

/* Cover swap animation */
.cover-swap-enter-active,
.cover-swap-leave-active {
  transition: all 0.25s ease;
}

.cover-swap-enter-from {
  opacity: 0;
  transform: scale(0.9);
}

.cover-swap-leave-to {
  opacity: 0;
  transform: scale(1.1);
}

/* Info swap animation */
.info-swap-enter-active,
.info-swap-leave-active {
  transition: all 0.2s ease;
}

.info-swap-enter-from {
  opacity: 0;
  transform: translateX(-10px);
}

.info-swap-leave-to {
  opacity: 0;
  transform: translateX(10px);
}

/* ============ FULLSCREEN MODE ============ */
.fullscreen-player-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: linear-gradient(180deg, #1a1030 0%, #0d0815 50%, #050208 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.fullscreen-player {
  width: 100%;
  max-width: 600px;
  padding: 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 32px;
}

.fs-close-btn {
  position: absolute;
  top: 24px;
  right: 24px;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: rgba(255, 255, 255, 0.7);
  padding: 12px;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.2s;
}

.fs-close-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  color: white;
}

.fs-cover-wrapper {
  width: 100%;
  max-width: 400px;
}

.fs-cover {
  width: 100%;
  aspect-ratio: 1/1;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 
    0 30px 80px rgba(0, 0, 0, 0.6),
    0 0 0 rgba(208, 188, 255, 0);
  transition: box-shadow 0.8s ease;
}

.fs-cover.playing {
  box-shadow: 
    0 30px 100px rgba(99, 58, 137, 0.4),
    0 0 60px rgba(208, 188, 255, 0.2);
}

/* Pulse animation only when loading */
.fs-cover.loading {
  animation: fs-pulse-glow-loading 1.5s ease-in-out infinite;
}

@keyframes fs-pulse-glow-loading {
  0%, 100% { box-shadow: 0 30px 80px rgba(0, 0, 0, 0.6); }
  50% { box-shadow: 0 30px 120px rgba(208, 188, 255, 0.35); }
}

.fs-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.fs-cover-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #3a2e5a 0%, #1a1030 100%);
  color: rgba(255, 255, 255, 0.15);
}

.fs-info {
  text-align: center;
  width: 100%;
  overflow: hidden;
}

.fs-title {
  font-size: 28px;
  font-weight: 700;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.fs-title .fs-title-text {
  background: linear-gradient(90deg, #D0BCFF, #00d9e7);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Marquee анимация для длинных названий */
.fs-title.is-long {
  text-overflow: clip;
}

.fs-title.is-long .fs-title-inner {
  display: inline-flex;
  animation: fs-marquee 16s linear infinite;
}

.fs-title.is-long .fs-title-text {
  flex-shrink: 0;
  padding-right: 100px;
}

@keyframes fs-marquee {
  0% { transform: translateX(0); }
  100% { transform: translateX(-50%); }
}

.fs-artist {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.6);
  margin: 8px 0 0 0;
}

.fs-progress {
  width: 100%;
}

.fs-progress-bar {
  position: relative;
  height: 24px;
  display: flex;
  align-items: center;
  cursor: pointer;
}

.fs-progress-track {
  width: 100%;
  height: 6px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 3px;
  overflow: hidden;
}

.fs-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #00d9e7 0%, #633A89 100%);
  border-radius: 3px;
  transition: none;
}

.fs-progress-thumb {
  position: absolute;
  top: 50%;
  width: 18px;
  height: 18px;
  background: #D0BCFF;
  border-radius: 50%;
  transform: translate(-50%, -50%);
  box-shadow: 0 0 12px rgba(208, 188, 255, 0.6);
  transition: transform 0.15s;
}

.fs-progress-bar:hover .fs-progress-thumb {
  transform: translate(-50%, -50%) scale(1.1);
}

.fs-times {
  display: flex;
  justify-content: space-between;
  margin-top: 12px;
}

.fs-time-current {
  font-size: 13px;
  color: #00d9e7;
  text-shadow: 0 0 8px rgba(0, 217, 231, 0.5);
}

.fs-time-duration {
  font-size: 13px;
  color: #bf5af2;
  text-shadow: 0 0 8px rgba(191, 90, 242, 0.5);
}

.fs-controls {
  display: flex;
  align-items: center;
  gap: 40px;
}

.fs-control-btn {
  background: transparent;
  border: none;
  color: #633A89;
  cursor: pointer;
  padding: 12px;
  transition: all 0.2s;
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.fs-control-btn svg {
  width: 48px;
  height: 48px;
}

.fs-control-btn:hover {
  color: #8B5BA8;
  transform: scale(1.1);
}

.fs-play-btn {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: #633A89;
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 32px rgba(99, 58, 137, 0.4);
  transition: all 0.2s;
}

.fs-play-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 12px 40px rgba(99, 58, 137, 0.6);
}

.fs-volume {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 200px;
}

.fs-volume-btn {
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  padding: 4px;
  transition: color 0.2s;
}

.fs-volume-btn:hover {
  color: white;
}

.fs-volume-slider {
  flex: 1;
  height: 20px;
  display: flex;
  align-items: center;
  cursor: pointer;
  position: relative;
}

.fs-volume-track {
  width: 100%;
  height: 4px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 2px;
  overflow: hidden;
}

.fs-volume-fill {
  height: 100%;
  background: linear-gradient(90deg, #00d9e7 0%, #633A89 100%);
  border-radius: 2px;
  transition: none;
}

.fs-volume-thumb {
  position: absolute;
  top: 50%;
  width: 14px;
  height: 14px;
  background: #D0BCFF;
  border-radius: 50%;
  transform: translate(-50%, -50%);
  box-shadow: 0 0 8px rgba(208, 188, 255, 0.5);
}

/* Fullscreen cover/info transition animations */
.fs-cover-swap-enter-active,
.fs-cover-swap-leave-active {
  transition: all 0.35s ease;
}

.fs-cover-swap-enter-from {
  opacity: 0;
  transform: scale(0.95) translateY(10px);
}

.fs-cover-swap-leave-to {
  opacity: 0;
  transform: scale(0.95) translateY(-10px);
}

.fs-info-swap-enter-active,
.fs-info-swap-leave-active {
  transition: all 0.3s ease;
}

.fs-info-swap-enter-from {
  opacity: 0;
  transform: translateY(15px);
}

.fs-info-swap-leave-to {
  opacity: 0;
  transform: translateY(-15px);
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

/* Hide desktop player on touch devices (mobile/tablet) regardless of screen size */
@media (pointer: coarse) {
  .desktop-player {
    display: none !important;
  }
}
</style>

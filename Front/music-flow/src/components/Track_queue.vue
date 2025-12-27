<template>
  <div class="queue-container">
    <div class="queue-scroll-wrapper">
      <ul class="queue-list">
        <li 
          v-for="(track, index) in tracks" 
          :key="track.title + '-' + index"
          :class="[
            'queue-item', 
            { 
              'current': index === currentTrackIndex, 
              'dragging': dragIndex === index,
              'drag-over-above': dragOverIndex === index && dragIndex > index,
              'drag-over-below': dragOverIndex === index && dragIndex < index
            }
          ]"
          :draggable="isDragHandleActive"
          @dragstart="onDragStart($event, index)"
          @dragover.prevent="onDragOver($event, index)"
          @drop="onDrop($event, index)"
          @dragend="onDragEnd"
          @click="onTrackClick(index)"
        >
          <div 
            class="drag-handle"
            @mousedown="enableDrag"
            @mouseup="disableDrag"
            @touchstart.prevent="enableDrag"
            @touchend="disableDrag"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
              <path d="M11 18c0 1.1-.9 2-2 2s-2-.9-2-2 .9-2 2-2 2 .9 2 2zm-2-8c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm0-6c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm6 4c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zm0 2c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm0 6c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z"/>
            </svg>
          </div>
          
          <div class="track-cover">
            <img 
              v-if="track.cover" 
              :src="track.cover" 
              :alt="track.title"
              class="cover-img"
              @error="onCoverError($event)"
            />
            <div v-else class="cover-placeholder">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z"/>
              </svg>
            </div>
            <div v-if="index === currentTrackIndex" class="playing-indicator">
              <span class="bar"></span>
              <span class="bar"></span>
              <span class="bar"></span>
            </div>
            <!-- Play overlay on hover -->
            <div v-if="index !== currentTrackIndex" class="play-overlay">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="white">
                <path d="M8 5v14l11-7z"/>
              </svg>
            </div>
          </div>
          
          <div class="track-info">
            <span class="track-name">{{ track.title }}</span>
            <span class="track-artist">{{ track.artist }}</span>
          </div>
          
          <span class="track-duration">{{ formatDuration(track.duration) }}</span>
        </li>
      </ul>
      
      <div v-if="tracks.length === 0" class="empty-queue">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="currentColor" class="empty-icon">
          <path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z"/>
        </svg>
        <p>Очередь пуста</p>
        <p class="empty-hint">Добавьте треки по ссылке из Яндекс.Музыки</p>
      </div>
    </div>
  </div>
</template>


<script>
export default {
  props: {
    tracks: {
      type: Array,
      required: true,
      default: () => []
    },
    currentTrackIndex: {
      type: Number,
      default: 0
    }
  },
  
  emits: ['reorder', 'play-track'],
  
  data() {
    return {
      dragIndex: null,
      dragOverIndex: null,
      isDragHandleActive: false,
    };
  },
  
  methods: {
    formatDuration(seconds) {
      if (!seconds || !isFinite(seconds)) return '0:00';
      const mins = Math.floor(seconds / 60);
      const secs = Math.floor(seconds % 60);
      return `${mins}:${secs.toString().padStart(2, '0')}`;
    },
    
    onCoverError(event) {
      event.target.style.display = 'none';
    },
    
    enableDrag() {
      this.isDragHandleActive = true;
    },
    
    disableDrag() {
      // Небольшая задержка чтобы drag успел начаться
      setTimeout(() => {
        if (this.dragIndex === null) {
          this.isDragHandleActive = false;
        }
      }, 100);
    },
    
    onDragStart(event, index) {
      if (!this.isDragHandleActive) {
        event.preventDefault();
        return;
      }
      this.dragIndex = index;
      event.dataTransfer.effectAllowed = 'move';
      event.dataTransfer.setData('text/plain', index.toString());
      
      // Добавляем класс к body для курсора
      document.body.classList.add('is-dragging-track');
    },
    
    onDragOver(event, index) {
      if (this.dragIndex === null) return;
      this.dragOverIndex = index;
    },
    
    onDrop(event, targetIndex) {
      const sourceIndex = this.dragIndex;
      
      if (sourceIndex === null || sourceIndex === targetIndex) {
        this.resetDrag();
        return;
      }
      
      const newTracks = [...this.tracks];
      const [removed] = newTracks.splice(sourceIndex, 1);
      newTracks.splice(targetIndex, 0, removed);
      
      // Передаём новый список треков и индексы для пересчёта currentTrackIndex
      this.$emit('reorder', newTracks, sourceIndex, targetIndex);
      this.resetDrag();
    },
    
    onDragEnd() {
      this.resetDrag();
      document.body.classList.remove('is-dragging-track');
    },
    
    resetDrag() {
      this.dragIndex = null;
      this.dragOverIndex = null;
      this.isDragHandleActive = false;
    },
    
    onTrackClick(index) {
      // Не переключать если это drag операция
      if (this.isDragHandleActive || this.dragIndex !== null) return;
      // Переключить на этот трек
      this.$emit('play-track', index);
    }
  }
}
</script>

<style scoped>
.queue-container {
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  background: rgba(23, 18, 34, 0.5);
  border-radius: 20px;
  box-sizing: border-box;
  height: 100%;
  overflow: hidden;
}

.queue-scroll-wrapper {
  flex-grow: 1;
  overflow-y: auto;
  padding: 12px;
  padding-right: 6px;
}

.queue-scroll-wrapper::-webkit-scrollbar {
  width: 6px;
}

.queue-scroll-wrapper::-webkit-scrollbar-track {
  background: transparent;
}

.queue-scroll-wrapper::-webkit-scrollbar-thumb {
  background-color: rgba(208, 188, 255, 0.3);
  border-radius: 3px;
}

.queue-scroll-wrapper::-webkit-scrollbar-thumb:hover {
  background-color: rgba(208, 188, 255, 0.5);
}

.queue-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.queue-item {
  display: flex;
  align-items: center;
  padding: 8px 10px;
  background: rgba(208, 188, 255, 0.05);
  border-radius: 10px;
  transition: all 0.2s ease, transform 0.15s ease;
  gap: 10px;
  cursor: pointer;
  position: relative;
}

.queue-item:hover {
  background: rgba(208, 188, 255, 0.12);
}

.queue-item:hover .play-overlay {
  opacity: 1;
}

.queue-item.current {
  background: rgba(0, 217, 231, 0.1);
  border: 1px solid rgba(0, 217, 231, 0.2);
}

.queue-item.dragging {
  opacity: 0.4;
  transform: scale(0.98);
  cursor: grabbing;
}

/* Визуальный индикатор места вставки */
.queue-item.drag-over-above::before {
  content: '';
  position: absolute;
  top: -4px;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #00d9e7 0%, #9333ea 100%);
  border-radius: 2px;
  animation: pulse-line 1s ease infinite;
}

.queue-item.drag-over-below::after {
  content: '';
  position: absolute;
  bottom: -4px;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #00d9e7 0%, #9333ea 100%);
  border-radius: 2px;
  animation: pulse-line 1s ease infinite;
}

@keyframes pulse-line {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.drag-handle {
  color: rgba(255, 255, 255, 0.25);
  cursor: grab;
  flex-shrink: 0;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s;
}

.drag-handle:hover {
  color: rgba(255, 255, 255, 0.6);
  background: rgba(255, 255, 255, 0.1);
}

.drag-handle:active {
  cursor: grabbing;
}

.track-cover {
  width: 40px;
  height: 40px;
  border-radius: 6px;
  overflow: hidden;
  flex-shrink: 0;
  position: relative;
  background: rgba(208, 188, 255, 0.1);
}

.cover-img {
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
  color: rgba(208, 188, 255, 0.4);
}

.play-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s ease;
  border-radius: 6px;
}

.playing-indicator {
  position: absolute;
  bottom: 4px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 2px;
  align-items: flex-end;
  height: 12px;
}

.playing-indicator .bar {
  width: 3px;
  background: #00d9e7;
  border-radius: 1px;
  animation: sound 0.5s ease infinite;
}

.playing-indicator .bar:nth-child(1) {
  height: 6px;
  animation-delay: 0s;
}

.playing-indicator .bar:nth-child(2) {
  height: 10px;
  animation-delay: 0.15s;
}

.playing-indicator .bar:nth-child(3) {
  height: 4px;
  animation-delay: 0.3s;
}

@keyframes sound {
  0%, 100% {
    transform: scaleY(1);
  }
  50% {
    transform: scaleY(0.5);
  }
}

.track-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  gap: 2px;
}

.track-name {
  font-weight: 500;
  color: white;
  font-size: 13px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.track-artist {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.track-duration {
  flex-shrink: 0;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
  font-variant-numeric: tabular-nums;
}

.empty-queue {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: rgba(255, 255, 255, 0.4);
  text-align: center;
}

.empty-icon {
  opacity: 0.3;
  margin-bottom: 12px;
}

.empty-queue p {
  margin: 0;
  font-size: 14px;
}

.empty-hint {
  margin-top: 8px !important;
  font-size: 12px !important;
  color: rgba(255, 255, 255, 0.3);
}

/* Анимации списка */
.track-list-enter-active {
  transition: all 0.3s ease;
}

.track-list-leave-active {
  transition: all 0.2s ease;
}

.track-list-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}

.track-list-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

.track-list-move {
  transition: transform 0.3s ease;
}

@media (max-width: 768px) {
  .queue-scroll-wrapper {
    padding: 10px;
  }
  
  .queue-item {
    padding: 8px;
    gap: 8px;
  }
  
  .track-cover {
    width: 36px;
    height: 36px;
  }
  
  .track-name {
    font-size: 12px;
  }
  
  .track-artist {
    font-size: 10px;
  }
  
  .drag-handle {
    display: none;
  }
}
</style>

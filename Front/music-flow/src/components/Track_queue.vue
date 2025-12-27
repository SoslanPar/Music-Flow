<template>
  <div class="queue-container">
    <!-- Loading skeleton -->
    <div v-if="isLoading" class="queue-loading">
      <div v-for="i in 5" :key="i" class="skeleton-item">
        <div class="skeleton-handle"></div>
        <div class="skeleton-cover"></div>
        <div class="skeleton-info">
          <div class="skeleton-title"></div>
          <div class="skeleton-artist"></div>
        </div>
        <div class="skeleton-duration"></div>
      </div>
    </div>
    
    <div v-else class="queue-scroll-wrapper">
      <TransitionGroup name="track-list" tag="ul" class="queue-list">
        <li 
          v-for="(track, index) in tracks" 
          :key="track.id || (track.title + '-' + track.artist)"
          :class="[
            'queue-item', 
            { 
              'current': index === currentTrackIndex, 
              'dragging': dragIndex === index && isMouseDragging,
              'drag-over-above': dragOverIndex === index && dragIndex > index && dragIndex !== null,
              'drag-over-below': dragOverIndex === index && dragIndex < index && dragIndex !== null,
              'swiping': swipeIndex === index,
              'swipe-delete-ready': swipeIndex === index && swipeOffset < -60
            }
          ]"
          :style="getItemStyle(index)"
          @click="onTrackClick(index)"
          @touchstart="onSwipeStart($event, index)"
          @touchmove="onSwipeMove($event)"
          @touchend="onSwipeEnd($event, index)"
        >
          <!-- Delete background (full width red) -->
          <div class="delete-bg" :class="{ 'active': swipeIndex === index && swipeOffset < -30 }">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor">
              <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
            </svg>
            <span>Удалить</span>
          </div>
          
          <div class="track-cover">
            <img 
              v-if="track.cover" 
              :src="getHighResCover(track.cover)" 
              :alt="track.title"
              class="cover-img"
              @error="onCoverError($event)"
            />
            <div v-else class="cover-placeholder">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z"/>
              </svg>
            </div>
            <div v-if="index === currentTrackIndex" class="playing-indicator" :class="{ 'paused': !isPlaying }">
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
          
          <div class="track-actions">
            <span class="track-duration">{{ formatDuration(track.duration) }}</span>
            <button 
              class="delete-btn" 
              @click.stop="deleteTrack(index)"
              title="Удалить трек"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
              </svg>
            </button>
          </div>
          
          <!-- Drag handle moved to right -->
          <div 
            class="drag-handle"
            @mousedown.stop="startMouseDrag($event, index)"
            @touchstart.stop="startTouchDrag($event, index)"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
              <path d="M11 18c0 1.1-.9 2-2 2s-2-.9-2-2 .9-2 2-2 2 .9 2 2zm-2-8c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm0-6c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm6 4c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zm0 2c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm0 6c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z"/>
            </svg>
          </div>
        </li>
      </TransitionGroup>
      
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
    },
    isPlaying: {
      type: Boolean,
      default: false
    },
    isLoading: {
      type: Boolean,
      default: false
    }
  },
  
  emits: ['reorder', 'play-track', 'delete-track'],
  
  data() {
    return {
      dragIndex: null,
      dragOverIndex: null,
      isDragHandleActive: false,
      // Mouse drag state (desktop)
      isMouseDragging: false,
      mouseStartY: 0,
      mouseCurrentY: 0,
      mouseDraggedElement: null,
      // Touch drag state
      isTouchDragging: false,
      touchStartY: 0,
      touchCurrentY: 0,
      // Swipe to delete state
      swipeIndex: null,
      swipeStartX: 0,
      swipeOffset: 0,
      isSwipeActive: false,
      touchDraggedElement: null,
      touchPlaceholderIndex: null,
    };
  },
  
  methods: {
    formatDuration(seconds) {
      if (!seconds || !isFinite(seconds)) return '0:00';
      const mins = Math.floor(seconds / 60);
      const secs = Math.floor(seconds % 60);
      return `${mins}:${secs.toString().padStart(2, '0')}`;
    },
    
    /**
     * Улучшает качество обложки Yandex Music
     * Заменяет размер в URL на высокое разрешение (400x400)
     */
    getHighResCover(coverUrl) {
      if (!coverUrl) return '';
      // Yandex Music cover URLs обычно содержат размер, например: 100x100, 200x200
      // Заменяем на 400x400 для высокого разрешения
      return coverUrl.replace(/\d+x\d+/, '400x400');
    },
    
    onCoverError(event) {
      event.target.style.display = 'none';
    },
    
    /**
     * Начать touch drag - напрямую получаем индекс
     */
    startTouchDrag(event, index) {
      event.preventDefault();
      
      const touch = event.touches[0];
      const listItem = event.target.closest('.queue-item');
      if (!listItem) return;
      
      this.isDragHandleActive = true;
      this.isTouchDragging = true;
      this.dragIndex = index;
      this.touchStartY = touch.clientY;
      this.touchCurrentY = touch.clientY;
      this.touchDraggedElement = listItem;
      this.touchPlaceholderIndex = index;
      
      listItem.classList.add('touch-dragging');
      document.body.classList.add('is-dragging-track');
      
      // Add touch move/end listeners
      document.addEventListener('touchmove', this.onTouchMove, { passive: false });
      document.addEventListener('touchend', this.onTouchEnd);
    },
    
    /**
     * Начать mouse drag - для desktop
     */
    startMouseDrag(event, index) {
      event.preventDefault();
      
      const listItem = event.target.closest('.queue-item');
      if (!listItem) return;
      
      this.isDragHandleActive = true;
      this.isMouseDragging = true;
      this.dragIndex = index;
      this.mouseStartY = event.clientY;
      this.mouseCurrentY = event.clientY;
      this.mouseDraggedElement = listItem;
      this.dragOverIndex = index;
      
      document.body.classList.add('is-dragging-track');
      
      // Add mouse move/up listeners
      document.addEventListener('mousemove', this.onMouseMove);
      document.addEventListener('mouseup', this.onMouseUp);
    },
    
    onMouseMove(event) {
      if (!this.isMouseDragging || !this.mouseDraggedElement) return;
      
      this.mouseCurrentY = event.clientY;
      
      // Используем позицию курсора для определения целевого элемента
      const listItems = Array.from(this.mouseDraggedElement.parentNode.querySelectorAll('.queue-item'));
      
      let newOverIndex = this.dragIndex;
      
      for (let idx = 0; idx < listItems.length; idx++) {
        const item = listItems[idx];
        if (idx === this.dragIndex) continue;
        
        const rect = item.getBoundingClientRect();
        const itemCenter = rect.top + rect.height / 2;
        
        // Курсор выше центра элемента - вставить перед ним
        if (this.mouseCurrentY < itemCenter && idx < this.dragIndex) {
          newOverIndex = idx;
          break;
        }
        // Курсор ниже центра элемента - вставить после него
        if (this.mouseCurrentY > itemCenter && idx > this.dragIndex) {
          newOverIndex = idx;
        }
      }
      
      this.dragOverIndex = newOverIndex;
    },
    
    onMouseUp() {
      if (!this.isMouseDragging) return;
      
      document.removeEventListener('mousemove', this.onMouseMove);
      document.removeEventListener('mouseup', this.onMouseUp);
      
      // Perform the reorder
      if (this.dragOverIndex !== null && this.dragOverIndex !== this.dragIndex) {
        const sourceIndex = this.dragIndex;
        const targetIndex = this.dragOverIndex;
        
        const newTracks = [...this.tracks];
        const [removed] = newTracks.splice(sourceIndex, 1);
        newTracks.splice(targetIndex, 0, removed);
        
        this.$emit('reorder', newTracks, sourceIndex, targetIndex);
      }
      
      this.resetMouseDrag();
    },
    
    resetMouseDrag() {
      this.isMouseDragging = false;
      this.mouseStartY = 0;
      this.mouseCurrentY = 0;
      this.mouseDraggedElement = null;
      this.resetDrag();
    },
    
    /**
     * Получить стиль для элемента списка
     */
    getItemStyle(index) {
      // Swipe style
      if (this.swipeIndex === index) {
        return { transform: `translateX(${this.swipeOffset}px)` };
      }
      
      return {};
    },
    
    onTouchMove(event) {
      if (!this.isTouchDragging || !this.touchDraggedElement) return;
      
      event.preventDefault();
      const touch = event.touches[0];
      this.touchCurrentY = touch.clientY;
      
      // Move the dragged element visually
      const deltaY = this.touchCurrentY - this.touchStartY;
      this.touchDraggedElement.style.transform = `translateY(${deltaY}px)`;
      
      // Determine which item we're over
      const listItems = Array.from(this.touchDraggedElement.parentNode.querySelectorAll('.queue-item'));
      const draggedRect = this.touchDraggedElement.getBoundingClientRect();
      const draggedCenter = draggedRect.top + draggedRect.height / 2;
      
      // Находим элемент, над которым находится перетаскиваемый элемент
      let newPlaceholderIndex = this.dragIndex;
      
      for (let idx = 0; idx < listItems.length; idx++) {
        const item = listItems[idx];
        if (item === this.touchDraggedElement) continue;
        
        const rect = item.getBoundingClientRect();
        const itemCenter = rect.top + rect.height / 2;
        
        // Двигаемся вверх - если центр перетаскиваемого выше центра текущего
        if (idx < this.dragIndex && draggedCenter < itemCenter) {
          newPlaceholderIndex = idx;
          break;
        }
        // Двигаемся вниз - если центр перетаскиваемого ниже центра текущего
        if (idx > this.dragIndex && draggedCenter > itemCenter) {
          newPlaceholderIndex = idx;
        }
      }
      
      this.touchPlaceholderIndex = newPlaceholderIndex;
      this.dragOverIndex = newPlaceholderIndex;
    },
    
    onTouchEnd() {
      if (!this.isTouchDragging) return;
      
      document.removeEventListener('touchmove', this.onTouchMove);
      document.removeEventListener('touchend', this.onTouchEnd);
      
      if (this.touchDraggedElement) {
        this.touchDraggedElement.style.transform = '';
        this.touchDraggedElement.classList.remove('touch-dragging');
      }
      
      // Perform the reorder
      if (this.touchPlaceholderIndex !== null && this.touchPlaceholderIndex !== this.dragIndex) {
        const sourceIndex = this.dragIndex;
        const targetIndex = this.touchPlaceholderIndex;
        
        const newTracks = [...this.tracks];
        const [removed] = newTracks.splice(sourceIndex, 1);
        newTracks.splice(targetIndex, 0, removed);
        
        this.$emit('reorder', newTracks, sourceIndex, targetIndex);
      }
      
      this.resetTouchDrag();
    },
    
    resetTouchDrag() {
      this.isTouchDragging = false;
      this.touchStartY = 0;
      this.touchCurrentY = 0;
      this.touchDraggedElement = null;
      this.touchPlaceholderIndex = null;
      this.resetDrag();
    },
    
    resetDrag() {
      this.dragIndex = null;
      this.dragOverIndex = null;
      this.isDragHandleActive = false;
      document.body.classList.remove('is-dragging-track');
    },
    
    onTrackClick(index) {
      // Не переключать если это drag операция или swipe
      if (this.isDragHandleActive || this.dragIndex !== null || this.isTouchDragging || this.isSwipeActive || this.isMouseDragging) return;
      // Переключить на этот трек (или play/pause если текущий)
      this.$emit('play-track', index);
    },
    
    // ========== Swipe to delete (mobile) ==========
    onSwipeStart(event, index) {
      // Не начинать swipe если это drag операция
      if (this.isTouchDragging) return;
      
      const touch = event.touches[0];
      this.swipeStartX = touch.clientX;
      this.swipeIndex = index;
      this.swipeOffset = 0;
      this.isSwipeActive = false;
    },
    
    onSwipeMove(event) {
      if (this.swipeIndex === null || this.isTouchDragging) return;
      
      const touch = event.touches[0];
      const deltaX = touch.clientX - this.swipeStartX;
      
      // Только свайп влево для удаления
      if (deltaX < -10) {
        this.isSwipeActive = true;
        this.swipeOffset = Math.max(deltaX, -100);
      } else if (deltaX > 10) {
        // Если свайп вправо - возвращаем на место
        this.swipeOffset = Math.min(deltaX * 0.3, 20);
      }
    },
    
    onSwipeEnd(event, index) {
      if (this.swipeIndex === null) return;
      
      // Если свайп больше порога - удаляем
      if (this.swipeOffset < -60) {
        this.deleteTrack(index);
      }
      
      // Сброс состояния
      this.swipeIndex = null;
      this.swipeOffset = 0;
      setTimeout(() => {
        this.isSwipeActive = false;
      }, 100);
    },
    
    // ========== Delete track ==========
    deleteTrack(index) {
      this.$emit('delete-track', index);
    }
  },
  
  beforeUnmount() {
    document.removeEventListener('touchmove', this.onTouchMove);
    document.removeEventListener('touchend', this.onTouchEnd);
    document.body.classList.remove('is-dragging-track');
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

/* Loading skeleton */
.queue-loading {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.skeleton-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  background: rgba(208, 188, 255, 0.05);
  border-radius: 10px;
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

.skeleton-item:nth-child(2) { animation-delay: 0.1s; }
.skeleton-item:nth-child(3) { animation-delay: 0.2s; }
.skeleton-item:nth-child(4) { animation-delay: 0.3s; }
.skeleton-item:nth-child(5) { animation-delay: 0.4s; }

@keyframes skeleton-pulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

.skeleton-handle {
  width: 14px;
  height: 24px;
  background: rgba(208, 188, 255, 0.1);
  border-radius: 4px;
}

.skeleton-cover {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, rgba(99, 58, 137, 0.3) 0%, rgba(208, 188, 255, 0.2) 100%);
  border-radius: 6px;
}

.skeleton-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.skeleton-title {
  height: 14px;
  width: 70%;
  background: rgba(208, 188, 255, 0.15);
  border-radius: 4px;
}

.skeleton-artist {
  height: 10px;
  width: 50%;
  background: rgba(208, 188, 255, 0.1);
  border-radius: 4px;
}

.skeleton-duration {
  width: 32px;
  height: 12px;
  background: rgba(208, 188, 255, 0.1);
  border-radius: 4px;
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
  position: relative;
}

/* TransitionGroup animations */
.track-list-enter-active,
.track-list-leave-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.track-list-leave-active {
  position: absolute;
  width: calc(100% - 12px);
}

.track-list-enter-from {
  opacity: 0;
  transform: scale(0.8) translateY(-10px);
}

.track-list-leave-to {
  opacity: 0;
  transform: scale(0.8) translateX(50px);
}

/* Анимация перемещения элементов */
.track-list-move {
  transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Предотвращаем анимацию move во время leave */
.track-list-leave-active ~ .queue-item {
  transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.queue-item {
  display: flex;
  align-items: center;
  padding: 8px 10px;
  background: rgba(208, 188, 255, 0.05);
  border-radius: 10px;
  transition: background 0.15s ease;
  gap: 10px;
  cursor: pointer;
  position: relative;
  -webkit-tap-highlight-color: transparent;
  user-select: none;
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
  cursor: grabbing;
  background: rgba(99, 58, 137, 0.4);
  z-index: 1000;
  position: relative;
}

/* Touch dragging state */
.queue-item.touch-dragging {
  z-index: 1000;
  background: rgba(99, 58, 137, 0.4);
  cursor: grabbing;
  pointer-events: none;
}

/* Визуальный индикатор места вставки - линия */
.queue-item.drag-over-above::before {
  content: '';
  position: absolute;
  top: -4px;
  left: 8px;
  right: 8px;
  height: 3px;
  background: linear-gradient(90deg, #00d9e7, #9333ea);
  border-radius: 2px;
}

.queue-item.drag-over-below::after {
  content: '';
  position: absolute;
  bottom: -4px;
  left: 8px;
  right: 8px;
  height: 3px;
  background: linear-gradient(90deg, #00d9e7, #9333ea);
  border-radius: 2px;
}

.drag-handle {
  color: rgba(255, 255, 255, 0.3);
  cursor: grab;
  flex-shrink: 0;
  padding: 8px 6px;
  border-radius: 6px;
}

.drag-handle:hover {
  color: rgba(255, 255, 255, 0.6);
}

.drag-handle:active {
  cursor: grabbing;
  color: white;
}

.track-cover {
  width: 40px;
  height: 40px;
  border-radius: 6px;
  overflow: hidden;
  flex-shrink: 0;
  position: relative;
  background: rgba(208, 188, 255, 0.1);
  transition: opacity 0.15s ease;
  will-change: opacity;
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

/* Пауза анимации когда плеер на паузе */
.playing-indicator.paused .bar {
  animation-play-state: paused;
}

.track-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  gap: 2px;
  transition: opacity 0.15s ease;
  will-change: opacity;
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

/* Track actions (duration + delete) */
.track-actions {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
  margin-left: auto;
  transition: opacity 0.15s ease;
  will-change: opacity;
}

.delete-btn {
  display: none;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  color: rgba(255, 100, 100, 0.5);
  padding: 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  opacity: 0;
  transform: scale(0.8);
}

.queue-item:hover .delete-btn {
  display: flex;
  opacity: 1;
  transform: scale(1);
}

.delete-btn:hover {
  color: #ff5555;
  background: rgba(255, 85, 85, 0.15);
  transform: scale(1.1);
}

.delete-btn:active {
  transform: scale(0.95);
}

/* Swipe delete background */
.delete-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, rgba(220, 38, 38, 0.95) 0%, rgba(185, 28, 28, 1) 100%);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: white;
  font-weight: 600;
  font-size: 15px;
  letter-spacing: 0.5px;
  opacity: 0;
  transform: scale(0.98);
  transition: opacity 0.15s ease, transform 0.15s ease;
  z-index: 5;
  pointer-events: none;
}

.delete-bg.active {
  opacity: 1;
  transform: scale(1);
}

.delete-bg svg {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
}

/* Swiping state */
.queue-item.swiping {
  transition: none;
  z-index: 10;
}

/* Hide track content when swiping */
.queue-item.swiping .track-cover,
.queue-item.swiping .track-info,
.queue-item.swiping .track-actions,
.queue-item.swiping .drag-handle {
  transition: opacity 0.15s ease;
}

/* When ready to delete - fully hide track content, show only red background */
.queue-item.swipe-delete-ready {
  background: transparent !important;
}

.queue-item.swipe-delete-ready .track-cover,
.queue-item.swipe-delete-ready .track-info,
.queue-item.swipe-delete-ready .track-actions,
.queue-item.swipe-delete-ready .drag-handle {
  opacity: 0;
  pointer-events: none;
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

@media (max-width: 768px) {
  .queue-scroll-wrapper {
    padding: 10px;
  }
  
  .queue-item {
    padding: 8px;
    gap: 8px;
    overflow: visible;
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
    display: flex;
    padding: 10px;
    margin: -6px;
  }
  
  .skeleton-cover {
    width: 36px;
    height: 36px;
  }
  
  /* Hide desktop delete button on mobile */
  .delete-btn {
    display: none !important;
  }
  
  /* Mobile swipe delete background */
  .delete-bg {
    display: flex;
  }
}

/* Hide delete background on desktop */
@media (min-width: 769px) {
  .delete-bg {
    display: none;
  }
}
</style>

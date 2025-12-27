<template>
  <div class="volume-control">
    <button class="volume-btn" @click="toggleMute">
      <svg v-if="displayVolume === 0" width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
        <path d="M16.5 12c0-1.77-1.02-3.29-2.5-4.03v2.21l2.45 2.45c.03-.2.05-.41.05-.63zm2.5 0c0 .94-.2 1.82-.54 2.64l1.51 1.51C20.63 14.91 21 13.5 21 12c0-4.28-2.99-7.86-7-8.77v2.06c2.89.86 5 3.54 5 6.71zM4.27 3L3 4.27 7.73 9H3v6h4l5 5v-6.73l4.25 4.25c-.67.52-1.42.93-2.25 1.18v2.06c1.38-.31 2.63-.95 3.69-1.81L19.73 21 21 19.73l-9-9L4.27 3zM12 4L9.91 6.09 12 8.18V4z"/>
      </svg>
      <svg v-else-if="displayVolume < 0.5" width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
        <path d="M18.5 12c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM5 9v6h4l5 5V4L9 9H5z"/>
      </svg>
      <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
        <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/>
      </svg>
    </button>
    <div 
      class="slider-wrapper"
      ref="sliderWrapper"
      @mousedown="startDrag"
      @touchstart.prevent="startDrag"
    >
      <div class="slider-track">
        <div class="slider-fill" :style="{ width: displayPercent + '%' }"></div>
      </div>
      <div class="slider-thumb" :style="{ left: displayPercent + '%' }"></div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Volume',
  props: {
    volume: {
      type: Number,
      required: true,
    },
  },
  data() {
    return {
      previousVolume: 0.5,
      isDragging: false,
      dragPercent: 0
    };
  },
  computed: {
    volumePercent() {
      return Math.min(100, Math.max(0, this.volume * 100));
    },
    displayPercent() {
      return this.isDragging ? this.dragPercent : this.volumePercent;
    },
    displayVolume() {
      return this.isDragging ? this.dragPercent / 100 : this.volume;
    }
  },
  methods: {
    toggleMute() {
      if (this.volume > 0) {
        this.previousVolume = this.volume;
        this.$emit('update:volume', 0);
      } else {
        this.$emit('update:volume', this.previousVolume);
      }
    },
    
    getPercentFromEvent(e) {
      const wrapper = this.$refs.sliderWrapper;
      if (!wrapper) return 0;
      
      const rect = wrapper.getBoundingClientRect();
      const clientX = e.touches ? e.touches[0].clientX : e.clientX;
      const x = Math.max(0, Math.min(clientX - rect.left, rect.width));
      return (x / rect.width) * 100;
    },
    
    startDrag(e) {
      e.preventDefault();
      this.isDragging = true;
      this.dragPercent = this.getPercentFromEvent(e);
      
      // Сразу применяем
      this.$emit('update:volume', this.dragPercent / 100);
      
      document.addEventListener('mousemove', this.handleDrag);
      document.addEventListener('mouseup', this.stopDrag);
      document.addEventListener('touchmove', this.handleDrag);
      document.addEventListener('touchend', this.stopDrag);
    },
    
    handleDrag(e) {
      if (!this.isDragging) return;
      
      // Use requestAnimationFrame for smooth, lag-free updates
      requestAnimationFrame(() => {
        if (!this.isDragging) return;
        this.dragPercent = this.getPercentFromEvent(e);
        this.$emit('update:volume', this.dragPercent / 100);
      });
    },
    
    stopDrag() {
      if (!this.isDragging) return;
      
      this.isDragging = false;
      document.removeEventListener('mousemove', this.handleDrag);
      document.removeEventListener('mouseup', this.stopDrag);
      document.removeEventListener('touchmove', this.handleDrag);
      document.removeEventListener('touchend', this.stopDrag);
    }
  },
  beforeUnmount() {
    this.stopDrag();
  }
};
</script>

<style scoped>
.volume-control {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  max-width: 180px;
}

.volume-btn {
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s;
  flex-shrink: 0;
}

.volume-btn:hover {
  color: white;
}

.slider-wrapper {
  flex: 1;
  position: relative;
  height: 20px;
  display: flex;
  align-items: center;
  cursor: pointer;
  touch-action: none;
}

.slider-track {
  position: absolute;
  width: 100%;
  height: 4px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 2px;
  overflow: hidden;
}

.slider-fill {
  height: 100%;
  background: linear-gradient(90deg, #00d9e7 0%, #9333ea 100%);
  border-radius: 2px;
  /* No transition for immediate response to drag */
}

.slider-thumb {
  position: absolute;
  width: 12px;
  height: 12px;
  background: white;
  border-radius: 50%;
  transform: translateX(-50%);
  cursor: pointer;
  box-shadow: 0 0 6px rgba(0, 0, 0, 0.3);
  transition: transform 0.1s ease;
}

.slider-thumb:hover {
  transform: translateX(-50%) scale(1.2);
}

/* Скрыть на мобильных */
@media (max-width: 768px) {
  .volume-control {
    display: none;
  }
}

/* Показывать только на устройствах с hover (десктоп) */
@media (hover: none) and (pointer: coarse) {
  .volume-control {
    display: none;
  }
}
</style>

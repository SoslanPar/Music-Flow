<template>
  <div class="progress-wrapper">
    <div class="time-display current">{{ formatTime(currentTime) }}</div>
    
    <div 
      class="progress-container" 
      ref="progressContainer"
      @mousedown="startDrag"
      @touchstart="startDrag"
    >
      <div class="progress-track">
        <div class="progress-fill" :style="{ width: displayPercent + '%' }"></div>
      </div>
      <div
        class="progress-thumb"
        :style="{ left: displayPercent + '%' }"
      ></div>
    </div>
    
    <div class="time-display duration">{{ formatTime(duration) }}</div>
  </div>
</template>


<script>
export default {
  props: {
    currentTime: {
      type: Number,
      required: true,
    },
    duration: {
      type: Number,
      required: true,
    },
  },
  data() {
    return {
      isDragging: false,
      dragPercent: 0,
    };
  },
  computed: {
    progressPercent() {
      if (!this.duration || this.duration === 0) return 0;
      return Math.min(100, Math.max(0, (this.currentTime / this.duration) * 100));
    },
    displayPercent() {
      return this.isDragging ? this.dragPercent : this.progressPercent;
    }
  },
  methods: {
    formatTime(seconds) {
      if (!seconds || !isFinite(seconds)) return '0:00';
      const minutes = Math.floor(seconds / 60);
      const remainingSeconds = Math.floor(seconds % 60);
      return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
    },
    
    getPercentFromEvent(e) {
      const container = this.$refs.progressContainer;
      if (!container) return 0;
      
      const rect = container.getBoundingClientRect();
      const clientX = e.touches ? e.touches[0].clientX : e.clientX;
      const x = Math.max(0, Math.min(clientX - rect.left, rect.width));
      return (x / rect.width) * 100;
    },
    
    startDrag(e) {
      if (!isFinite(this.duration) || this.duration === 0) return;
      
      e.preventDefault();
      this.isDragging = true;
      this.dragPercent = this.getPercentFromEvent(e);
      
      // Сразу применяем позицию
      const newTime = (this.dragPercent / 100) * this.duration;
      this.$emit('seek', newTime);
      
      document.addEventListener('mousemove', this.handleDrag);
      document.addEventListener('mouseup', this.stopDrag);
      document.addEventListener('touchmove', this.handleDrag);
      document.addEventListener('touchend', this.stopDrag);
    },
    
    handleDrag(e) {
      if (!this.isDragging) return;
      
      this.dragPercent = this.getPercentFromEvent(e);
      const newTime = (this.dragPercent / 100) * this.duration;
      this.$emit('seek', newTime);
    },
    
    stopDrag() {
      if (!this.isDragging) return;
      
      this.isDragging = false;
      document.removeEventListener('mousemove', this.handleDrag);
      document.removeEventListener('mouseup', this.stopDrag);
      document.removeEventListener('touchmove', this.handleDrag);
      document.removeEventListener('touchend', this.stopDrag);
    },
  },
  beforeUnmount() {
    this.stopDrag();
  }
};
</script>


<style scoped>
.progress-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 8px 0;
}

.time-display {
  font-size: 12px;
  font-variant-numeric: tabular-nums;
  min-width: 36px;
  user-select: none;
}

.time-display.current {
  color: #00d9e7;
  text-align: left;
  text-shadow: 0 0 8px rgba(0, 217, 231, 0.6), 0 0 16px rgba(0, 217, 231, 0.3);
}

.time-display.duration {
  color: #9333ea;
  text-align: right;
  text-shadow: 0 0 8px rgba(147, 51, 234, 0.6), 0 0 16px rgba(147, 51, 234, 0.3);
}

.progress-container {
  flex: 1;
  position: relative;
  height: 24px;
  display: flex;
  align-items: center;
  cursor: pointer;
  touch-action: none;
}

.progress-track {
  width: 100%;
  height: 4px;
  background: rgba(147, 51, 234, 0.3);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #00d9e7 0%, #9333ea 100%);
  border-radius: 2px;
}

.progress-thumb {
  position: absolute;
  top: 50%;
  width: 14px;
  height: 14px;
  background: #D0BCFF;
  border-radius: 50%;
  transform: translate(-50%, -50%);
  cursor: grab;
  box-shadow: 0 0 8px rgba(208, 188, 255, 0.5);
  transition: transform 0.1s ease;
}

.progress-thumb:hover {
  transform: translate(-50%, -50%) scale(1.2);
}

.progress-thumb:active {
  cursor: grabbing;
  transform: translate(-50%, -50%) scale(1.1);
}

@media (max-width: 480px) {
  .progress-wrapper {
    gap: 8px;
  }
  
  .time-display {
    font-size: 11px;
    min-width: 30px;
  }
  
  .progress-thumb {
    width: 16px;
    height: 16px;
  }
}
</style>

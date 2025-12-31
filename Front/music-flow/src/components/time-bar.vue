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


<script setup>
import { ref, computed } from 'vue';
import { formatTime, useProgressDrag } from '@/composables/usePlayer';

const props = defineProps({
  currentTime: { type: Number, required: true },
  duration: { type: Number, required: true },
});

const emit = defineEmits(['seek']);
const progressContainer = ref(null);

const { isDragging, dragPercent, startDrag } = useProgressDrag(
  progressContainer,
  (percent) => {
    if (!isFinite(props.duration) || props.duration === 0) return;
    const newTime = (percent / 100) * props.duration;
    emit('seek', newTime);
  },
  true // with touch support
);

const progressPercent = computed(() => {
  if (!props.duration || props.duration === 0) return 0;
  return Math.min(100, Math.max(0, (props.currentTime / props.duration) * 100));
});

const displayPercent = computed(() => isDragging.value ? dragPercent.value : progressPercent.value);
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
  font-weight: 600;
}

.time-display.current {
  color: #00ffff;
  text-align: left;
  text-shadow: 
    0 0 5px rgba(0, 255, 255, 0.8),
    0 0 10px rgba(0, 255, 255, 0.6),
    0 0 20px rgba(0, 255, 255, 0.4),
    0 0 30px rgba(0, 255, 255, 0.2);
}

.time-display.duration {
  color: #bf5af2;
  text-align: right;
  text-shadow: 
    0 0 5px rgba(191, 90, 242, 0.8),
    0 0 10px rgba(191, 90, 242, 0.6),
    0 0 20px rgba(191, 90, 242, 0.4),
    0 0 30px rgba(191, 90, 242, 0.2);
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
  background: rgba(99, 58, 137, 0.3);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #00d9e7 0%, #633A89 100%);
  border-radius: 2px;
  transition: none;
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
  opacity: 1;
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
    width: 18px;
    height: 18px;
    opacity: 1;
  }
}
</style>

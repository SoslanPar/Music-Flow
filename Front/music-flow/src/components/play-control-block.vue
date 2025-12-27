<script setup>
import { computed } from 'vue';
import play_button_pause from '@/assets/play_button_pause.vue';
import play_button_active from '@/assets/play_button_active.vue';
import play_past_button from '@/assets/play_past_button.vue';
import play_next_button from '@/assets/play_next_button.vue';

const props = defineProps({
  isPlaying: Boolean
});

const emit = defineEmits(['play', 'pause', 'prev', 'next']);

const togglePlayPause = () => {
  if (props.isPlaying) {
    emit('pause');
  } else {
    emit('play');
  }
};
</script>

<template>
  <div class="control-block" :class="{ 'play-active': isPlaying }">
    <button class="control-btn prev-btn" @click="emit('prev')">
      <play_past_button />
    </button>

    <button class="control-btn play-btn" @click="togglePlayPause">
      <component 
        :is="isPlaying ? play_button_active : play_button_pause" 
        class="play-icon" 
      />
    </button>

    <button class="control-btn next-btn" @click="emit('next')">
      <play_next_button />
    </button>
  </div>
</template>

<style scoped>
.control-block {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 8px 0;
}

.control-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.control-btn:active {
  transform: scale(0.95);
}

.prev-btn,
.next-btn {
  width: 36px;
  height: 36px;
  opacity: 0.8;
}

.prev-btn:hover,
.next-btn:hover {
  opacity: 1;
  transform: scale(1.1);
}

.play-btn {
  width: 64px;
  height: 64px;
}

.play-btn:hover {
  transform: scale(1.05);
}

.play-icon {
  width: 64px;
  height: 64px;
}

/* Анимация при воспроизведении */
.play-active .prev-btn,
.play-active .next-btn {
  opacity: 1;
}

.play-active .play-btn {
  transform: scale(1.05);
}

@media (max-width: 480px) {
  .control-block {
    gap: 12px;
  }
  
  .prev-btn,
  .next-btn {
    width: 28px;
    height: 28px;
  }
  
  .play-btn {
    width: 52px;
    height: 52px;
  }
  
  .play-icon {
    width: 52px;
    height: 52px;
  }
}
</style>
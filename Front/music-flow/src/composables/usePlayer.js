/**
 * Composables для плеера - общая логика для всех плееров
 */
import { ref, onBeforeUnmount } from 'vue';

/**
 * Форматирование времени в mm:ss
 * @param {number} seconds - время в секундах
 * @returns {string} - отформатированное время
 */
export function formatTime(seconds) {
  if (!seconds || !isFinite(seconds)) return '0:00';
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.floor(seconds % 60);
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
}

/**
 * Hook для управления перетаскиванием прогресс-бара
 * @param {Ref<HTMLElement>} containerRef - ref элемента контейнера
 * @param {Function} onSeek - callback с процентом (0-100)
 * @param {boolean} withTouch - поддержка touch событий
 */
export function useProgressDrag(containerRef, onSeek, withTouch = false) {
  const isDragging = ref(false);
  const dragPercent = ref(0);
  
  // Сохраняем ссылки на обработчики для cleanup
  let handleDrag = null;
  let stopDrag = null;

  const getPercentFromEvent = (e) => {
    const container = containerRef.value;
    if (!container) return 0;
    const rect = container.getBoundingClientRect();
    const clientX = e.touches ? e.touches[0].clientX : e.clientX;
    const x = Math.max(0, Math.min(clientX - rect.left, rect.width));
    return (x / rect.width) * 100;
  };

  const startDrag = (e) => {
    e.preventDefault();
    isDragging.value = true;
    dragPercent.value = getPercentFromEvent(e);
    onSeek(dragPercent.value);
    
    handleDrag = (e) => {
      if (!isDragging.value) return;
      requestAnimationFrame(() => {
        if (!isDragging.value) return;
        dragPercent.value = getPercentFromEvent(e);
        onSeek(dragPercent.value);
      });
    };
    
    stopDrag = () => {
      isDragging.value = false;
      cleanup();
    };
    
    document.addEventListener('mousemove', handleDrag);
    document.addEventListener('mouseup', stopDrag);
    if (withTouch) {
      document.addEventListener('touchmove', handleDrag);
      document.addEventListener('touchend', stopDrag);
    }
  };
  
  const cleanup = () => {
    if (handleDrag) {
      document.removeEventListener('mousemove', handleDrag);
      document.removeEventListener('mouseup', stopDrag);
      if (withTouch) {
        document.removeEventListener('touchmove', handleDrag);
        document.removeEventListener('touchend', stopDrag);
      }
    }
  };

  onBeforeUnmount(cleanup);

  return {
    isDragging,
    dragPercent,
    startDrag,
    cleanup,
  };
}

/**
 * Hook для управления громкостью
 * @param {Ref<HTMLElement>} containerRef - ref элемента слайдера
 * @param {Function} onVolumeChange - callback с громкостью (0-1)
 */
export function useVolumeDrag(containerRef, onVolumeChange) {
  const isDragging = ref(false);
  const dragValue = ref(0);
  const previousVolume = ref(0.5);
  
  let handleDrag = null;
  let stopDrag = null;

  const getValueFromEvent = (e) => {
    const container = containerRef.value;
    if (!container) return 0;
    const rect = container.getBoundingClientRect();
    const clientX = e.touches ? e.touches[0].clientX : e.clientX;
    const x = Math.max(0, Math.min(clientX - rect.left, rect.width));
    return x / rect.width;
  };

  const startDrag = (e) => {
    e.preventDefault();
    isDragging.value = true;
    dragValue.value = getValueFromEvent(e);
    onVolumeChange(dragValue.value);
    
    handleDrag = (e) => {
      if (!isDragging.value) return;
      requestAnimationFrame(() => {
        if (!isDragging.value) return;
        dragValue.value = getValueFromEvent(e);
        onVolumeChange(dragValue.value);
      });
    };
    
    stopDrag = () => {
      isDragging.value = false;
      cleanup();
    };
    
    document.addEventListener('mousemove', handleDrag);
    document.addEventListener('mouseup', stopDrag);
  };
  
  const cleanup = () => {
    if (handleDrag) {
      document.removeEventListener('mousemove', handleDrag);
      document.removeEventListener('mouseup', stopDrag);
    }
  };

  const toggleMute = (currentVolume) => {
    if (currentVolume > 0) {
      previousVolume.value = currentVolume;
      onVolumeChange(0);
    } else {
      onVolumeChange(previousVolume.value);
    }
  };

  onBeforeUnmount(cleanup);

  return {
    isDragging,
    dragValue,
    previousVolume,
    startDrag,
    toggleMute,
    cleanup,
  };
}

/**
 * Получить обложку высокого разрешения
 * @param {string} coverUrl - URL обложки
 * @param {string} size - желаемый размер (default: '400x400')
 * @returns {string} - URL высокого разрешения
 */
export function getHighResCover(coverUrl, size = '400x400') {
  if (!coverUrl) return '';
  // Yandex Music cover URLs содержат размер, например: 100x100, 200x200
  return coverUrl.replace(/\d+x\d+/, size);
}

/**
 * Проверка длины названия для marquee эффекта
 * @param {string} title - название трека
 * @param {number} maxLength - максимальная длина (default: 25)
 * @returns {boolean}
 */
export function isLongTitle(title, maxLength = 25) {
  return title && title.length > maxLength;
}

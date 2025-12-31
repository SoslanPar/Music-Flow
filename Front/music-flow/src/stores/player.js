/**
 * Pinia Store для состояния плеера
 * Централизованное управление состоянием воспроизведения
 */
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const usePlayerStore = defineStore('player', () => {
  // State
  const currentTrack = ref(null);
  const tracks = ref([]);
  const currentTrackIndex = ref(0);
  const currentTime = ref(0);
  const duration = ref(0);
  const volume = ref(1);
  const isPlaying = ref(false);
  const isLoading = ref(false);
  const isMuted = ref(false);

  // Getters
  const currentTrackTitle = computed(() => currentTrack.value?.title || 'Выберите трек');
  const currentTrackArtist = computed(() => currentTrack.value?.artist || '');
  const currentTrackCover = computed(() => currentTrack.value?.cover || '');
  
  const progressPercent = computed(() => {
    if (!duration.value) return 0;
    return (currentTime.value / duration.value) * 100;
  });

  const volumePercent = computed(() => {
    return isMuted.value ? 0 : volume.value * 100;
  });

  const hasNextTrack = computed(() => {
    return currentTrackIndex.value < tracks.value.length - 1;
  });

  const hasPrevTrack = computed(() => {
    return currentTrackIndex.value > 0 || currentTime.value > 5;
  });

  // Actions
  function setTrack(track) {
    currentTrack.value = track;
  }

  function setTracks(newTracks, index = 0) {
    tracks.value = newTracks;
    currentTrackIndex.value = index;
    if (newTracks[index]) {
      currentTrack.value = newTracks[index];
    }
  }

  function setCurrentTime(time) {
    currentTime.value = time;
  }

  function setDuration(dur) {
    duration.value = dur;
  }

  function setVolume(vol) {
    volume.value = vol;
    if (vol > 0) {
      isMuted.value = false;
    }
  }

  function toggleMute() {
    isMuted.value = !isMuted.value;
  }

  function setPlaying(playing) {
    isPlaying.value = playing;
  }

  function setLoading(loading) {
    isLoading.value = loading;
  }

  function nextTrack() {
    if (hasNextTrack.value) {
      currentTrackIndex.value++;
      currentTrack.value = tracks.value[currentTrackIndex.value];
      currentTime.value = 0;
    }
  }

  function prevTrack() {
    // Если играет > 5 секунд - возврат в начало
    if (currentTime.value > 5) {
      currentTime.value = 0;
    } else if (hasPrevTrack.value && currentTrackIndex.value > 0) {
      currentTrackIndex.value--;
      currentTrack.value = tracks.value[currentTrackIndex.value];
      currentTime.value = 0;
    }
  }

  function setTrackIndex(index) {
    if (index >= 0 && index < tracks.value.length) {
      currentTrackIndex.value = index;
      currentTrack.value = tracks.value[index];
      currentTime.value = 0;
    }
  }

  function updatePlayerState(state) {
    if (state.currentTime !== undefined) currentTime.value = state.currentTime;
    if (state.duration !== undefined) duration.value = state.duration;
    if (state.isPlaying !== undefined) isPlaying.value = state.isPlaying;
    if (state.isLoading !== undefined) isLoading.value = state.isLoading;
  }

  function reset() {
    currentTrack.value = null;
    tracks.value = [];
    currentTrackIndex.value = 0;
    currentTime.value = 0;
    duration.value = 0;
    isPlaying.value = false;
    isLoading.value = false;
  }

  return {
    // State
    currentTrack,
    tracks,
    currentTrackIndex,
    currentTime,
    duration,
    volume,
    isPlaying,
    isLoading,
    isMuted,
    
    // Getters
    currentTrackTitle,
    currentTrackArtist,
    currentTrackCover,
    progressPercent,
    volumePercent,
    hasNextTrack,
    hasPrevTrack,
    
    // Actions
    setTrack,
    setTracks,
    setCurrentTime,
    setDuration,
    setVolume,
    toggleMute,
    setPlaying,
    setLoading,
    nextTrack,
    prevTrack,
    setTrackIndex,
    updatePlayerState,
    reset,
  };
});

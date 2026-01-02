<script setup>
  // Блокировка щипка (pinch-to-zoom)
document.addEventListener('gesturestart', function(e) {
  e.preventDefault();
}, { passive: false });

// Блокировка масштабирования через тач (на случай, если gesturestart не сработал)
document.addEventListener('touchstart', function(e) {
  if (e.touches.length > 1) {
    e.preventDefault();
  }
}, { passive: false });
</script>

<template>
  <div class="app-background">
    <router-view />
  </div>
</template>


<style>


  html, body {
  overscroll-behavior-y: none;   
  overscroll-behavior-x: none;
  touch-action: manipulation;
}


</style>